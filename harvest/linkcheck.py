"""Check every harvested URL and record what actually happened.

Most of these point at licensed vendors that reject unauthenticated bots, so a
403 or 401 is a healthy resource, not a dead one. Only DNS failures, 404 and 410
mean the link is genuinely broken. Proxy URLs are checked at their inner target,
because the proxy itself answers 200 for anything.
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

from common import CONTENT, UA, write

TODAY = datetime.date.today().isoformat()
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
BROKEN = {404, 410}


def target(url: str) -> str:
    """Follow the proxy wrapper to the resource it actually points at."""
    m = re.search(r"[?&]url=(.+)$", url)
    return urllib.parse.unquote(m.group(1)) if m else url


def probe(u: str, method: str):
    req = urllib.request.Request(u, headers=UA, method=method)
    return urllib.request.urlopen(req, timeout=25, context=CTX)


def check(url: str):
    u = target(url)
    if not u.startswith("http"):
        return url, "skip", 0
    try:
        r = probe(u, "HEAD")
        return url, "ok", r.status
    except urllib.error.HTTPError as e:
        # West Academic and several vendors answer 404/405 to HEAD but 200 to
        # GET, so never call a link broken on a HEAD result alone.
        if e.code in BROKEN | {405}:
            try:
                r = probe(u, "GET")
                return url, "ok", r.status
            except urllib.error.HTTPError as e2:
                if e2.code in (403, 401, 429):
                    return url, "gated", e2.code
                if e2.code in BROKEN:
                    return url, "broken", e2.code
                return url, "other", e2.code
            except Exception:
                return url, "unreachable", 0
        if e.code in (403, 401, 405, 429):
            # Vendor blocks bots or dislikes HEAD; presence is what we wanted.
            return url, "gated", e.code
        if e.code in BROKEN:
            return url, "broken", e.code
        return url, "other", e.code
    except Exception as e:
        name = type(e).__name__
        if "NameResolution" in str(e) or "gaierror" in name:
            return url, "broken", 0
        return url, "unreachable", 0


def collect():
    urls = set()
    def add(u):
        if u and isinstance(u, str) and u.startswith("http"):
            urls.add(u)
    for f in ("studyaids.json", "treatises.json"):
        for s in json.load(open(os.path.join(CONTENT, f), encoding="utf-8"))["subjects"]:
            add(s["source"])
            for i in s["items"]:
                add(i["url"])
    for d in json.load(open(os.path.join(CONTENT, "databases.json"), encoding="utf-8"))["items"]:
        add(d["url"])
    sv = json.load(open(os.path.join(CONTENT, "services.json"), encoding="utf-8"))
    for i in sv["items"]:
        add(i.get("url")); add(i.get("extra_url"))
    for c in json.load(open(os.path.join(CONTENT, "concentrations.json"), encoding="utf-8"))["items"]:
        add(c["requirements_url"]); add(c["courses_url"])
    return sorted(urls)


def main():
    urls = collect()
    print("  checking %d unique URLs ..." % len(urls))
    res = {}
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for u, state, code in ex.map(check, urls):
            res[u] = {"state": state, "code": code}
    tally = {}
    for v in res.values():
        tally[v["state"]] = tally.get(v["state"], 0) + 1
    for k in sorted(tally, key=lambda x: -tally[x]):
        print("    %-12s %4d" % (k, tally[k]))
    broken = sorted(u for u, v in res.items() if v["state"] == "broken")
    print("  BROKEN: %d" % len(broken))
    for b in broken[:25]:
        print("    %s" % b[:120])
    write("linkcheck.json", {"verified": TODAY, "tally": tally,
                              "broken": broken, "results": res})


if __name__ == "__main__":
    main()

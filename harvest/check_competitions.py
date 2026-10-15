"""Weekly check of the /compete/ catalogue against the organizers' own pages.

For each entry it fetches the organizer's page and flags, for a person to act on:
  - dead links (404/410, DNS failures). A 403 means the site blocks scripts, not that the
    page is gone, so those are listed separately as "can't check from here".
  - pages whose text changed since last week (new dates usually show up this way), quoting
    any date on the page that falls in the next cycle, so the reader knows where to look

It never edits content/competitions.json. A new date goes in only after someone reads it
on the organizer's page. Writes cache/competitions-check.md; exits 1 when there is
something to read, 0 when the week was quiet. refresh_watch.sh runs it on Mondays.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE = os.path.join(SITE, "content", "competitions.json")
STATE = os.path.join(SITE, "cache", "competitions-check.json")
REPORT = os.path.join(SITE, "cache", "competitions-check.md")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128 Safari/537.36"}


def fetch(url: str) -> tuple[str, str]:
    """(status, visible text). status is 'ok', 'blocked', or 'dead: <why>'."""
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
    except urllib.error.HTTPError as ex:
        return ("blocked" if ex.code in (401, 403, 429) else f"dead: HTTP {ex.code}"), ""
    except Exception as ex:  # noqa: BLE001 (DNS, TLS, timeouts all mean the same thing here)
        return f"dead: {ex.__class__.__name__}", ""
    text = raw.decode("utf-8", "ignore")
    text = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return "ok", re.sub(r"\s+", " ", text).strip()


def main() -> int:
    items = json.load(open(CATALOGUE))["items"]
    prior = json.load(open(STATE)) if os.path.exists(STATE) else {}
    today = dt.date.today()
    next_year = str(today.year + 1)
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda c: fetch(c["url"]), items))

    state, dead, blocked, changed = {}, [], [], []
    for c, (status, text) in zip(items, results):
        digest = hashlib.sha256(text.encode()).hexdigest() if text else None
        state[c["url"]] = {"status": status, "hash": digest or prior.get(c["url"], {}).get("hash")}
        if status.startswith("dead"):
            dead.append((c, status))
        elif status == "blocked":
            blocked.append(c)
        elif digest and prior.get(c["url"], {}).get("hash") not in (None, digest):
            hits = [m.group(0).strip() for m in re.finditer(rf"[^.]{{0,80}}\b{next_year}\b[^.]{{0,40}}", text)]
            changed.append((c, hits[:3]))

    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(state, open(STATE, "w"), indent=1)

    lines = [f"# Competitions check, {today:%b} {today.day}, {today.year}", ""]
    def section(title, rows):
        lines.extend([f"## {title} ({len(rows)})", ""] + (rows or ["None."]) + [""])
    section("Dead links: fix or drop", [f"- {c['name']}: {why}. {c['url']}" for c, why in dead])
    section("Page changed since last week: read it, update the entry if a date moved",
            [f"- {c['name']}: {c['url']}" + "".join(f"\n  - “{h}”" for h in hits) for c, hits in changed])
    section("Blocks scripts, check by hand now and then", [f"- {c['name']}: {c['url']}" for c in blocked])
    open(REPORT, "w").write("\n".join(lines))
    print("\n".join(lines))
    return 1 if (dead or changed) else 0


if __name__ == "__main__":
    sys.exit(main())

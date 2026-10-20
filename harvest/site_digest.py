"""Weekly suffolklitsa.org numbers, as Markdown, for the Monday digest email.

Reads Counterscale's rows straight from Cloudflare Analytics Engine with the wrangler login
on sam-dev (the same one the deploys use). What it reports, for the last N days against the
N before:
  - visits and page views, by day and by page
  - where people came from: the referrer's site, or the ?source= name an entry link set
    (suffolklitsa.org/nl, /qr, /li ... see static/_redirects)
  - clicks that left the site, recorded by analytics.js as views of /out/...: SUConnect,
    emails, competition pages, everything else
  - how far down each page people got (/depth/25 to /depth/100) and how long they stayed
    (/time/<bucket>), also from analytics.js, with the page in the referrer field
  - newsletter clicks by section, recorded by functions/nl as views of /nl/<issue>/<slug>,
    listed in the order the links appear in newsletter_links.json (top of the email first)
  - the course planner: views of /planner/, a funnel, and its usage counts, which the planner's
    web/track.js records as views of /planner/ev/<name>[/<detail>] (course-planner repo)
It leaves out bots (crawler user agents, and any browser that loads 15+ pages inside a
minute) and our own test hits. Board members who opened /me/ are never recorded at all.

    python3 harvest/site_digest.py [--days 7]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRANGLER_CFG = os.path.expanduser("~/.config/.wrangler/config/default.toml")
BOT_UA = re.compile(r"bot\b|bot/|crawl|spider|slurp|headless|lighthouse|preview|facebookexternalhit|"
                    r"curl|python|wget|httpclient|go-http|monitor|pingdom|uptime", re.I)
BURST = 15  # page loads inside one minute from one browser: not a person
PLANNER_EV = "/planner/ev/"
EVENTS = ("/out/", "/depth/", "/time/", "/nl/", PLANNER_EV)  # recorded as views, but not pages anyone viewed
ROW_LIMIT = 50000
PLANNER_MIN_ADDS = 5  # a course is named only once this many adds hide who added it
TIME_ORDER = ["0-10s", "10-30s", "30-60s", "1-3m", "3-10m", "10m+"]


def _token() -> str:
    return re.search(r'oauth_token\s*=\s*"([^"]+)"', open(WRANGLER_CFG).read()).group(1)


def _call(url: str, data: bytes | None = None) -> bytes:
    for attempt in (1, 2):
        req = urllib.request.Request(url, data=data, headers={"Authorization": f"Bearer {_token()}"})
        try:
            return urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as ex:
            if ex.code in (401, 403) and attempt == 1:
                # The wrangler login is short-lived; any wrangler command refreshes it.
                subprocess.run(["npx", "--yes", "wrangler@latest", "whoami"], capture_output=True, timeout=180)
                continue
            raise


def rows(days: int) -> list[dict]:
    acct = json.loads(_call("https://api.cloudflare.com/client/v4/accounts"))["result"][0]["id"]
    sql = ("SELECT timestamp, blob1 AS host, blob2 AS ua, blob3 AS path, blob4 AS country, "
           "blob5 AS ref, blob10 AS device, double1 AS new_visitor, _sample_interval AS n "
           "FROM metricsDataset WHERE index1 = 'litsa' "
           f"AND timestamp > NOW() - INTERVAL '{days * 2}' DAY ORDER BY timestamp LIMIT {ROW_LIMIT}")
    out = json.loads(_call(f"https://api.cloudflare.com/client/v4/accounts/{acct}/analytics_engine/sql",
                           sql.encode()))["data"]
    for r in out:
        r["ts"] = dt.datetime.fromisoformat(r["timestamp"]).replace(tzinfo=dt.timezone.utc)
        r["n"] = int(r.get("n") or 1)
    return out


def browser(r: dict) -> tuple:
    """Counterscale keeps no visitor id, so one user agent from one country on one day stands for a browser."""
    return (r.get("ua"), r.get("country"), r["ts"].date())


def drop_bots(data: list[dict]) -> tuple[list[dict], int]:
    bad = {id(r) for r in data if BOT_UA.search(r.get("ua") or "") or (r.get("path") or "").startswith("/__")}
    by_browser = collections.defaultdict(list)
    for r in data:
        by_browser[browser(r)].append(r)
    for hits in by_browser.values():
        # A student using the planner sends many events a minute, so only other rows count toward a burst.
        loads = sorted((r for r in hits if not (r.get("path") or "").startswith(PLANNER_EV)), key=lambda r: r["ts"])
        for i in range(len(loads) - BURST + 1):
            if (loads[i + BURST - 1]["ts"] - loads[i]["ts"]).total_seconds() <= 60:
                bad |= {id(r) for r in hits}
                break
    kept = [r for r in data if id(r) not in bad]
    return kept, sum(r["n"] for r in data if id(r) in bad)


def source(r: dict) -> str:
    ref = (r.get("ref") or "").strip()
    if not ref:
        return "direct, or an app that hides it"
    if "://" not in ref:
        return f"entry link: {ref}"
    host = urlparse(ref).netloc.lower().removeprefix("www.").removeprefix("m.").removeprefix("l.")
    for name, pat in [("LinkedIn", "linkedin"), ("Google", "google."), ("Bing", "bing."), ("Instagram", "instagram"),
                      ("Facebook", "facebook"), ("X / Twitter", "t.co"), ("Suffolk", "suffolk.edu"),
                      ("Suffolk assistant", "suffolklitsa.org")]:
        if pat in host:
            return name
    return host


def comp_hosts() -> dict[str, str]:
    try:
        items = json.load(open(os.path.join(SITE, "content", "competitions.json")))["items"]
    except Exception:
        return {}
    return {urlparse(c["url"]).netloc.lower().removeprefix("www."): c["name"] for c in items}


def is_planner_page(p: str) -> bool:
    return (p == "/planner" or p.startswith("/planner/")) and not p.startswith(PLANNER_EV)


def planner_lines(this: list[dict], prev: list[dict], change) -> list[str]:
    """The course planner section. Events arrive as views of /planner/ev/<name>[/<detail>]."""
    page = lambda rs: [r for r in rs if is_planner_page(r.get("path") or "")]
    ev = lambda rs: [r for r in rs if (r.get("path") or "").startswith(PLANNER_EV)]
    total = lambda rs: sum(r["n"] for r in rs)
    p_now, e_now = page(this), ev(this)
    L = ["", "## Course planner", ""]
    if not p_now and not e_now:
        return L + ["No views of /planner/ this week."]
    L.append(f"**{total(p_now)} page views of /planner/**{change(total(p_now), total(page(prev)))}, "
             f"{int(sum(r['n'] * (r.get('new_visitor') or 0) for r in p_now))} visitors.")

    # Funnel: each browser counted once a day, weighted by the sample interval of its first planner row,
    # so every step uses the same weight and no step can outgrow the first.
    steps = [("Opened the planner", lambda p: is_planner_page(p) or p.startswith(PLANNER_EV)),
             ("Searched or filtered", lambda p: p == PLANNER_EV + "search" or p.startswith(PLANNER_EV + "filter/")),
             ("Added a course", lambda p: p == PLANNER_EV + "add" or p.startswith(PLANNER_EV + "add/")),
             ("Shared or printed", lambda p: p in (PLANNER_EV + "share/create", PLANNER_EV + "print"))]
    weight, did = {}, collections.defaultdict(set)
    for r in sorted(this, key=lambda r: r["ts"]):
        p = r.get("path") or ""
        for name, test in steps:
            if test(p):
                weight.setdefault(browser(r), r["n"])
                did[browser(r)].add(name)
    reached = {name: sum(w for b, w in weight.items() if name in did[b]) for name, _ in steps}
    opened = reached[steps[0][0]]
    L += ["", "Funnel, counting each browser once a day:", ""]
    for name, _ in steps:
        share = f" ({round(reached[name] / opened * 100)}%)" if opened and name != steps[0][0] else ""
        L.append(f"- {name}: {reached[name]}{share}")

    counts, adds, errors = collections.Counter(), collections.Counter(), collections.Counter()
    for r in e_now:
        name = r["path"][len(PLANNER_EV):]
        if name.startswith("err/"):
            errors[name.split("/")[1]] += r["n"]
            continue
        if name.startswith("add/"):
            adds[name.split("/")[1]] += r["n"]
            name = "add"
        counts[name] += r["n"]
    L += ["", "Events: " + (", ".join(f"{k} {n}" for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
                             or "none") + "."]
    named = sorted(((c, n) for c, n in adds.items() if n >= PLANNER_MIN_ADDS), key=lambda cn: (-cn[1], cn[0]))
    rest = sum(n for c, n in adds.items() if n < PLANNER_MIN_ADDS)
    L.append(f"Courses added {PLANNER_MIN_ADDS} or more times: " + (", ".join(f"{c} ({n})" for c, n in named) or "none")
             + (f"; {rest} adds of other courses" if rest else "") + ".")
    L.append("Errors: " + (", ".join(f"{k} {n}" for k, n in errors.most_common()) or "none") + ".")
    return L


def digest(days: int = 7, now: dt.datetime | None = None) -> str:
    now = now or dt.datetime.now(dt.timezone.utc)
    raw = rows(days)
    data, bots = drop_bots(raw)
    start, prev_start = now - dt.timedelta(days=days), now - dt.timedelta(days=2 * days)
    this = [r for r in data if r["ts"] >= start]
    prev = [r for r in data if prev_start <= r["ts"] < start]
    views = lambda rs: [r for r in rs if not (r.get("path") or "").startswith(EVENTS)]
    outs = [r for r in this if (r.get("path") or "").startswith("/out/")]
    v_now, v_prev = views(this), views(prev)
    total = lambda rs: sum(r["n"] for r in rs)
    visitors = lambda rs: int(sum(r["n"] * (r.get("new_visitor") or 0) for r in rs))

    def change(a, b):
        return "" if not b else f" ({'+' if a >= b else ''}{round((a - b) / b * 100)}% on the {days} days before)"

    L = [f"# suffolklitsa.org, {days} days to {now:%b} {now.day}", ""]
    L.append(f"**{visitors(v_now)} visitors, {total(v_now)} page views**{change(total(v_now), total(v_prev))}. "
             f"Bots and test hits left out: {bots}. Board members who opened suffolklitsa.org/me/ are not counted.")
    if len(raw) >= ROW_LIMIT:
        # The query keeps the oldest rows, so a full result is missing the newest ones.
        L.append(f"**The query hit its {ROW_LIMIT}-row limit, so this week's numbers are short.**")
    L += ["", "## By day", ""]
    per_day = collections.Counter()
    for r in v_now:
        per_day[r["ts"].astimezone(dt.timezone(dt.timedelta(hours=-4))).date()] += r["n"]
    for i in range(days - 1, -1, -1):
        d = (now - dt.timedelta(days=i)).astimezone(dt.timezone(dt.timedelta(hours=-4))).date()
        L.append(f"- {d:%a %b} {d.day}: {per_day.get(d, 0)} {'█' * min(per_day.get(d, 0), 40)}")

    L += ["", "## Pages", ""]
    pages = collections.Counter()
    for r in v_now:
        pages[r["path"]] += r["n"]
    L += [f"- {p}: {n}" for p, n in pages.most_common(10)] or ["None."]

    L += ["", "## Where visitors came from", ""]
    srcs = collections.Counter()
    for r in v_now:
        srcs[source(r)] += r["n"]
    L += [f"- {s}: {n}" for s, n in srcs.most_common(8)] or ["None."]

    L += ["", "## Clicks that left the site", ""]
    comps, kinds, other, froms = comp_hosts(), collections.Counter(), collections.Counter(), collections.Counter()
    for r in outs:
        p, n = r["path"], r["n"]
        froms[r.get("ref") or "?"] += n
        if p == "/out/suconnect":
            kinds["Join on SUConnect"] += n
        elif p.startswith("/out/email/"):
            kinds[f"Email to {p.split('/')[3]}"] += n
        else:
            host = p.split("/")[2]
            if host in comps:
                kinds[f"Competition: {comps[host]}"] += n
            else:
                other[host] += n
    if not outs:
        L.append("None this week.")
    L += [f"- {k}: {n}" for k, n in kinds.most_common()]
    if other:
        L.append("- Elsewhere: " + ", ".join(f"{h} ({n})" for h, n in other.most_common(6)))
    if froms:
        L.append("- Clicked from: " + ", ".join(f"{p} ({n})" for p, n in froms.most_common(5)))

    L += ["", "## How far people read", ""]
    L.append("Of the views of each page, the share that scrolled halfway and to the bottom, and the most "
             "common time spent. Pages that fit on one screen record no scrolling.")
    L.append("")
    depth = collections.defaultdict(collections.Counter)
    stay = collections.defaultdict(collections.Counter)
    for r in this:
        p, ref = r.get("path") or "", r.get("ref") or ""
        if p.startswith("/depth/"):
            depth[ref][p.split("/")[2]] += r["n"]
        elif p.startswith("/time/"):
            stay[ref][p.split("/")[2]] += r["n"]
    pct = lambda a, b: f"{min(100, round(a / b * 100))}%" if b else "n/a"
    rows_read = []
    for p, n in pages.most_common(10):
        d, t = depth.get(p, {}), stay.get(p, {})
        common = max(t, key=lambda k: (t[k], -TIME_ORDER.index(k) if k in TIME_ORDER else 0)) if t else None
        rows_read.append(f"- {p}: {n} views, {pct(d.get('50', 0), n)} halfway, {pct(d.get('100', 0), n)} to the "
                         f"bottom" + (f", most stayed {common}" if common else ""))
    if not depth and not stay:
        L.append("Nothing recorded yet. Scroll and time tracking started September 29, 2026.")
    else:
        L += rows_read or ["None."]

    L += ["", "## Newsletter clicks", ""]
    nl = collections.Counter()
    for r in this:
        p = r.get("path") or ""
        if p.startswith("/nl/") and not p.startswith("/nl/test/"):
            nl[p] += r["n"]
    if not nl:
        L.append("None this week.")
    else:
        try:
            order = json.load(open(os.path.join(SITE, "newsletter_links.json")))
        except Exception:
            order = {}
        issues = sorted({p.split("/")[2] for p in nl}, key=lambda i: (len(i), i), reverse=True)
        for issue in issues:
            slugs = list(order.get(issue, {})) or sorted({p.split("/")[3] for p in nl if p.split("/")[2] == issue})
            L.append(f"- No. {issue}, top of the email first: " +
                     ", ".join(f"{s} {nl.get(f'/nl/{issue}/{s}', 0)}" for s in slugs))

    L += planner_lines(this, prev, change)

    L += ["", "## Who", ""]
    cc, dev = collections.Counter(), collections.Counter()
    for r in v_now:
        cc[r.get("country") or "?"] += r["n"]
        dev[r.get("device") or "?"] += r["n"]
    L.append("Countries: " + (", ".join(f"{c} {n}" for c, n in cc.most_common(5)) or "none") + ". "
             "Devices: " + (", ".join(f"{d} {n}" for d, n in dev.most_common()) or "none") + ".")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    try:
        print(digest(ap.parse_args().days))
    except Exception as ex:  # the email still goes out with the chatbot half
        print(f"# suffolklitsa.org\n\nSite numbers unavailable this week: {ex.__class__.__name__}: {ex}\n")
        sys.exit(1)

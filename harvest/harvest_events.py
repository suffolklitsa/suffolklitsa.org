"""Pull upcoming events from the sources that publish them, for /events/.

The hand-kept list in src/events_data.py stays the curated layer (ours, Suffolk's, the
one-offs). This adds whatever the machine-readable sources announce, so new events show up
without anyone re-checking pages by hand:

  Mass AI Coalition   its site ships its event list as Luma links; each event page is read
                      for name, time, place and price
  Luma calendars      Code & Counsel (legal AI builders) and the Coalition's partner calendar,
                      via Luma's public iCal feed, kept only when the topic fits
  Boston Bar          the BBA's public iCal feed, kept only when the topic fits
  Berkman Klein       Harvard's Berkman Klein Center has no feed; its events page lists upcoming
                      events as plain teasers (date, title, subtitle, RSVP links)

Writes content/events_auto.json. Upcoming events only. A source that fails keeps its last
good results, so one bad fetch never empties the page.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("EVENTS_OUT") or os.path.join(os.path.dirname(HERE), "content", "events_auto.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; LITSA-events/1.0; suffolklitsa.org)"}
ET = ZoneInfo("America/New_York")
TOPIC = re.compile(r"\bAI\b|artificial intelligence|machine learning|generative|legal tech|legaltech|"
                   r"technolog|privacy|cyber|data\b|intellectual property|patent|copyright|trademark|"
                   r"e-?discovery|innovation|blockchain|crypto|digital|software|automation", re.I)
LUMA_CALENDARS = {
    "cal-Slf1iP6ecIGwbim": "Code & Counsel",  # legal AI community: everything counts
    "cal-emQFVlpgfBmiF0S": "Mass AI Coalition partners",
}
LEGAL_CALENDARS = {"cal-Slf1iP6ecIGwbim"}  # legal-community calendars skip the topic filter
BBA_ICS = "https://bostonbar.org/events/?ical=1"
COALITION = "https://massaicoalition.com/"
BKC = "https://cyber.harvard.edu/events"


def get(url: str, tries: int = 2) -> str:
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001 (a source being down is routine)
            err = e
            time.sleep(3)
    raise err


def hhmm(t: dt.datetime) -> str:
    return t.strftime("%-I:%M").replace(":00", "") + t.strftime("%p").lower()


def span(start: dt.datetime, end: dt.datetime | None) -> str:
    if end and end.date() == start.date():
        a, b = hhmm(start), hhmm(end)
        if a[-2:] == b[-2:]:
            a = a[:-2]
        return f"{a}–{b}"
    if end and end.date() > start.date():
        return "multi-day"
    return hhmm(start)


def record(name, start, end, host, venue, cost, url, source):
    return dict(date=start.date().isoformat(), time=span(start, end), name=name.strip(), host=host,
                venue=venue or "See event page", cost=cost, url=url, source=source,
                tier="virtual" if re.search(r"virtual|zoom|online", venue or "", re.I) else "boston")


# ---------------------------------------------------------------- Luma event pages
def luma_event(slug: str, host: str) -> dict | None:
    t = get(f"https://luma.com/{slug}")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, re.S)
    if not m:
        return None
    data = json.loads(m.group(1))

    def walk(o, key, depth=0):
        if depth > 9:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if k == key:
                    yield v
                yield from walk(v, key, depth + 1)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v, key, depth + 1)

    ev = next((x for x in walk(data, "event") if isinstance(x, dict) and x.get("start_at")), None)
    if not ev:
        return None
    tz = ZoneInfo(ev.get("timezone") or "America/New_York")
    start = dt.datetime.fromisoformat(ev["start_at"].replace("Z", "+00:00")).astimezone(tz)
    end = dt.datetime.fromisoformat(ev["end_at"].replace("Z", "+00:00")).astimezone(tz) if ev.get("end_at") else None
    geo = ev.get("geo_address_info") or {}
    venue = geo.get("address") or geo.get("city") or ("Virtual" if ev.get("location_type") == "online" else "")
    tickets = next((x for x in walk(data, "ticket_info") if isinstance(x, dict)), {}) or {}
    cost = "Free" if tickets.get("is_free") else "See Luma"
    if tickets.get("require_approval"):
        cost += ", approval required"
    return record(ev["name"], start, end, host, venue, cost, f"https://luma.com/{slug}", "luma")


def scene(e: dict) -> dict:
    e["tier"] = "ai"  # the Coalition's calendar is Boston's AI scene, not legal-specific
    return e


def coalition() -> list[dict]:
    home = get(COALITION)
    js = re.search(r'src="(/assets/index-[^"]+\.js)"', home)
    if not js:
        raise RuntimeError("Coalition site no longer ships an index bundle")
    bundle = get(COALITION.rstrip("/") + js.group(1))
    slugs = sorted(set(re.findall(r"https://luma\.com/([a-z0-9]{8})\b", bundle)))
    out = []
    for s in slugs:
        try:
            e = luma_event(s, "Mass AI Coalition")
        except Exception as ex:  # noqa: BLE001
            print("  coalition event failed", s, ex, file=sys.stderr)
            continue
        if e:
            out.append(scene(e))
        time.sleep(1)
    return out


# ---------------------------------------------------------------- Berkman Klein
def berkman() -> list[dict]:
    t = get(BKC)
    i, j = t.find("Upcoming Events"), t.find("Past Events")
    if i < 0:
        raise RuntimeError("Berkman events page no longer has an Upcoming Events section")
    seg = t[i: j if j > i else None]
    out = []
    for item in seg.split('c-linear-list__item')[1:]:
        when = re.search(r'o-eyebrow">([A-Z][a-z]{2} \d{1,2}, \d{4}) @ (\d{1,2}:\d{2} [AP]M)<', item)
        title = re.search(r'c-media-block__title-link[^>]*>([^<]+)<', item)
        href = re.search(r'href="(/events/[^"]+)"', item)
        if not (when and title and href):
            continue
        start = dt.datetime.strptime(" ".join(when.groups()), "%b %d, %Y %I:%M %p").replace(tzinfo=ET)
        sub = re.search(r'c-media-block__subtitle"><p>([^<]+)<', item)
        zoom = "Zoom RSVP" in item
        person = "In-Person RSVP" in item
        venue = "Harvard, Cambridge" + (" and on Zoom" if zoom else "") if person else ("Zoom" if zoom else "See event page")
        e = record(html.unescape(title.group(1)), start, None, "Berkman Klein Center, Harvard", venue, "Free",
                   "https://cyber.harvard.edu" + href.group(1), "berkman")
        if person:
            e["tier"] = "boston"
        if sub:
            e["note"] = html.unescape(sub.group(1)).strip()
        out.append(e)
    return out


# ---------------------------------------------------------------- iCal feeds
def ics_events(text: str):
    text = re.sub(r"\r?\n[ \t]", "", text)  # unfold continuation lines
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        f = {}
        for line in block.strip().splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            f[k.split(";")[0]] = (k, v.replace("\\,", ",").replace("\\;", ";").replace("\\n", " ").strip())
        yield f


def ics_time(field) -> dt.datetime | None:
    if not field:
        return None
    k, v = field
    tzid = re.search(r"TZID=([^;:]+)", k)
    if re.fullmatch(r"\d{8}", v):
        return dt.datetime.strptime(v, "%Y%m%d").replace(tzinfo=ET)
    if v.endswith("Z"):
        return dt.datetime.strptime(v, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc).astimezone(ET)
    return dt.datetime.strptime(v[:15], "%Y%m%dT%H%M%S").replace(tzinfo=ZoneInfo(tzid.group(1)) if tzid else ET)


def from_ics(url: str, host: str, source: str, need_topic: bool) -> list[dict]:
    out = []
    for f in ics_events(get(url)):
        name = (f.get("SUMMARY") or ("", ""))[1]
        desc = (f.get("DESCRIPTION") or ("", ""))[1]
        if need_topic and not TOPIC.search(name + " " + desc[:600]):
            continue
        start = ics_time(f.get("DTSTART"))
        if not start:
            continue
        link = (f.get("URL") or ("", ""))[1] or url
        venue = (f.get("LOCATION") or ("", ""))[1]
        free = re.search(r"\bfree\b", desc, re.I)
        out.append(record(name, start, ics_time(f.get("DTEND")), host, venue,
                          "Free" if free else "See event page", link, source))
    return out


def main() -> int:
    today = dt.datetime.now(ET).date().isoformat()
    prior = {}
    if os.path.exists(OUT):
        for e in json.load(open(OUT)).get("events", []):
            prior.setdefault(e["source_key"], []).append(e)
    jobs = [("coalition", coalition)]
    jobs += [(f"luma:{cid}", lambda cid=cid, h=h: from_ics(
                f"https://api2.luma.com/ics/get?entity=calendar&id={cid}", h, "luma",
                cid not in LEGAL_CALENDARS))
             for cid, h in LUMA_CALENDARS.items()]
    jobs += [("bba", lambda: from_ics(BBA_ICS, "Boston Bar Association", "bba", True))]
    jobs += [("berkman", berkman)]
    events, status, failed = [], {}, 0
    for key, fn in jobs:
        try:
            got = fn()
            status[key] = f"ok {len(got)}"
        except Exception as ex:  # noqa: BLE001
            got = prior.get(key, [])
            status[key] = f"FAILED ({ex.__class__.__name__}); kept {len(got)} from last run"
            failed = 1
        for e in got:
            e["source_key"] = key
        events += got
    seen, keep = set(), []
    for e in sorted(events, key=lambda x: (x["date"], x["name"])):
        k = (e["date"], re.sub(r"[^a-z0-9]", "", e["name"].lower())[:30])
        if e["date"] >= today and k not in seen:
            seen.add(k)
            keep.append(e)
    json.dump({"fetched": dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), "status": status,
               "events": keep}, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(status), len(keep), "upcoming")
    return failed


if __name__ == "__main__":
    sys.exit(main())

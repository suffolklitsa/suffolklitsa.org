# -*- coding: utf-8 -*-
"""/events/ — the legal tech calendar, sorted.

Most of this is free and none of it is published anywhere together. Two layers: the
hand-kept list in events_data.py (ours, Suffolk's, one-offs), and content/events_auto.json,
refreshed twice a day by harvest/harvest_events.py from sources that publish their calendars.
Past events drop off at build time.
"""
import datetime
import json
import os
import re

import shell as sh
import data as D
import events_data as E

CSS = """
<style>
section.zone{padding-block:var(--s7); border-top:1px solid var(--line-soft);
  scroll-margin-top:var(--s6);}
.zone > h2{font-size:var(--t-2xl); margin-top:0;}
.zone > .lede{color:var(--ink-2); max-width:var(--measure); margin-top:var(--s3);
  font-size:var(--t-base);}
.index{display:flex; gap:var(--s5); flex-wrap:wrap; margin-top:var(--s6);
  border-top:2px solid var(--ink); border-bottom:1px solid var(--line);
  padding-block:var(--s4);}
.index a{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-2);}
.index a b{display:block; font-size:var(--t-2xl); letter-spacing:.01em;
  color:var(--ink); line-height:1; margin-bottom:5px;}
.index a:hover{color:var(--ink); text-decoration:none;}
.ev{display:grid; grid-template-columns:132px 1fr 150px; gap:var(--s4) var(--s5);
  padding-block:var(--s4); border-bottom:1px solid var(--line-soft);
  align-items:baseline;}
.ev .d{font-family:var(--display); font-size:var(--t-sm); letter-spacing:.03em;
  color:var(--ink);}
.ev .d span{display:block; color:var(--ink-3); font-size:var(--t-xs);
  margin-top:3px; letter-spacing:.05em;}
.ev h3{font-family:var(--display); font-size:var(--t-base); line-height:1.3;}
.ev h3 a{color:var(--ink);}
.ev .who{color:var(--ink-3); font-size:var(--t-xs); margin-top:5px;
  font-family:var(--display); letter-spacing:.04em;}
.ev p{color:var(--ink-2); font-size:var(--t-sm); margin-top:7px; line-height:1.55;
  max-width:62ch;}
.ev .cost{text-align:right; font-family:var(--display); font-size:10px;
  letter-spacing:.11em; text-transform:uppercase; color:var(--ink-3);}
.ev .cost.free{background:var(--ink); color:var(--paper); padding:3px 7px;
  display:inline-block;}
.ev.flag-deadline{background:var(--paper-2); box-shadow:inset 3px 0 0 var(--gold);
  padding-left:var(--s4);}
.ev.flag-pick h3::after, .ev.flag-ours h3::after{content:"Pick"; font-family:var(--display);
  font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--blue);
  margin-left:8px;}
.ev.flag-ours h3::after{content:"Ours"; color:var(--gold);}
.ev.flag-watch h3::after{content:"Watch"; font-family:var(--display); font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; color:var(--ink-3); margin-left:8px;}
.deadline{border:1px solid var(--gold); border-left-width:4px;
  background:var(--paper-2); padding:var(--s4) var(--s5); margin-top:var(--s6);}
.deadline h2{font-family:var(--display); font-size:var(--t-lg);}
.deadline p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  max-width:var(--measure);}
.mcle{margin-top:var(--s5);}
.mcle .row{display:grid; grid-template-columns:132px 1fr 96px; gap:var(--s4);
  padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  font-size:var(--t-sm); align-items:baseline;}
.mcle .row .d{font-family:var(--display); font-size:var(--t-xs); color:var(--ink);}
.mcle .row .p{text-align:right; font-family:var(--display); font-size:var(--t-xs);
  color:var(--ink);}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}
@media (max-width:760px){
  .ev, .mcle .row{grid-template-columns:1fr; gap:var(--s2);}
  .ev .cost, .mcle .row .p{text-align:left;}
  .ev.flag-deadline{padding-left:var(--s3);}}
</style>
"""


def event(e):
    free = "free" in (e.get("cost") or "").lower()
    flag = (" flag-%s" % e["flag"]) if e.get("flag") else ""
    title = D.esc(e["name"])
    if e.get("url"):
        title = '<a href="%s" rel="noopener">%s</a>' % (D.esc(e["url"]), title)
    note = ('<p>%s</p>' % D.esc(e["note"])) if e.get("note") else ""
    return ('<article class="ev%s"><div class="d">%s<span>%s</span></div>'
            '<div><h3>%s</h3><p class="who">%s &middot; %s</p>%s</div>'
            '<div><span class="cost%s">%s</span></div></article>'
            % (flag, E.when(e["date"]), D.esc(e["time"]), title,
               D.esc(e["host"]), D.esc(e["venue"]), note,
               " free" if free else "", D.esc(e["cost"])))


AUTO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content", "events_auto.json")


def _key(e):
    return (e["date"], re.sub(r"[^a-z0-9]", "", e["name"].lower())[:30])


def _squash(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _same_as_listed(e, events):
    """Calendars list one event twice with and without the host's name in the title
    ("Human in the Loop Ping Pong Meetup", "Code + Counsel's Human-in-the-Loop Ping Pong
    Meetup"). Same day and one title inside the other is the same event."""
    name = _squash(e["name"])
    for other in events:
        o = _squash(other["name"])
        if other["date"] == e["date"] and min(len(name), len(o)) >= 12 and (name in o or o in name):
            return True
    return False


def upcoming():
    """Hand-kept and harvested events, from today on, with duplicates removed."""
    today = datetime.date.today().isoformat()
    events = []
    for e in E.EVENTS:
        if e.get("dates"):  # recurring: show the next date
            nxt = [d for d in e["dates"] if d >= today]
            if not nxt:
                continue
            e = dict(e, date=nxt[0], note=(e.get("note") or "") +
                     (" Also " + ", ".join(E.when(d)[4:] for d in nxt[1:]) + "." if nxt[1:] else ""))
        events.append(e)
    auto, fetched = [], None
    if os.path.exists(AUTO):
        blob = json.load(open(AUTO))
        auto, fetched = blob.get("events", []), blob.get("fetched")
    have = {_key(e) for e in events} | {e.get("url") for e in events if e.get("url")}
    for e in auto:
        if _key(e) not in have and e.get("url") not in have and not _same_as_listed(e, events):
            events.append(e)
    return [e for e in events if e["date"] >= today], fetched


from urllib.parse import quote

SUGGEST = ("mailto:sam.darkwa@su.suffolk.edu?subject=" + quote("Event suggestion for the LITSA calendar")
           + "&body=" + quote("Event name:\nDate and time:\nLink:\nWhere:\nYour name and email:\n"))


def render():
    events, fetched = upcoming()
    by = {}
    for e in events:
        by.setdefault(e["tier"], []).append(e)
    for v in by.values():
        v.sort(key=lambda x: x["date"])

    idx = "".join(
        '<a href="#%s"><b>%d</b>%s</a>' % (k, len(by.get(k, [])), D.esc(label))
        for k, label, _ in E.TIERS)

    zones = "".join(
        '<section class="wrap zone" id="%s"><h2>%s</h2><p class="lede">%s</p>%s</section>'
        % (k, D.esc(label), D.esc(blurb),
           "".join(event(e) for e in by.get(k, [])))
        for k, label, blurb in E.TIERS)

    mcle = "".join(
        '<div class="row"><span class="d">%s</span><span>'
        '<a href="https://www.mcle.org/product/catalog/code/%s" rel="noopener">%s</a>'
        '</span><span class="p">%s</span></div>'
        % (E.when(d), code, D.esc(name), D.esc(price))
        for d, name, price, code in E.MCLE if d >= datetime.date.today().isoformat())

    free_count = sum(1 for e in events if "free" in (e.get("cost") or "").lower())
    stamp = (f"Calendars checked {D.esc(fetched)} &middot; hand-kept entries verified "
             f"{D.esc(E.VERIFIED)} &middot; every entry links to its source") if fetched else \
        f"Verified {D.esc(E.VERIFIED)} &middot; every entry links to its source"

    body = CSS + f"""
<section class="tight" style="padding-bottom:var(--s5)">
  <div class="wrap rail initial" data-initial="E">
    <p class="rail-label">Events</p>
    <div>
      <p class="eyebrow">Fall 2026</p>
      <h1 class="display">The legal tech calendar nobody publishes</h1>
      <p class="lede">{len(events)} things coming up,
      {free_count} of them free. Ours, Suffolk's, and everything around Boston worth
      leaving the building for.</p>
      <p class="stampline">{stamp}</p>
      <div class="acts" style="margin-top:var(--s5); display:flex; gap:var(--s4); flex-wrap:wrap; align-items:center">
        <a class="btn btn--ghost" href="{SUGGEST}">Suggest an event</a>
        <span class="small" style="color:var(--ink-2)">Know one we missed? Send the name, date, link and your name.</span>
      </div>
    </div>
  </div>
</section>

<section class="wrap" style="padding-block:0">
  <div class="index">{idx}</div>
</section>

<section class="wrap" style="padding-block:var(--s6) 0">{sh.scene("events-acorn-street.webp", "Acorn Street on Beacon Hill: a narrow cobblestone lane between brick row houses with black shutters and a gas lamp.", "Acorn Street, Beacon Hill, a few blocks from Sargent Hall.", size=(2016, 917))}</section>

{zones}

<section class="wrap zone" id="mcle">
  <h2>Worth paying for</h2>
  <p class="lede">MCLE's student rate is roughly half. Massachusetts has no mandatory
  CLE, so these are for the material rather than the credit hours.</p>
  <div class="mcle">{mcle}</div>
  <p class="stampline" style="margin-top:var(--s6)">
    Also: <a href="https://www.lexisnexis.com/en-us/training/training-calendar.page">LexisNexis
    runs about 21 free training webinars</a> between September 3 and December 10,
    several of them CLE-eligible.</p>
</section>
"""
    return sh.page("Events — LITSA",
                   "Legal tech events in Boston and beyond, fall 2026. Most of them free, "
                   "none of them published anywhere together.",
                   "/events/", body, reference=True)

# -*- coding: utf-8 -*-
"""/compete/ — moots, writing competitions, hackathons and fellowships a Suffolk student can enter.

Only ones that touch law and technology (IP, privacy, cyber, AI, legal tech, telecom), and
only ones a Suffolk student is eligible for. Grouped the way people look for them: who runs
it (a law school, or an organization with a reason to), then what kind it is.

The catalogue lives in content/competitions.json. Each entry was read off the organizer's own
page; ones whose date came from somewhere else carry verified=false and say so on the page.
The page is rebuilt twice a day by refresh_events.sh, and a deadline that has passed moves
itself to "next cycle not posted" with last year's date, so nothing expired is ever shown as
open. check_competitions.py flags dead links and changed organizer pages every Monday.
"""
import datetime as dt

import data as D
import shell as sh

KINDS = [("moot", "Moot courts"), ("writing", "Writing competitions"),
         ("build", "Hackathons and challenges"), ("fellowship", "Fellowships and scholarships")]
KIND_ONE = {"moot": "Moot court", "writing": "Writing", "build": "Hackathon or challenge",
            "fellowship": "Fellowship"}
SOON_DAYS = 45

CSS = """
<style>
.lede{max-width:60ch; color:var(--ink-2); font-size:var(--t-md); margin-top:var(--s5);}
.stamp{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.06em;
  color:var(--ink-3); margin-top:var(--s4);}
.stamp b{color:var(--ink);}
.band{margin-top:var(--s8); border-top:2px solid var(--ink); padding-top:var(--s4);}
.band > .blurb{color:var(--ink-2); max-width:60ch; margin-top:var(--s4);}
.lane{margin-top:var(--s6); padding-block:0;}
.lane > h3{font-size:var(--t-lg); border-bottom:1px solid var(--line); padding-bottom:var(--s3);}
.comp{display:grid; grid-template-columns:8rem minmax(0,1fr); gap:var(--s4);
  padding:var(--s4) 0; border-bottom:1px solid var(--line-soft); align-items:baseline;}
.comp .when{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.03em;
  font-variant-numeric:tabular-nums; line-height:1.5; color:var(--ink-3);}
.comp .when b{display:block; color:var(--gold); font-size:var(--t-sm); font-weight:inherit;}
.comp .when.later b{color:var(--ink-3);}
.comp .name{font-family:var(--display); font-size:var(--t-base); color:var(--ink); line-height:1.3;}
.comp .name a{color:inherit; text-decoration-color:var(--line);}
.comp .host{font-size:var(--t-xs); color:var(--ink-3); margin-top:var(--s1);}
.comp .topic{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s2); line-height:1.5;}
.comp .facts{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s2); line-height:1.55; max-width:70ch;}
.comp .facts span + span::before{content:" · "; color:var(--ink-3);}
.chip{display:inline-block; font-family:var(--display); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; border:1px solid var(--line); color:var(--ink-2);
  padding:1px 6px; margin:var(--s2) var(--s2) 0 0;}
.chip.ours{background:var(--gold); border-color:var(--gold); color:var(--ink);}
.chip.unv{border-style:dashed; color:var(--ink-3);}
.howto{margin-top:var(--s6); display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--s5) var(--s7);}
.howto article{border-top:2px solid var(--gold); padding-top:var(--s4);}
.howto h4{font-family:var(--display); font-size:var(--t-base);}
.howto p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3); line-height:1.55;}
.empty{color:var(--ink-3); font-size:var(--t-sm); margin-top:var(--s5);}
@media (max-width:820px){
  .howto{grid-template-columns:1fr;}
  .comp{grid-template-columns:1fr; gap:var(--s2);}
}
</style>
"""


def _date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def _state(c, today):
    """(open?, sort key). A passed deadline turns into last cycle's date."""
    dl = c.get("deadline")
    if dl and dt.date.fromisoformat(dl) >= today:
        return True, dl
    return False, "9999"


def _row(c, today, with_host_type=False):
    is_open, _ = _state(c, today)
    if is_open:
        when = f'<div class="when"><b>{D.esc(_date(c["deadline"]))}</b>{D.esc(c.get("label", "Deadline"))}</div>'
    else:
        last = c.get("last") or c.get("deadline")
        when = ('<div class="when later"><b>Not open yet</b>'
                + (f'last cycle {D.esc(_date(last))}' if last else "") + '</div>')
    facts = [c[k] for k in ("when", "entry", "prize") if c.get(k)]
    if not is_open:
        facts.insert(0, c.get("next") or "Next cycle not posted")
    chips = f'<span class="chip">{D.esc(KIND_ONE[c["kind"]])}</span>'
    if with_host_type:
        chips += f'<span class="chip">{"Law school" if c["host_type"] == "school" else "Organization"}</span>'
    if c.get("suffolk"):
        chips += f'<span class="chip ours">{D.esc(c["suffolk"])}</span>'
    if not c.get("verified", True):
        chips += '<span class="chip unv">Date not confirmed with the organizer</span>'
    return (f'<div class="comp">{when}<div>'
            f'<div class="name"><a href="{D.esc(c["url"])}">{D.esc(c["name"])}</a></div>'
            f'<div class="host">{D.esc(c["host"])}</div>'
            f'<p class="topic">{D.esc(c["topic"])}</p>'
            + (f'<p class="facts">{"".join(f"<span>{D.esc(f)}</span>" for f in facts)}</p>' if facts else "")
            + f'<div>{chips}</div></div></div>')


def _band(items, host_type, today):
    out = ""
    for kind, label in KINDS:
        rows = [c for c in items if c["host_type"] == host_type and c["kind"] == kind]
        if not rows:
            continue
        rows.sort(key=lambda c: (not _state(c, today)[0], _state(c, today)[1], c["name"]))
        out += (f'<section class="lane"><h3>{label}</h3>'
                + "".join(_row(c, today) for c in rows) + "</section>")
    return out


def render():
    cat = D.load("competitions") or {}
    items = cat.get("items") or []
    today = dt.date.today()
    soon = sorted((c for c in items if _state(c, today)[0]
                   and (dt.date.fromisoformat(c["deadline"]) - today).days <= SOON_DAYS),
                  key=lambda c: c["deadline"])
    soon_html = ("".join(_row(c, today, True) for c in soon)
                 or '<p class="empty">Nothing closes in the next six weeks.</p>')
    n_open = sum(1 for c in items if _state(c, today)[0])

    body = f"""
{CSS}
<section class="wrap">
  <h1>Compete</h1>
  <p class="lede">Moot courts, writing competitions, hackathons and fellowships in
  IP, privacy, cybersecurity, AI and legal tech that a Suffolk student can enter.
  {len(items)} of them, {n_open} open right now.</p>
  <div class="stamp">Catalogue checked <b>{D.esc(cat.get("checked", "—"))}</b>
    &middot; a deadline drops off the day after it passes</div>
  {sh.scene("compete-adams-courthouse.webp",
    "The John Adams Courthouse on Pemberton Square in Boston, a granite building with a mansard roof and an arched entrance, between taller modern towers.",
    'The John Adams Courthouse, home of the Supreme Judicial Court, ten minutes from Sargent Hall. '
    'Photo: Kenneth C. Zirkel, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.',
    True, (2016, 917))}

  <div class="band">
    <h2>Closing soon</h2>
    <p class="blurb">Everything with a deadline in the next six weeks, soonest first.</p>
    {soon_html}
  </div>

  <div class="band">
    <h2>Run by law schools</h2>
    <p class="blurb">Journals, centers and moot court boards at other schools. Moots
    take a school team, so they go through Suffolk's Moot Court Honor Board.</p>
    {_band(items, "school", today)}
  </div>

  <div class="band">
    <h2>Run by organizations</h2>
    <p class="blurb">Bar associations, industry groups, nonprofits and firms that
    want students working on these questions.</p>
    {_band(items, "org", today)}
  </div>

  <div class="band">
    <h2>How to enter</h2>
    <div class="howto">
      <article><h4>Moot courts</h4><p>Schools enter teams, not students. Ask
      the Moot Court Honor Board which ones Suffolk is sending and how teams
      are picked. Suffolk already enters Lefkowitz, Giles Rich and Jessup.</p></article>
      <article><h4>Writing competitions</h4><p>You enter on your own. A seminar
      paper or note you've already written often qualifies; check the length
      limit and whether it can be published already.</p></article>
      <article><h4>Missing one?</h4><p>Send it to
      <a href="mailto:sam.darkwa@su.suffolk.edu">sam.darkwa@su.suffolk.edu</a>
      with a link to the organizer's page and we'll add it.</p></article>
    </div>
  </div>
</section>
"""
    return sh.page("Compete — LITSA",
                   "Moot courts, writing competitions, hackathons and fellowships in IP, "
                   "privacy, cyber, AI and legal tech that Suffolk students can enter, with deadlines.",
                   "/compete/", body, reference=True)

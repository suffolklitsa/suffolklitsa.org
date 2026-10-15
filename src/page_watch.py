# -*- coding: utf-8 -*-
"""/watch/ — this week's headlines, what the courts are doing, who wrote about us, what to read.

Four things that all answer the same question: what is happening in this field
right now. The headlines come from outlets' own feeds twice a day (harvest_news.py):
their headline, their one-line description, a link, nothing rewritten. The court
list is machine-kept and refreshes weekly. The press and reading lists are curated
but machine-checked, so a dead link falls off rather than sitting there.

The last-checked date is printed on the page deliberately. If the job stops
running, the date goes stale in public, which is a better alarm than anything
we would remember to watch.
"""
import datetime as dt

import data as D
import shell as sh

CSS = """
<style>
.lede{max-width:58ch; color:var(--ink-2); font-size:var(--t-md); margin-top:var(--s5);}
.stamp{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.06em;
  color:var(--ink-3); margin-top:var(--s4);}
.stamp b{color:var(--ink);}
.band{margin-top:var(--s8); border-top:2px solid var(--ink); padding-top:var(--s4);}
.band > h2{max-width:20ch;}
.band > .blurb{color:var(--ink-2); max-width:58ch; margin-top:var(--s4);}
.lane{margin-top:var(--s6); padding-block:0;}
.lane > h3{font-size:var(--t-lg); border-bottom:1px solid var(--line);
  padding-bottom:var(--s3);}
.case{display:grid; grid-template-columns:6.5rem minmax(0,1fr); gap:var(--s4);
  padding:var(--s4) 0; border-bottom:1px solid var(--line-soft);
  align-items:baseline;}
.case .when{font-family:var(--display); font-size:var(--t-xs); color:var(--gold);
  letter-spacing:.03em; font-variant-numeric:tabular-nums; white-space:nowrap;}
.case .name{font-family:var(--display); font-size:var(--t-base); color:var(--ink);
  line-height:1.3;}
.case .name a{color:inherit; text-decoration-color:var(--line);}
.case .why{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s2);
  line-height:1.55; max-width:66ch;}
.case .court{font-size:var(--t-xs); color:var(--ink-3); margin-top:var(--s2);}
.press{margin-top:var(--s6); display:grid; gap:1px; background:var(--line-soft);
  border:1px solid var(--line-soft);}
.press article{background:var(--paper-2); padding:var(--s5);
  display:grid; grid-template-columns:7rem minmax(0,1fr); gap:var(--s4);
  align-items:baseline;}
.press .meta{font-family:var(--display); font-size:var(--t-xs); color:var(--ink-3);
  letter-spacing:.04em; line-height:1.6;}
.press .meta b{display:block; color:var(--ink); font-variant-numeric:tabular-nums;}
.press h4{font-family:var(--display); font-size:var(--t-base); line-height:1.3;}
.press h4 a{color:var(--ink); text-decoration-color:var(--line);}
.press p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  line-height:1.55; max-width:64ch;}
.tag-ours{display:inline-block; font-family:var(--display); font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; background:var(--gold);
  color:var(--ink); padding:2px 6px; margin-left:var(--s2); vertical-align:2px;}
.read{margin-top:var(--s6); display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr)); gap:var(--s5) var(--s7);}
.read article{border-top:2px solid var(--gold); padding-top:var(--s4);}
.read h4{font-family:var(--display); font-size:var(--t-base);}
.read h4 a{color:var(--ink); text-decoration-color:var(--line);}
.read .by{font-size:var(--t-xs); color:var(--ink-3); margin-top:var(--s2);}
.read p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  line-height:1.55;}
.news{margin-top:var(--s6); display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr)); gap:0 var(--s7);}
.news article{border-top:1px solid var(--line-soft); padding:var(--s4) 0 var(--s5);}
.news .meta{font-family:var(--display); font-size:var(--t-xs); color:var(--ink-3);
  letter-spacing:.04em; font-variant-numeric:tabular-nums;}
.news .meta b{color:var(--gold); font-weight:inherit;}
.news h4{font-family:var(--display); font-size:var(--t-base); line-height:1.3;
  margin-top:var(--s2); text-wrap:balance;}
.news h4 a{color:var(--ink); text-decoration-color:var(--line);}
.news p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s2);
  line-height:1.55; display:-webkit-box; -webkit-line-clamp:3;
  -webkit-box-orient:vertical; overflow:hidden;}
.empty{color:var(--ink-3); font-size:var(--t-sm); margin-top:var(--s5);}
.elsewhere-h{font-size:var(--t-lg); border-bottom:1px solid var(--line);
  padding-bottom:var(--s3); margin-top:var(--s7);}
@media (max-width:820px){
  .read,.news{grid-template-columns:1fr;}
  .case,.press article{grid-template-columns:1fr; gap:var(--s2);}
}
</style>
"""


def _case(c):
    return (f'<div class="case"><div class="when">{D.esc(c["date"])}</div>'
            f'<div><div class="name"><a href="{D.esc(c["url"])}">'
            f'{D.esc(c["case"])}</a></div>'
            f'<p class="why">{D.esc(c["why"])}</p>'
            f'<div class="court">{D.esc(c["court"])}'
            + (f' &middot; No. {D.esc(c["docket"])}' if c.get("docket") else "")
            + '</div></div></div>')


def _press(p):
    ours = ('<span class="tag-ours">Ours</span>' if p.get("kind") == "ours"
            else "")
    return (f'<article><div class="meta"><b>{D.esc(p["date"][:4])}</b>'
            f'{D.esc(p["outlet"])}</div>'
            f'<div><h4><a href="{D.esc(p["url"])}">{D.esc(p["title"])}</a>'
            f'{ours}</h4><p>{D.esc(p["note"])}</p></div></article>')


def _read(r):
    return (f'<article><h4><a href="{D.esc(r["url"])}">{D.esc(r["name"])}</a></h4>'
            f'<div class="by">{D.esc(r["by"])}</div>'
            f'<p>{D.esc(r["note"])}</p></article>')


def _day(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d:%b} {d.day}"


def _news(n):
    return (f'<article><div class="meta">{D.esc(_day(n["date"]))} &middot; '
            f'{D.esc(n["source"])} &middot; <b>{D.esc(n["tag"])}</b></div>'
            f'<h4><a href="{D.esc(n["url"])}">{D.esc(n["title"])}</a></h4>'
            + (f'<p>{D.esc(n["summary"])}</p>' if n.get("summary") else "")
            + '</article>')


def render():
    lit = D.load("litigation") or {}
    news = D.load("news") or {}
    headlines = "".join(_news(n) for n in (news.get("items") or []))
    if not headlines:
        headlines = '<p class="empty">No headlines right now. This list refreshes twice a day.</p>'
    press = D.load("press") or {}
    pub = set(lit.get("published") or [])
    items = [i for i in (lit.get("items") or []) if i["id"] in pub]

    lanes = ""
    for lane in lit.get("lanes", []):
        rows = [i for i in items if i.get("lane") == lane["id"]]
        if not rows:
            continue
        lanes += (f'<section class="lane"><h3>{D.esc(lane["label"])}</h3>'
                  + "".join(_case(c) for c in rows) + "</section>")
    if not lanes:
        lanes = ('<p class="empty">Nothing new since the last sweep. The list '
                 'refreshes weekly.</p>')

    coverage = "".join(_press(p) for p in (press.get("items") or []))
    reading = "".join(_read(r) for r in (press.get("reading") or []))

    checked = lit.get("last_success") or lit.get("last_run") or "not yet run"
    body = f"""
{CSS}
<section class="wrap">
  <h1>What we're watching</h1>
  <p class="lede">Courts, regulators and attackers are deciding what technology
  means for practice while we're still in school. This page tracks the week's
  news, the court decisions, and what's been written about the work happening
  at Suffolk.</p>
  <div class="stamp">Headlines refreshed <b>{D.esc(str(news.get("fetched", "—")))}</b>
    &middot; court list last refreshed <b>{D.esc(str(checked))}</b>
    &middot; links last checked <b>{D.esc(str(press.get("last_checked", "—")))}</b></div>

  <div class="band">
    <h2>This week</h2>
    <p class="blurb">AI, privacy, cybersecurity, IP and legal tech, from the
    outlets that cover them. Each headline and description is the outlet's own;
    click through for the story. Refreshed twice a day.</p>
    <div class="news">{headlines}</div>
  </div>

  <div class="band">
    <h2>In the courts</h2>
    <p class="blurb">Opinions where the court had to decide something about the
    technology itself. Gathered from CourtListener every week and screened
    before anything lands here. Each one links to the full opinion.</p>
    {lanes}

    <h3 class="elsewhere-h">Where else to look</h3>
    <p class="blurb">Two databases, each built around one question.</p>
    <div class="read">
      <article><h4><a href="https://www.damiencharlotin.com/hallucinations/">AI
      Hallucination Cases</a></h4>
      <div class="by">Damien Charlotin</div>
      <p>Every decision where a court found that a filing leaned on
      AI-fabricated material. More than two thousand of them so far, and the
      count moves most weeks.</p></article>
      <article><h4><a href="https://ai-legal-education.perl.chatgpt.site/">AI in
      Legal Education: Law School Policy Archive</a></h4>
      <div class="by">Andrew Perlman</div>
      <p>Public AI policies from 180 law schools, sorted by the question each
      one answers. Curated by our own dean, who takes corrections at a
      suffolk.edu address.</p></article>
    </div>
  </div>

  <div class="band">
    <h2>Written about us</h2>
    <p class="blurb">Coverage of legal innovation at Suffolk, and the pieces
    we've written ourselves.</p>
    <div class="press">{coverage}</div>
  </div>

  <div class="band">
    <h2>Worth reading</h2>
    <p class="blurb">Where this field gets discussed. Short on purpose.</p>
    <div class="read">{reading}</div>
  </div>
</section>
"""
    return sh.page("What we're watching — LITSA",
                   "This week's AI, privacy, cyber and legal-tech news, courts deciding questions about technology, coverage of "
                   "legal innovation at Suffolk, and where to follow the field.",
                   "/watch/", body, reference=True)

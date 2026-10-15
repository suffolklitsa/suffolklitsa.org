import datetime
import json
import os

import data as D
import shell as sh

CONTENT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content")

HERO_CSS = """
<style>
.hero{position:relative; overflow:hidden; border-bottom:1px solid var(--line-soft);
  max-width:100%;}
.hero{padding-block:0;}
.hero .wrap{position:relative; z-index:2; padding-block:var(--s7) var(--s8);}
.hero .pros{margin-top:var(--s5); color:var(--ink-2); font-size:var(--t-sm);}
.hero .editorial-scene{margin-top:var(--s6);}

.now{padding-top:var(--s7);}
.nowgrid{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:var(--s6) var(--s7);}
.nowcol{display:flex; flex-direction:column;}
.nowcol ul{flex:1 0 auto;}
.nowcol h3{font-size:var(--t-xs); font-family:var(--display); letter-spacing:.13em;
  text-transform:uppercase; color:var(--ink-3); border-bottom:2px solid var(--ink);
  padding-bottom:var(--s3);}
.nowcol ul{list-style:none; margin:0; padding:0;}
.nowcol li{padding:var(--s3) 0; border-bottom:1px solid var(--line-soft);}
.nowcol .d{display:block; font-family:var(--display); font-size:var(--t-xs); color:var(--gold);
  letter-spacing:.03em; font-variant-numeric:tabular-nums;}
.nowcol li a{color:var(--ink); font-size:var(--t-sm); line-height:1.45;}
.nowcol .by{display:block; font-size:var(--t-xs); color:var(--ink-3); margin-top:2px;}
.nowcol .all{display:inline-block; margin-top:var(--s4); font-family:var(--display);
  font-size:var(--t-xs); letter-spacing:.12em; text-transform:uppercase;}
@media (max-width:900px){.nowgrid{grid-template-columns:1fr;}}
.hero h1{max-width:min(13ch,100%);}
.hero .lede{margin-top:var(--s5);}
.hero .acts{display:flex; gap:var(--s4); align-items:center; margin-top:var(--s7);
  flex-wrap:wrap;}
.btn{font-family:var(--display); font-size:var(--t-sm); letter-spacing:.1em;
  text-transform:uppercase; padding:14px 22px; display:inline-block;}
.btn--solid{background:var(--blue); color:var(--paper);}
.btn--solid:hover{background:var(--blue-deep); text-decoration:none;}
.btn--ghost{color:var(--ink); box-shadow:inset 0 0 0 1.5px var(--ink);}
.btn--ghost:hover{background:var(--ink); color:var(--paper); text-decoration:none;}
/* torch at architectural scale, cropped hard by the viewport */
.hero .bleed{position:absolute; top:-12%; right:-6%; width:min(34vw,400px);
  z-index:1; pointer-events:none;}
.hero .bleed svg{width:100%; height:auto;}
@media (max-width:900px){.hero .bleed{right:-16%; width:46vw; top:auto; bottom:-14%;}}
@media (max-width:680px){.hero .wrap{padding-block:var(--s8) var(--s7);}}

.routes{display:grid; gap:var(--s7);}
.route{display:grid; grid-template-columns:minmax(0,1fr) auto; gap:var(--s5);
  align-items:end; padding-bottom:var(--s6); border-bottom:1px solid var(--line-soft);}
.route h3{margin-bottom:var(--s3);}
.route p{color:var(--ink-2); max-width:54ch;}
.route .go{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.12em;
  text-transform:uppercase; white-space:nowrap;}
@media (max-width:680px){.route{grid-template-columns:1fr; align-items:start;}}
</style>
"""

BODY = HERO_CSS + f"""
<section class="hero">
  <div class="bleed">{sh.torch_animated()}</div>
  <div class="wrap">
    <p class="eyebrow">Suffolk University Law School &middot; Boston</p>
    <h1 style="margin-top:var(--s5)">Where Suffolk Law meets legal tech.</h1>
    <p class="lede">LITSA is Suffolk Law&rsquo;s student organization for legal
    innovation and technology. We run a competition where teams ship working
    software in one evening, bring in the people already doing this work, and give
    you room to build something without waiting for permission.</p>
    <p class="lede" style="margin-top:var(--s4)"><b>You don&rsquo;t need to code.</b></p>
    <div class="acts">
      <a class="btn btn--solid" href="https://suffolk.campuslabs.com/engage/organization/litsa">Join on SUConnect</a>
      <a class="btn btn--ghost" href="/field/">See what the field covers</a>
    </div>
    <p class="pros">Practitioner or alum? <a href="/partners/">Speak, mentor, or set a
    problem for the build competition &rarr;</a></p>
    {sh.scene("home-sargent-hall-tremont.webp",
      "David J. Sargent Hall, Suffolk University Law School, on Tremont Street in Boston: a curved stone facade under a wide overhanging roof, with columns across the entrance and brick buildings on either side.",
      "Sargent Hall, 120 Tremont Street.", True, (2016, 1064))}
    <div class="grade">
      <span class="mk num">A<em>+</em></span>
      <span class="txt"><b>Suffolk is graded A+ for technology law.</b>
      <i>preLaw</i> magazine, 2026 &middot; one of twelve schools in the top tier.</span>
    </div>
  </div>
</section>

<!--NOW-->

{sh.step()}

<section>
  <div class="wrap rail">
    <p class="rail-label">Start here</p>
    <div class="routes">

      <article class="route">
        <div class="hd"><svg class="ico" viewBox="0 0 12 12" aria-hidden="true" shape-rendering="crispEdges"><rect x="0" y="0" width="3" height="3"/><rect x="4.5" y="0" width="3" height="3"/><rect x="9" y="0" width="3" height="3"/><rect x="0" y="4.5" width="3" height="3"/><rect x="9" y="4.5" width="3" height="3"/><rect x="4.5" y="9" width="3" height="3"/><rect x="9" y="9" width="3" height="3"/></svg><div>
          <h2 class="h3">Legal tech is not one thing</h2>
          <p>Privacy, AI regulation, access to justice, legal design, e-discovery,
          legal operations. Twelve domains, and eleven of them need no code.</p>
        </div></div>
        <a class="go" href="/field/">The field &rarr;</a>
      </article>

      <article class="route">
        <div class="hd"><svg class="ico" viewBox="0 0 12 12" aria-hidden="true" shape-rendering="crispEdges"><rect x="4.5" y="0" width="3" height="3"/><rect x="2.25" y="3" width="7.5" height="2.4"/><rect x="0" y="5.4" width="12" height="2.4"/><rect x="1.5" y="9" width="9" height="3"/></svg><div>
          <h2 class="h3">Suffolk already has the infrastructure</h2>
          <p>A concentration, the LIT Lab, a clinic run with the American
          Arbitration Association, a journal, and a conference held here every
          spring. Most students never find it.</p>
        </div></div>
        <a class="go" href="/suffolk/">At Suffolk &rarr;</a>
      </article>

      <article class="route" style="border-bottom:0; padding-bottom:0">
        <div class="hd"><svg class="ico" viewBox="0 0 12 12" aria-hidden="true" shape-rendering="crispEdges"><rect x="0" y="9" width="3" height="3"/><rect x="3" y="6" width="3" height="6"/><rect x="6" y="3" width="3" height="9"/><rect x="9" y="0" width="3" height="12"/></svg><div>
          <h2 class="h3">Four projects, and most of the work is not code</h2>
          <p>Testing, interviewing, writing problem sets, judging, mapping how a
          process actually works. Plenty of it never touches a keyboard.</p>
        </div></div>
        <a class="go" href="/build/">What we build &rarr;</a>
      </article>

    </div>
    {sh.scene("home-legal-worktable-pixel.webp",
      "A law-library table with books, a laptop and Boston brick buildings outside.",
      "A quiet workspace for reading, drafting and testing ideas.")}
  </div>
</section>

{sh.step()}

<section class="slab">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">Joining</p>
    <div>
      <h2>Join in about two minutes.</h2>
      <p class="lede" style="margin-top:var(--s5)">Sign in to SUConnect, press
      join, and tell us what you want out of it. No application, no screening,
      and no experience assumed.</p>
      <div class="acts" style="margin-top:var(--s7)">
        <a class="btn btn--solid" href="/join/">How to join</a>
      </div>
    </div>
  </div>
</section>
"""

def _day(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d:%a} {d:%b} {d.day}"


def now_panel():
    """Next events, closing competitions, this week's headlines. Rebuilt twice a day."""
    import page_events, page_compete
    today = datetime.date.today()
    events = sorted(page_events.upcoming()[0], key=lambda e: (e["date"], e.get("time") or ""))[:3]
    comps = json.load(open(os.path.join(CONTENT, "competitions.json"))).get("items", [])
    closing = sorted((c for c in comps if page_compete._state(c, today)[0]),
                     key=lambda c: c["deadline"])[:3]
    news = (json.load(open(os.path.join(CONTENT, "news.json"))).get("items", [])
            if os.path.exists(os.path.join(CONTENT, "news.json")) else [])[:3]

    def col(title, rows, href, more):
        items = "".join(rows) or '<li><span class="by">Nothing listed right now.</span></li>'
        return (f'<div class="nowcol"><h3>{title}</h3><ul>{items}</ul>'
                f'<a class="all" href="{href}">{more} &rarr;</a></div>')

    ev = [f'<li><span class="d">{_day(e["date"])}</span>'
          f'<a href="{D.esc(e.get("url") or "/events/")}">{D.esc(e["name"])}</a>'
          f'<span class="by">{D.esc(e.get("host") or "")}</span></li>' for e in events]
    cp = [f'<li><span class="d">{_day(c["deadline"])} &middot; {D.esc(c.get("label", "Deadline"))}</span>'
          f'<a href="{D.esc(c["url"])}">{D.esc(c["name"])}</a>'
          f'<span class="by">{D.esc(c["host"])}</span></li>' for c in closing]
    nw = [f'<li><span class="d">{_day(n["date"])} &middot; {D.esc(n["source"])}</span>'
          f'<a href="{D.esc(n["url"])}">{D.esc(n["title"])}</a></li>' for n in news]
    n_comps = len(comps)
    return (f'<section class="now"><div class="wrap rail"><p class="rail-label">Now</p>'
            f'<div class="nowgrid">'
            + col("Next up", ev, "/events/", "All events")
            + col("Closing soon", cp, "/compete/", f"All {n_comps} competitions")
            + col("In the news", nw, "/watch/", "This week")
            + '</div></div></section>')


def render():
    return sh.page(
        "LITSA · Legal Innovation and Technology at Suffolk Law",
        "The student organization for legal innovation and technology at Suffolk "
        "University Law School, graded A+ for technology law by preLaw magazine.",
        "/", BODY.replace("<!--NOW-->", now_panel()), reference=True)

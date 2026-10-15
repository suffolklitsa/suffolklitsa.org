# -*- coding: utf-8 -*-
"""/curriculum/ — the concentration index Suffolk does not publish.

The school's own /law/academics-clinics/jd-program/concentrations answers 200
with the 404 body, so there is no single page listing all seven with their
credit requirements. This is that page.
"""
import shell as sh
import data as D
import prose as P

CSS = """
<style>
.cgrid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s7) var(--s6); margin-top:var(--s7);}
.conc{border-top:2px solid var(--gold); padding-top:var(--s4);}
.conc .top{display:flex; justify-content:space-between; align-items:baseline;
  gap:var(--s3);}
.conc h2{font-size:var(--t-xl); line-height:1.15; max-width:18ch;}
.conc h2 a{color:var(--ink);}
.conc .cr{font-family:var(--display); font-size:var(--t-2xl); line-height:1;
  color:var(--ink); white-space:nowrap;}
.conc .cr span{font-size:var(--t-xs); letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-3); display:block; text-align:right; margin-top:4px;}
.conc p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s4);
  line-height:1.55;}
.conc .facts{display:flex; gap:var(--s4); flex-wrap:wrap; margin-top:var(--s4);
  font-family:var(--display); font-size:var(--t-xs); letter-spacing:.05em;
  color:var(--ink-3);}
.conc .facts b{color:var(--ink);}
.rulebox{margin-top:var(--s8); border:1px solid var(--line);
  background:var(--paper-2); padding:var(--s5);}
.rulebox h2{font-size:var(--t-xl);}
.rulebox dl{display:grid; grid-template-columns:200px 1fr; gap:var(--s3) var(--s5);
  margin-top:var(--s4); font-size:var(--t-sm);}
.rulebox dt{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3);}
.rulebox dd{color:var(--ink-2); margin:0;}
.caveat{margin-top:var(--s6); border-left:2px solid var(--gold);
  padding-left:var(--s4); color:var(--ink-2); font-size:var(--t-sm);
  max-width:var(--measure);}
.tracking{margin-top:var(--s4); border-left:2px solid var(--blue);
  padding-left:var(--s4); color:var(--ink-2); font-size:var(--t-sm);
  max-width:var(--measure);}
.aof{margin-top:var(--s8);}
.aof h2{font-size:var(--t-xl);}
.aof .chips{display:flex; gap:var(--s2); flex-wrap:wrap; margin-top:var(--s4);}
.aof .chips span{font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.05em; border:1px solid var(--line); padding:5px 10px;
  color:var(--ink-2); background:var(--paper-2);}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}
@media (max-width:880px){.cgrid{grid-template-columns:1fr;}
  .rulebox dl{grid-template-columns:1fr;} .rulebox dd{margin-bottom:var(--s3);}}
</style>
"""


def card(c):
    r = c["reconciliation"]
    cr = ('<p class="cr">%d<span>credits</span></p>' % c["credits_required"]
          if c["credits_required"] else '<p class="cr">&mdash;<span>not published</span></p>')
    return (
        '<article class="conc"><div class="top">'
        '<h2><a href="/curriculum/%s/">%s</a></h2>%s</div>'
        '<p>%s</p><div class="facts">'
        '<span><b>%d</b> courses count</span>'
        '<span><b>%d</b> run this year</span>'
        '<span><b>%d</b> spring only</span></div></article>'
        % (c["slug"], D.esc(c["name"]), cr,
           D.esc(P.CONCENTRATION_NOTES.get(c["key"], "")),
           r["listed"], r["offered_2026_27"], len(r["spring_only"])))


def render():
    cs = D.concentrations()
    u = D.universal()
    areas = D.load("crosswalk")["focus_areas"]
    courses = D.courses()
    body = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="C">
    <p class="rail-label">Curriculum</p>
    <div>
      <p class="eyebrow">What can I study</p>
      <h1 class="display">{D.esc(P.CURRICULUM['title'])}</h1>
      <p class="lede">{D.esc(P.CURRICULUM['lede'])}</p>
      <p class="caveat">{D.esc(P.CURRICULUM['caveat'])}</p>
      <p class="tracking">{D.esc(P.CURRICULUM['tracking_note'])}</p>
      <p class="stampline">Verified {D.esc(D.verified('concentrations'))} &middot;
      reconciled against {len(courses)} live 2026&ndash;27 sections</p>
    </div>
  </div>
</section>

<section class="wrap">
  <div class="cgrid">{"".join(card(c) for c in cs)}</div>

  <div class="rulebox">
    <h2>Rules that apply to all of them</h2>
    <dl>
      <dt>Eligibility</dt><dd>{D.esc(u['eligible'])}</dd>
      <dt>How many</dt><dd>One at a time. You may switch, but you graduate with one.</dd>
      <dt>Credit floor</dt><dd>The faculty minimum is {u['min_credits_floor']} credits.
        Every concentration sets its own higher.</dd>
      <dt>Grades</dt><dd>Cumulative {u['gpa_in_concentration']:.3f} across concentration
        courses, and nothing below {u['no_grade_below']:.3f} in any of them.</dd>
      <dt>Writing</dt><dd>A concentration thesis of publishable quality, or the legal
        writing requirement satisfied inside a concentration course.</dd>
      <dt>Experience</dt><dd>An experiential course or externship approved by the
        concentration Faculty Director.</dd>
      <dt>Enrol by</dt><dd>October 1 for January graduates, February 1 for May graduates.</dd>
      <dt>Completion form</dt><dd>{D.esc(u['completion_form'])}</dd>
      <dt>With distinction</dt><dd>{D.esc(u['distinction'])}</dd>
    </dl>
    <p class="stampline"><a href="{D.esc(u['rules_url'])}">Academic Rules &amp; Regulations</a></p>
  </div>

  <div class="aof">
    <h2>Areas of focus</h2>
    <p class="lede">Lighter than a concentration and not certified, but the registrar tags
    every course with them, which makes them the fastest way to find what to take next.</p>
    <div class="chips">{"".join("<span>%s</span>" % D.esc(a) for a in areas)}</div>
    <p class="stampline" style="margin-top:var(--s5)">
      <a href="/curriculum/courses/">Browse all {len(courses)} sections &rarr;</a></p>
  </div>
</section>
"""
    return sh.page("Curriculum — LITSA",
                   "All seven Suffolk Law concentrations with their credit requirements, "
                   "reconciled against the courses actually running in 2026-27.",
                   "/curriculum/", body, reference=True,
                   assistant_seed='Which Suffolk Law concentration should I consider?')

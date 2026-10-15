# -*- coding: utf-8 -*-
"""/curriculum/<concentration>/ — requirements, and what is actually running.

A concentration page lists what counts. The catalog lists what is offered. The
gap between them is the part that traps people, so it is stated rather than
implied: a spring-only core course is a scheduling constraint, not a footnote.
"""
import shell as sh
import data as D
import prose as P

CSS = """
<style>
.hdr h1{margin-bottom:var(--s5);}
.hdr .cr{font-family:var(--display); font-size:var(--t-4xl); line-height:1;
  display:flex; align-items:baseline; gap:var(--s3);
  border-top:2px solid var(--ink); padding-top:var(--s4); margin-top:var(--s5);
  max-width:420px;}
.hdr .cr span{font-size:var(--t-sm); letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-3);}
.hdr .lede{margin-top:var(--s5);}
.warn{margin-top:var(--s6); border:1px solid var(--gold);
  border-left-width:4px; background:var(--paper-2); padding:var(--s4) var(--s5);}
.warn h2{font-family:var(--display); font-size:var(--t-base); letter-spacing:.02em;}
.warn p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  max-width:var(--measure);}
.warn ul{margin-top:var(--s3);}
.warn li{font-size:var(--t-sm); color:var(--ink-2); padding-block:3px;}
.warn li b{font-family:var(--display); color:var(--ink);}
.reqs{margin-top:var(--s7);}
.reqs h2{font-size:var(--t-xl); border-bottom:2px solid var(--gold);
  padding-bottom:var(--s3);}
.reqs li{padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  font-size:var(--t-sm); color:var(--ink-2); line-height:1.55;}
.cgrp{margin-top:var(--s7);}
.cgrp > h3{font-family:var(--display); font-size:var(--t-base); letter-spacing:.02em;
  border-bottom:1px solid var(--line); padding-bottom:var(--s2);}
.crow{display:grid; grid-template-columns:1fr 78px 132px; gap:var(--s4);
  padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  align-items:baseline; font-size:var(--t-sm);}
.crow .t{color:var(--ink);}
.crow .cr2{font-family:var(--display); color:var(--ink-3); font-size:var(--t-xs);}
.crow .when{text-align:right; font-family:var(--display); font-size:10px;
  letter-spacing:.11em; text-transform:uppercase;}
.when-both{color:var(--ink-3);}
.when-fall{color:var(--ink); box-shadow:inset 0 -3px 0 var(--line);}
.when-spring{color:var(--ink); box-shadow:inset 0 -3px 0 var(--gold);}
.when-none{color:var(--ink-3); opacity:.75;}
.crow .who{color:var(--ink-3); font-size:var(--t-xs); grid-column:1/-1;
  margin-top:-6px;}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}
.backlink{margin-top:var(--s7); font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.1em; text-transform:uppercase;}
@media (max-width:760px){.crow{grid-template-columns:1fr 70px;}
  .crow .when{grid-column:1/-1; text-align:left;}}
</style>
"""

WHEN = {("fall", "spring"): ("Both terms", "both"), ("fall",): ("Fall only", "fall"),
        ("spring",): ("Spring only", "spring"), (): ("Not offered 2026-27", "none")}


def course_row(x):
    label, cls = WHEN[tuple(x["offered"])]
    who = ('<p class="who">%s</p>' % D.esc(", ".join(x["instructors"][:3]))) if x["instructors"] else ""
    cr = ("%g cr" % x["credits"]) if x.get("credits") else ""
    return ('<div class="crow"><span class="t">%s</span><span class="cr2">%s</span>'
            '<span class="when when-%s">%s</span>%s</div>'
            % (D.esc(x["title"]), cr, cls, D.esc(label), who))


def render(slug):
    c = [x for x in D.concentrations() if x["slug"] == slug][0]
    r = c["reconciliation"]
    u = D.universal()

    groups = {}
    for x in c["courses"]:
        groups.setdefault(x.get("group") or "Courses", []).append(x)

    blocks = []
    for g, items in groups.items():
        blocks.append('<section class="cgrp"><h3>%s</h3>%s</section>'
                      % (D.esc(g), "".join(course_row(x) for x in items)))

    warn = ""
    core_spring = [x["title"] for x in c["courses"]
                   if "core" in (x.get("group") or "").lower() and x["offered"] == ["spring"]]
    bits = []
    if core_spring:
        bits.append("<li><b>Core, spring only:</b> %s</li>" % D.esc(", ".join(core_spring)))
    if r["missing"]:
        bits.append("<li><b>Listed but not running in 2026&ndash;27:</b> %s</li>"
                    % D.esc(", ".join(r["missing"][:10])))
    if bits:
        warn = ('<div class="warn"><h2>Plan around these</h2>'
                '<p>%s</p><ul>%s</ul></div>'
                % (D.esc(D.load("concentrations")["reconciliation_note"]), "".join(bits)))

    cr = ('<p class="cr">%d<span>credits required</span></p>' % c["credits_required"]
          if c["credits_required"]
          else '<p class="cr">&mdash;<span>no total published</span></p>')

    body = CSS + f"""
<section class="tight" style="padding-bottom:var(--s5)">
  <div class="wrap rail initial" data-initial="{D.esc(c['name'][0])}">
    <p class="rail-label">Curriculum</p>
    <div class="hdr">
      <p class="eyebrow">Concentration</p>
      <h1 class="display">{D.esc(c['name'])}</h1>
      {cr}
      <p class="lede">{D.esc(P.CONCENTRATION_NOTES.get(c['key'], ''))}</p>
      <p class="stampline">Enrol by {D.esc(c['enroll_deadline'])} &middot;
      completion form {D.esc(u['completion_form'])}</p>
    </div>
  </div>
</section>

<section class="wrap" style="padding-top:var(--s5)">
  {warn}
  <div class="reqs">
    <h2>What it takes</h2>
    <ul>{"".join('<li>%s</li>' % D.esc(b) for b in c['requirement_bullets'])}</ul>
    <p class="stampline">
      <a href="{D.esc(c['requirements_url'])}">Suffolk's requirements page</a> &middot;
      <a href="{D.esc(c['courses_url'])}">its course list</a> &middot;
      <a href="{D.esc(u['rules_url'])}">Academic Rules</a></p>
  </div>

  <h2 style="margin-top:var(--s8); font-size:var(--t-2xl)">Courses that count</h2>
  <p class="lede">{r['listed']} listed, {r['offered_2026_27']} running this year.</p>
  {"".join(blocks)}

  <p class="stampline" style="margin-top:var(--s6)">
    Verified {D.esc(c['verified'])}. Confirm with Academic Services before you plan around it.</p>
  <p class="backlink"><a href="/curriculum/">&larr; All concentrations</a></p>
</section>
"""
    return sh.page("%s — Curriculum — LITSA" % c["name"],
                   "Requirements for the %s concentration at Suffolk Law, reconciled "
                   "against the 2026-27 catalog." % c["name"],
                   "/curriculum/%s/" % slug, body, reference=True,
                   assistant_seed="What does the %s concentration require?"
                   % c["name"])

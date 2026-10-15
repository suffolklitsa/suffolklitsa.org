# -*- coding: utf-8 -*-
"""/curriculum/courses/ — every section running in 2026-27, filterable.

Each course carries the resources for its subject, so "should I take Evidence"
and "I am in Evidence and it is week ten" land on the same row.
"""
import shell as sh
import data as D
import prose as P

CSS = """
<style>
.filters{margin-top:var(--s6); border-top:2px solid var(--ink);
  border-bottom:1px solid var(--line); padding-block:var(--s4);
  position:sticky; top:0; background:var(--paper); z-index:20;}
.frow{display:flex; gap:var(--s3); align-items:baseline; flex-wrap:wrap;
  margin-top:var(--s3);}
.frow:first-child{margin-top:0;}
.flabel{font-family:var(--display); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); flex:0 0 92px;}
.chip{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.06em;
  padding:5px 10px; border:1px solid var(--line); background:var(--paper-2);
  color:var(--ink-2); cursor:pointer;}
.chip:hover{border-color:var(--ink-3); color:var(--ink);}
.chip[aria-pressed="true"]{background:var(--ink); border-color:var(--ink);
  color:var(--paper);}
.chip .n{opacity:.55; margin-left:5px;}
.count{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); margin-top:var(--s4);}
.count b{color:var(--ink);}
.crs{margin-top:var(--s5); border-top:1px solid var(--line-soft);}
.c{padding-block:var(--s4); border-bottom:1px solid var(--line-soft);}
.c .top{display:grid; grid-template-columns:1fr 88px 116px; gap:var(--s4);
  align-items:baseline;}
.c h3{font-family:var(--display); font-size:var(--t-base); line-height:1.3;}
.c .cr{font-family:var(--display); font-size:var(--t-xs); color:var(--ink-3);}
.c .when{text-align:right; font-family:var(--display); font-size:10px;
  letter-spacing:.11em; text-transform:uppercase; color:var(--ink-3);}
.c .desc{color:var(--ink-2); font-size:var(--t-sm); margin-top:6px;
  max-width:74ch; line-height:1.55;}
.c .tags{display:flex; gap:var(--s3); flex-wrap:wrap; margin-top:var(--s3);
  font-family:var(--display); font-size:10px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3);}
.c .tags a{color:var(--blue);}
.c .tags .fl{border:1px solid var(--line); padding:2px 6px;}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}
@media (max-width:760px){
  .filters{position:static;} .flabel{flex:0 0 100%;}
  .c .top{grid-template-columns:1fr;} .c .when{text-align:left;}}
</style>
"""


def render():
    courses = D.courses()
    cm = D.course_map()
    subs = {s["subject"]: s for s in D.subjects()}

    # One row per title per term, rather than per section: five sections of
    # Torts is one course as far as planning goes.
    seen, rows = set(), []
    for c in courses:
        key = (c["base_title"], c["term"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(c)
    rows.sort(key=lambda x: (x["base_title"], x["term"]))

    areas, flags = {}, {}
    for c in rows:
        for f in c["focus"]:
            areas[f["area"]] = areas.get(f["area"], 0) + 1
        for f in c["flags"]:
            flags[f] = flags.get(f, 0) + 1
    keep_flags = ["Experiential Learning", "Massachusetts Bar Courses",
                  "Legal Writing Requirement", "Civil Litigation Requirement",
                  "Clinicals/Internships", "First Year", "Perspective Courses (Law)"]

    def chips(field, mapping, order=None):
        keys = order or sorted(mapping)
        return "".join(
            '<button class="chip" data-f="%s" data-v="%s" aria-pressed="false">%s'
            '<span class="n">%d</span></button>' % (field, D.esc(k), D.esc(k), mapping[k])
            for k in keys if k in mapping)

    def row(c):
        term = "fall" if "Fall" in c["term"] else "spring"
        tags = []
        for s in cm.get(c["base_title"], {}).get("subjects", []):
            if s in subs:
                tags.append('<a href="/resources/%s/">%s resources</a>' % (subs[s]["slug"], D.esc(s)))
        for f in c["flags"]:
            if f in keep_flags:
                tags.append('<span class="fl">%s</span>' % D.esc(f))
        for f in c["focus"]:
            tags.append('<span class="fl">%s</span>' % D.esc(f["area"]))
        desc = c["description"][:340] + ("..." if len(c["description"]) > 340 else "")
        return (
            '<article class="c" data-term="%s" data-areas="%s" data-flags="%s" '
            'data-mode="%s" data-title="%s">'
            '<div class="top"><h3>%s</h3><span class="cr">%s</span>'
            '<span class="when">%s</span></div>'
            '<p class="desc">%s</p><div class="tags">%s</div></article>'
            % (term, D.esc("|".join(f["area"] for f in c["focus"])),
               D.esc("|".join(c["flags"])), D.esc(c["delivery"]),
               D.esc(c["base_title"].lower()), D.esc(c["base_title"]),
               ("%g cr" % c["credits"]) if c["credits"] else "",
               "Fall 2026" if term == "fall" else "Spring 2027",
               D.esc(desc), "".join(tags)))

    modes = {}
    for c in rows:
        modes[c["delivery"]] = modes.get(c["delivery"], 0) + 1

    body = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="A">
    <p class="rail-label">Curriculum</p>
    <div>
      <p class="eyebrow">2026&ndash;27</p>
      <h1 class="display">Every course running this year</h1>
      <p class="lede">{len(rows)} course offerings across both terms, tagged the way the
      registrar tags them, and linked to the study aids for the subject.</p>
      <p class="stampline">Verified {D.esc(D.verified('courses'))} &middot;
      {len(courses)} sections &middot;
      <a href="/curriculum/">concentrations &rarr;</a></p>
    </div>
  </div>
</section>

<section class="wrap">
  <div class="filters" id="crs-filters">
    <div class="frow"><span class="flabel">Term</span>
      <button class="chip" data-f="term" data-v="fall" aria-pressed="false">Fall 2026</button>
      <button class="chip" data-f="term" data-v="spring" aria-pressed="false">Spring 2027</button>
    </div>
    <div class="frow"><span class="flabel">Area</span>{chips("areas", areas)}</div>
    <div class="frow"><span class="flabel">Satisfies</span>{chips("flags", flags, keep_flags)}</div>
    <div class="frow"><span class="flabel">Delivery</span>{chips("mode", modes)}</div>
  </div>
  <p class="count" id="crs-count">Showing <b>{len(rows)}</b> of {len(rows)}</p>
  <div class="crs" id="crs-rows">{"".join(row(c) for c in rows)}</div>
</section>
"""
    return sh.page("Courses 2026–27 — LITSA",
                   "Every Suffolk Law course running in 2026-27, filterable by area of "
                   "focus, requirement and term, linked to the study aids for each subject.",
                   "/curriculum/courses/", body, reference=True,
                   assistant_seed='What courses should I take next semester?')

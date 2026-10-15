# -*- coding: utf-8 -*-
"""/resources/<subject>/ — everything for one subject, in one place.

Both guides group their entries, and their groupings are written for students
rather than librarians, so we keep their vocabulary instead of inventing one.
"""
import shell as sh
import data as D
import prose as P

KIND_ORDER = ["outline", "practice", "cali", "audio", "intro", "depth",
              "practical", "massachusetts", "other"]
KIND_LABEL = {
    "outline": "Reviews, outlines and checklists",
    "practice": "Practice exam questions",
    "cali": "CALI lessons",
    "audio": "Audio and video",
    "intro": "Introductory treatises",
    "depth": "In depth",
    "practical": "Practical materials",
    "massachusetts": "Massachusetts materials",
    "other": "Also worth knowing",
}
KIND_NOTE = {
    "massachusetts": "Practice material for this jurisdiction. Most of it is MCLE, "
                     "and it stays useful well past the exam.",
    "cali": "Free, but you need an authorization code from the research desk.",
}

CSS = """
<style>
.grp{margin-top:var(--s7);}
.grp > h2{font-size:var(--t-xl); border-bottom:2px solid var(--gold);
  padding-bottom:var(--s3);}
.grp > .gnote{color:var(--ink-3); font-size:var(--t-sm); margin-top:var(--s3);
  max-width:var(--measure);}
.items{margin-top:var(--s4);}
.item{display:grid; grid-template-columns:1fr 120px; gap:var(--s4);
  padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  align-items:baseline;}
.item a{color:var(--ink); font-size:var(--t-base);}
.item .acc{justify-self:end;}
.acc{display:inline-block; font-family:var(--display); font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; padding:3px 7px;
  border:1px solid var(--line); color:var(--ink-3);}
.acc-open{background:var(--ink); color:var(--paper); border-color:var(--ink);}
.acc-account{border-color:var(--gold); box-shadow:inset 0 -3px 0 var(--gold);
  color:var(--ink);}
.tallybar{display:flex; gap:var(--s6); flex-wrap:wrap; margin-top:var(--s6);
  border-top:2px solid var(--ink); border-bottom:1px solid var(--line);
  padding-block:var(--s4);}
.tallybar div b{font-family:var(--display); font-size:var(--t-2xl); display:block;
  line-height:1;}
.tallybar div span{font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3);}
.running{margin-top:var(--s6); border-top:1px solid var(--line);
  padding-top:var(--s4);}
.running .eyebrow{margin-bottom:var(--s3);}
.crow{display:grid; grid-template-columns:1fr 70px 108px 168px; gap:var(--s4);
  padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  font-size:var(--t-sm); align-items:baseline;}
.crow .t{color:var(--ink);}
.crow .cr2, .crow .who{color:var(--ink-3); font-size:var(--t-xs);}
.crow .when{font-family:var(--display); font-size:10px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--ink-2);}
.running .more{margin-top:var(--s4); font-family:var(--display);
  font-size:var(--t-xs); letter-spacing:.1em; text-transform:uppercase;}
@media (max-width:760px){.crow{grid-template-columns:1fr; gap:2px;}}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}
.backlink{margin-top:var(--s7); font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.1em; text-transform:uppercase;}
@media (max-width:760px){.item{grid-template-columns:1fr;} .item .acc{justify-self:start;}}
</style>
"""

ACC_LABEL = {k: v[0] for k, v in P.ACCESS.items()}


def item(x):
    a = x.get("access", "unknown")
    return ('<div class="item"><a href="%s" rel="noopener">%s</a>'
            '<span class="acc acc-%s">%s</span></div>'
            % (D.esc(x["url"]), D.esc(x["title"]), a,
               D.esc(ACC_LABEL.get(a, "Check"))))


def render(slug):
    s = D.subject(slug)
    sa = D.studyaids().get(s["studyaids_subject"]) if s["studyaids_subject"] else None
    tre = D.treatises().get(s["treatises_subject"]) if s["treatises_subject"] else None
    dbs = {x["title"]: x for x in D.databases()}

    groups = {}
    for src in (sa, tre):
        if not src:
            continue
        for it in src["items"]:
            groups.setdefault(it["kind"], []).append(it)

    blocks = []
    for k in KIND_ORDER:
        if k not in groups:
            continue
        note = ('<p class="gnote">%s</p>' % D.esc(KIND_NOTE[k])) if k in KIND_NOTE else ""
        blocks.append('<section class="grp"><h2>%s</h2>%s<div class="items">%s</div></section>'
                      % (KIND_LABEL[k], note, "".join(item(x) for x in groups[k])))

    if s["databases"]:
        rows = "".join(
            '<div class="item"><a href="%s" rel="noopener">%s</a>'
            '<span class="acc acc-%s">%s</span></div>'
            % (D.esc(dbs[t]["url"]), D.esc(t), dbs[t]["access"],
               D.esc(ACC_LABEL.get(dbs[t]["access"], "Check")))
            for t in s["databases"] if t in dbs)
        blocks.append('<section class="grp"><h2>Databases for this subject</h2>'
                      '<div class="items">%s</div></section>' % rows)

    # What is actually running in this subject. Saying "Torts covers Torts" is
    # true and useless; the term and the instructor are the part worth knowing.
    cm = D.course_map()
    # Direct title matches only. Routing through an Area of Focus is right for
    # "what should I read", but it puts Advanced Civil Procedure on the Torts
    # page, which is wrong for "what is running in this subject".
    titles = {c["title"] for c in cm.values() if c.get("primary") == s["subject"]}
    running = {}
    for c in D.courses():
        if c["base_title"] not in titles:
            continue
        r = running.setdefault(c["base_title"], {"terms": set(), "who": set(),
                                                 "credits": c["credits"]})
        r["terms"].add("fall" if "Fall" in c["term"] else "spring")
        r["who"].update(c["instructors"])

    c = s["counts"]
    tally = []
    for label, n in (("Study aids", c["studyaids"]), ("Treatises", c["treatises"]),
                     ("Massachusetts", c["massachusetts"]), ("Databases", c["databases"])):
        if n:
            tally.append("<div><b>%d</b><span>%s</span></div>" % (n, label))

    cls_html = ""
    if running:
        rows = []
        for t in sorted(running):
            r = running[t]
            terms = "Both terms" if len(r["terms"]) > 1 else (
                "Fall 2026" if "fall" in r["terms"] else "Spring 2027")
            who = ", ".join(sorted(r["who"])[:2])
            cr = ("%g cr" % r["credits"]) if r["credits"] else ""
            rows.append('<div class="crow"><span class="t">%s</span>'
                        '<span class="cr2">%s</span><span class="when">%s</span>'
                        '<span class="who">%s</span></div>'
                        % (D.esc(t), cr, terms, D.esc(who)))
        cls_html = ('<div class="running"><p class="eyebrow">Running this year</p>%s'
                    '<p class="more"><a href="/curriculum/courses/">All 2026&ndash;27 '
                    'courses &rarr;</a></p></div>' % "".join(rows))

    src_links = []
    if sa:
        src_links.append('<a href="%s">study aids guide</a>' % D.esc(sa["source"]))
    if tre:
        src_links.append('<a href="%s">treatises guide</a>' % D.esc(tre["source"]))

    body = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="{D.esc(s['subject'][0])}">
    <p class="rail-label">Resources</p>
    <div>
      <p class="eyebrow">Subject</p>
      <h1 class="display">{D.esc(s['subject'])}</h1>
      <p class="lede">{D.esc(P.SUBJECTS.get(s['subject'], ''))}</p>
      <div class="tallybar">{"".join(tally)}</div>
      {cls_html}
      <p class="stampline">Verified {D.esc(D.verified('studyaids'))} &middot;
      source: {" &middot; ".join(src_links) if src_links else "Moakley Law Library"}</p>
    </div>
  </div>
</section>
<section class="wrap">
  {"".join(blocks)}
  <p class="backlink"><a href="/resources/">&larr; All resources</a></p>
</section>
"""
    return sh.page("%s — Resources — LITSA" % s["subject"],
                   "Study aids, treatises, Massachusetts practice material and databases "
                   "for %s at Suffolk Law." % s["subject"],
                   "/resources/%s/" % slug, body, reference=True,
                   assistant_seed="What study aids does Suffolk have for %s?"
                   % s["subject"])

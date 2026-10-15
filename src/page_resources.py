# -*- coding: utf-8 -*-
"""/resources/ — one page, three zones, no hierarchy.

The library already has a hierarchy: 54 pages, 26 guides, a 101-item A-Z list.
Rebuilding it would be a second maze. What this adds instead is selection, an
honest access state per item, and a verification date on everything.
"""
import json

import shell as sh
import data as D
import prose as P

CSS = """
<style>
/* section already carries padding-block:s9; a margin on top of that reads as a
   dropped page rather than a new section. */
section.zone{padding-block:var(--s7); scroll-margin-top:var(--s6);
  border-top:1px solid var(--line-soft);}
.zone > h2{margin-top:0;}
.zone > h2{font-size:var(--t-3xl); max-width:16ch;}
.zone .lede{color:var(--ink-2); max-width:var(--measure); margin-top:var(--s4);
  font-size:var(--t-md);}
.zone .note{color:var(--ink-3); max-width:var(--measure); margin-top:var(--s4);
  font-size:var(--t-sm); border-left:2px solid var(--gold); padding-left:var(--s4);}

/* ---- filter bar ---- */
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

/* ---- database rows ---- */
.rows{margin-top:var(--s5); border-top:1px solid var(--line-soft);}
.row{display:grid; grid-template-columns:1fr 148px; gap:var(--s4) var(--s5);
  padding-block:var(--s4); border-bottom:1px solid var(--line-soft);
  align-items:start;}
.row h3{font-family:var(--display); font-size:var(--t-base); letter-spacing:.01em;
  line-height:1.3;}
.row h3 a{color:var(--ink);}
.row p{color:var(--ink-2); font-size:var(--t-sm); line-height:1.55;
  margin-top:6px; max-width:62ch;}
.row .meta{text-align:right;}
.row .subj{color:var(--ink-3); font-size:var(--t-xs); margin-top:8px;
  font-family:var(--display); letter-spacing:.04em;}
.acc{display:inline-block; font-family:var(--display); font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; padding:3px 7px;
  border:1px solid var(--line);}
.acc-open{background:var(--ink); color:var(--paper); border-color:var(--ink);}
.acc-proxy{color:var(--ink-2);}
.acc-account{border-color:var(--gold); box-shadow:inset 0 -3px 0 var(--gold);
  color:var(--ink);}
.acc-platform,.acc-print,.acc-code,.acc-unknown{color:var(--ink-3);}
.acchelp{color:var(--ink-3); font-size:var(--t-xs); margin-top:6px;
  text-align:right; line-height:1.4;}

/* ---- subject cards ---- */
.cards{display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
  gap:var(--s6) var(--s6); margin-top:var(--s6);}
.card{border-top:2px solid var(--gold); padding-top:var(--s4);}
.card h3{font-size:var(--t-lg); line-height:1.2;}
.card h3 a{color:var(--ink);}
.card p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  line-height:1.55;}
.card .tally{display:flex; gap:var(--s4); flex-wrap:wrap; margin-top:var(--s4);
  font-family:var(--display); font-size:var(--t-xs); letter-spacing:.05em;
  color:var(--ink-3);}
.card .tally b{color:var(--ink); font-size:var(--t-base);}
.card.mine{border-top-color:var(--blue);}
.card.mine h3::after{content:"Yours"; font-family:var(--display); font-size:10px;
  letter-spacing:.12em; text-transform:uppercase; color:var(--blue);
  margin-left:8px; vertical-align:middle;}

/* ---- section picker ---- */
.zindex{display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
  gap:1px; background:var(--line-soft); border:1px solid var(--line-soft);
  margin-top:var(--s6);}
.zindex a{background:var(--paper-2); padding:var(--s5) var(--s5) var(--s6);
  font-family:var(--display); font-size:var(--t-xs); letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink);}
.zindex a b{display:block; font-size:var(--t-3xl); line-height:1;
  letter-spacing:.01em; margin-bottom:var(--s3);}
.zindex a span{display:block; text-transform:none; letter-spacing:0;
  font-family:var(--body); font-size:var(--t-sm); color:var(--ink-3);
  margin-top:6px;}
.zindex a:hover{background:var(--paper); text-decoration:none;}
@media (max-width:760px){.zindex{grid-template-columns:1fr;}}

.picker{border:1px solid var(--line); background:var(--paper-2);
  padding:var(--s5) var(--s6); max-width:760px;}
section.pickwrap{padding-block:0 var(--s7);}
.picker h2{font-size:var(--t-xl);}
.branch{margin-top:var(--s4);
  border-top:1px solid var(--line-soft); padding-top:var(--s4);}
.picker p{color:var(--ink-2); font-size:var(--t-sm); margin-top:var(--s3);
  max-width:56ch;}
.picker .grp{margin-top:var(--s4);}
.picker .glabel{font-family:var(--display); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin-bottom:var(--s2);}
.picker .opts{display:flex; gap:var(--s2); flex-wrap:wrap;}
.mine-out{margin-top:var(--s5); border-top:1px solid var(--line);
  padding-top:var(--s4); font-size:var(--t-sm); color:var(--ink-2);}
.mine-out b{font-family:var(--display); letter-spacing:.04em; color:var(--ink);}

/* ---- services ---- */
.svc{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s5) var(--s6); margin-top:var(--s6);}
.svc article{border-top:1px solid var(--line); padding-top:var(--s4);}
.svc h3{font-family:var(--display); font-size:var(--t-base); line-height:1.3;}
.svc h3 a{color:var(--ink);}
.svc p{color:var(--ink-2); font-size:var(--t-sm); margin-top:6px; line-height:1.55;}
.svc .renew{color:var(--ink); font-size:var(--t-sm); margin-top:8px;
  border-left:2px solid var(--gold); padding-left:10px;}
.absent{margin-top:var(--s7); border-top:2px solid var(--ink); padding-top:var(--s4);}
.absent li{padding-block:var(--s3); border-bottom:1px solid var(--line-soft);
  font-size:var(--t-sm); color:var(--ink-2);}
.absent li b{font-family:var(--display); color:var(--ink); letter-spacing:.02em;}
.stampline{color:var(--ink-3); font-size:var(--t-xs); margin-top:var(--s4);
  font-family:var(--display); letter-spacing:.08em; text-transform:uppercase;}

@media (max-width:980px){.cards{grid-template-columns:repeat(2,minmax(0,1fr));}}
@media (max-width:760px){
  .cards,.svc{grid-template-columns:1fr;}
  .row{grid-template-columns:1fr;}
  .row .meta,.acchelp{text-align:left;}
  .filters{position:static;}
  .flabel{flex:0 0 100%;}
}
</style>
"""



# Goals shown ahead of Suffolk's official areas of focus in "What are you working toward".
GOALS = {
    "Bar prep": ["Bar Exam", "Exam Prep", "Civil Procedure", "Constitutional Law", "Contracts",
                 "Criminal Law", "Criminal Procedure", "Evidence", "Property", "Torts",
                 "Business Entity Fundamentals", "Family Law", "Trusts & Estates",
                 "Professional Responsibility"],
    "Legal Innovation and Technology": ["Professional Responsibility", "Trademarks",
                                        "Administrative Law"],
}
GOAL_NOTES = {
    "Bar prep": "The MBE and MEE subjects, most of them 1L courses, plus Professional "
                "Responsibility for the MPRE.",
    "Legal Innovation and Technology": "Legal tech has few study aids of its own; these are the "
                "doctrinal courses it leans on. The courses themselves are on the "
                '<a href="/curriculum/legal-innovation-technology/">concentration page</a>.',
}

def acc_chip(a):
    label, _ = P.ACCESS.get(a, P.ACCESS["unknown"])
    return '<span class="acc acc-%s">%s</span>' % (a, D.esc(label))


def db_row(x):
    subs = ", ".join(x["subjects"][:3])
    return (
        '<article class="row" data-access="%s" data-subjects="%s" data-title="%s">'
        '<div><h3><a href="%s" rel="noopener">%s</a></h3><p>%s</p>%s</div>'
        '<div class="meta">%s<p class="acchelp">%s</p></div></article>'
        % (x["access"], D.esc("|".join(x["subjects"])), D.esc(x["title"].lower()),
           D.esc(x["url"]), D.esc(x["title"]), D.esc(x["description"]),
           ('<p class="subj">%s</p>' % D.esc(subs)) if subs else "",
           acc_chip(x["access"]), D.esc(P.ACCESS.get(x["access"], P.ACCESS["unknown"])[1])))


def subject_card(s):
    c = s["counts"]
    bits = []
    if c["studyaids"]:
        bits.append("<b>%d</b> study aids" % c["studyaids"])
    if c["treatises"]:
        bits.append("<b>%d</b> treatises" % c["treatises"])
    if c["massachusetts"]:
        bits.append("<b>%d</b> Massachusetts" % c["massachusetts"])
    if c["databases"]:
        bits.append("<b>%d</b> databases" % c["databases"])
    return ('<article class="card" data-subject="%s"><h3><a href="/resources/%s/">%s</a></h3>'
            '<p>%s</p><div class="tally">%s</div></article>'
            % (D.esc(s["subject"]), s["slug"], D.esc(s["subject"]),
               D.esc(P.SUBJECTS.get(s["subject"], "")),
               "".join("<span>%s</span>" % b for b in bits)))


def service(x):
    renew = ('<p class="renew">%s</p>' % D.esc(x["renew"])) if x.get("renew") else ""
    return ('<article><h3><a href="%s" rel="noopener">%s</a></h3><p>%s</p>%s</article>'
            % (D.esc(x["url"]), D.esc(x["title"]), D.esc(x["note"]), renew))


def render():
    dbs = D.databases()
    subs = D.subjects()
    cm = D.course_map()
    svc = D.services()
    cohorts = D.cohorts()
    ver = D.verified("databases")

    acc_counts = {}
    for x in dbs:
        acc_counts[x["access"]] = acc_counts.get(x["access"], 0) + 1
    db_subjects = {}
    for x in dbs:
        for s in x["subjects"]:
            db_subjects[s] = db_subjects.get(s, 0) + 1

    acc_chips = "".join(
        '<button class="chip" data-f="access" data-v="%s" aria-pressed="false">%s'
        '<span class="n">%d</span></button>' % (k, D.esc(P.ACCESS[k][0]), v)
        for k, v in sorted(acc_counts.items(), key=lambda kv: -kv[1]))
    sub_chips = "".join(
        '<button class="chip" data-f="subject" data-v="%s" aria-pressed="false">%s'
        '<span class="n">%d</span></button>' % (D.esc(k), D.esc(k), v)
        for k, v in sorted(db_subjects.items()))

    day = [c for c in cohorts if c["division"] == "day"]
    eve = [c for c in cohorts if c["division"] == "evening"]
    other = [c for c in cohorts if c["division"] not in ("day", "evening")]

    def opts(group):
        return "".join(
            '<button class="chip" data-cohort="%s" aria-pressed="false">%s</button>'
            % (c["cohort"], c["cohort"]) for c in group)

    # Upper-level students have no section, so they pick an area of focus and
    # get the subjects behind it, from the curated crosswalk map.
    # Two goals that are not Suffolk areas of focus go first. Bar prep pulls the
    # 1L subjects back in, because the bar tests them whatever year you are in.
    focus_subjects = dict(GOALS, **D.load("crosswalk")["focus_subjects"])
    focus_chips = "".join(
        '<button class="chip" data-focus="%s" aria-pressed="false">%s</button>'
        % (D.esc(k), D.esc(k)) for k in focus_subjects)

    total_sa = sum(len(x["items"]) for x in D.studyaids().values())
    total_tre = sum(len(x["items"]) for x in D.treatises().values())

    body = CSS + f"""
<section class="tight" style="padding-bottom:var(--s6)">
  <div class="wrap rail initial" data-initial="R">
    <p class="rail-label">Resources</p>
    <div>
      <p class="eyebrow">What you already have</p>
      <h1 class="display">Everything Suffolk already pays for on your behalf</h1>
      <p class="lede">{len(dbs)} databases, {total_sa} study aids across
      {len(subs)} subjects, {total_tre} treatises, and the parts of the building
      most people find in third year.</p>
      <p class="stampline">Verified {D.esc(ver)} &middot; every item below links to its source</p>
    </div>
  </div>
</section>

<section class="wrap" style="padding-block:0">
  <div class="zindex">
    <a href="#coursework"><b>{len(subs)}</b>Coursework<span>study aids by class</span></a>
    <a href="#research"><b>{len(dbs)}</b>Research<span>databases Moakley licenses</span></a>
    <a href="#building"><b>{len(svc['items'])}</b>The building<span>money, software, space</span></a>
  </div>
</section>

<section class="wrap pickwrap">
  <div class="picker" id="picker">
    <h2>{D.esc(P.SECTION_COPY['ask'])}</h2>
    <p>{D.esc(P.SECTION_COPY['why'])}</p>
    <div class="grp"><p class="glabel">Year</p>
      <div class="opts">
        <button class="chip" data-year="1L" aria-pressed="false">1L</button>
        <button class="chip" data-year="upper" aria-pressed="false">2L, 3L or 4L evening</button>
      </div></div>
    <div class="branch" id="branch-1L" hidden>
      <div class="grp"><p class="glabel">{D.esc(P.SECTION_COPY['day'])}</p>
        <div class="opts">{opts(day)}</div></div>
      <div class="grp"><p class="glabel">{D.esc(P.SECTION_COPY['evening'])}</p>
        <div class="opts">{opts(eve)}</div></div>
      <div class="grp"><p class="glabel">{D.esc(P.SECTION_COPY['other'])}</p>
        <div class="opts">{opts(other)}</div></div>
    </div>
    <div class="branch" id="branch-upper" hidden>
      <div class="grp"><p class="glabel">What are you working toward</p>
        <div class="opts">{focus_chips}</div></div>
    </div>
    <div class="mine-out" id="mine-out" hidden></div>
    <p class="stampline">{D.esc(P.SECTION_COPY['stored'])}</p>
  </div>
</section>

<section class="wrap zone" id="coursework">
  <h2>{D.esc(P.ZONES['coursework']['title'])}</h2>
  <p class="lede">{D.esc(P.ZONES['coursework']['lede'])}</p>
  <p class="note">{D.esc(P.ZONES['coursework']['note'])}</p>
  <div class="cards" id="subject-cards">{"".join(subject_card(s) for s in subs)}</div>
</section>

<section class="wrap zone" id="research">
  <h2>{D.esc(P.ZONES['research']['title'])}</h2>
  <p class="lede">{D.esc(P.ZONES['research']['lede'])}</p>
  <p class="note">{D.esc(P.ZONES['research']['note'])}</p>
  <div class="filters" id="db-filters">
    <div class="frow"><span class="flabel">Access</span>{acc_chips}</div>
    <div class="frow"><span class="flabel">Subject</span>{sub_chips}</div>
  </div>
  <p class="count" id="db-count">Showing <b>{len(dbs)}</b> of {len(dbs)}</p>
  <div class="rows" id="db-rows">{"".join(db_row(x) for x in dbs)}</div>
</section>

<section class="wrap zone" id="building">
  <h2>{D.esc(P.ZONES['building']['title'])}</h2>
  <p class="lede">{D.esc(P.ZONES['building']['lede'])}</p>
  <p class="note">{D.esc(P.ZONES['building']['note'])}</p>
  <div class="svc">{"".join(service(x) for x in svc['items'])}</div>
  <div class="absent">
    <p class="eyebrow">What Suffolk does not have</p>
    <ul>{"".join('<li><b>%s.</b> %s</li>' % (D.esc(a['title']), D.esc(a['note']))
                 for a in svc['absent'])}</ul>
  </div>
</section>
"""
    # The picker highlights subject cards, so cohort course titles are mapped
    # through the crosswalk first: Legal Practice Skills is a course, its
    # resources live under Legal Writing.
    def to_subjects(titles):
        out = []
        for t in titles:
            for sub in cm.get(t, {}).get("subjects", []) or []:
                if sub not in out:
                    out.append(sub)
        return out

    seq = {c["cohort"]: {"fall": to_subjects(c["fall"]),
                         "spring": to_subjects(c["spring"]),
                         "courses": {"fall": c["fall"], "spring": c["spring"]}}
           for c in cohorts}
    extra = ("<script>window.LITSA_SECTIONS=%s;window.LITSA_FOCUS=%s;window.LITSA_FOCUS_NOTE=%s;</script>"
             % (json.dumps(seq, separators=(",", ":")),
                json.dumps(focus_subjects, separators=(",", ":")),
                json.dumps(GOAL_NOTES, separators=(",", ":"))))
    return sh.page("Resources — LITSA",
                   "Every database, study aid and service Suffolk Law already pays for, "
                   "organized by the class you are taking and by how hard it is to get in.",
                   "/resources/", body, extra=extra, reference=True,
                   assistant_seed="What resources does Suffolk have for my classes?")

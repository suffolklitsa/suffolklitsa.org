"""The crosswalk: course -> resources.

Three vocabularies have to meet. The registrar tags courses with 19 Areas of
Focus. The Study Aids guide has 23 subjects. The Treatises guide has 21. The
A-Z database list has its own 28, which mix practice area with research task
with format. None of them share names, so the join is explicit and its coverage
is reported rather than assumed.
"""
from __future__ import annotations

import datetime
import json
import os

from common import CONTENT, slug, write

TODAY = datetime.date.today().isoformat()

# A course subject, as a student names it, mapped onto each guide's vocabulary.
# Left side is our label; the tuples are (study aids subject, treatises subject).
SUBJECTS = {
    "Administrative Law":            ("Administrative Law", "Administrative Law"),
    "Admiralty":                     (None, "Admiralty Law"),
    "Bankruptcy":                    (None, "Bankruptcy Law"),
    "Business Entity Fundamentals":  ("Business Entity Fundamentals", "Business Entity Fundamentals"),
    "Civil Procedure":               ("Civil Procedure", "Civil Practice & Procedure"),
    "Constitutional Law":            ("Constitutional Law", "Constitutional Law"),
    "Construction Law":              (None, "Construction Law"),
    "Contracts":                     ("Contracts", "Contracts"),
    "Criminal Law":                  ("Criminal Law", "Criminal Law & Procedure"),
    "Criminal Procedure":            ("Criminal Procedure", "Criminal Law & Procedure"),
    "Employment Law":                ("Employment Law", "Employment Law"),
    "Environmental Law":             ("Environmental Law", None),
    "Evidence":                      ("Evidence", "Evidence"),
    "Family Law":                    ("Family Law", None),
    "Immigration Law":               ("Immigration Law", "Immigration Law"),
    "Interviewing & Counseling":     ("Interviewing & Counseling", "Interviewing & Counseling"),
    "Law & Economics":               (None, "Law & Economics"),
    "Legal Writing":                 ("Legal Writing", None),
    "Professional Responsibility":   ("Professional Responsibility",
                                      "Professional Responsibility & Development"),
    "Property":                      ("Property", "Property"),
    "Reproductive Justice":          (None, "Reproductive Justice"),
    "Taxation":                      ("Taxation", "Taxation"),
    "Torts":                         ("Torts", "Torts"),
    "Trademarks":                    ("Trademarks", None),
    "Trial Advocacy":                ("Trial Advocacy", None),
    "Trusts & Estates":              ("Trusts & Estates", "Trusts & Estates"),
    "International Investment Law":  (None, "International Investment Law"),
    "Bar Exam":                      ("Bar Exam", None),
    "Exam Prep":                     ("General Exam Prep", None),
}

# Registrar Area of Focus -> our subjects, and -> database subject labels.
FOCUS = {
    "Bankruptcy":                     (["Bankruptcy"], ["Business"]),
    "Civil Litigation":               (["Civil Procedure", "Evidence", "Trial Advocacy"],
                                       ["Case Research", "Trial Courts"]),
    "Corporate Finance and Business": (["Business Entity Fundamentals", "Taxation"],
                                       ["Business", "Tax & Accounting"]),
    "Criminal":                       (["Criminal Law", "Criminal Procedure"], ["Criminal Law"]),
    "Dispute Resolution":             (["Interviewing & Counseling"], ["Trade & Arbitration"]),
    "Diversity and Social Justice":   (["Reproductive Justice"],
                                       ["Indigenous Issues", "Human Rights"]),
    "Environmental and Energy":       (["Environmental Law"], ["Environmental Law"]),
    "Health and Biomedical":          ([], ["Health Law", "Psychology"]),
    "Human Rights":                   ([], ["Human Rights", "International Law"]),
    "Immigration":                    (["Immigration Law"], ["International Law"]),
    "Intellectual Property":          (["Trademarks"], ["Intellectual Property"]),
    "International":                  (["International Investment Law"],
                                       ["International Law", "Trade & Arbitration"]),
    "Juvenile and Family":            (["Family Law"], ["Landlord & Tenant"]),
    "Labor and Employment":           (["Employment Law"], ["Business"]),
    "Patent Law":                     ([], ["Intellectual Property"]),
    "Personal Injury":                (["Torts"], ["Case Research"]),
    "Public Service":                 ([], ["Housing", "Federal Documents"]),
    "Real Estate and Land Use":       (["Property"], ["Land Use & Zoning", "Housing"]),
    "Taxation":                       (["Taxation"], ["Tax & Accounting"]),
}


def load(n):
    return json.load(open(os.path.join(CONTENT, n), encoding="utf-8"))


def main():
    sa = {s["subject"]: s for s in load("studyaids.json")["subjects"]}
    tre = {s["subject"]: s for s in load("treatises.json")["subjects"]}
    dbs = load("databases.json")["items"]
    courses = load("courses.json")["items"]

    # Validate every mapping target actually exists in the harvested data.
    problems = []
    for name, (s, t) in SUBJECTS.items():
        if s and s not in sa:
            problems.append("study aids subject missing: %r (for %s)" % (s, name))
        if t and t not in tre:
            problems.append("treatises subject missing: %r (for %s)" % (t, name))
    db_subjects = {x for d in dbs for x in d["subjects"]}
    for area, (subs, dsubs) in FOCUS.items():
        for x in subs:
            if x not in SUBJECTS:
                problems.append("focus %s -> unknown subject %r" % (area, x))
        for x in dsubs:
            if x not in db_subjects:
                problems.append("focus %s -> unknown db subject %r" % (area, x))
    for p in problems:
        print("  !! " + p)

    # Build the subject index: everything we can offer for one subject.
    subjects = []
    for name, (s, t) in sorted(SUBJECTS.items()):
        sa_items = sa[s]["items"] if s else []
        tre_items = tre[t]["items"] if t else []
        db_hits = sorted(
            {d["title"] for d in dbs
             for a, (subs, dsubs) in FOCUS.items()
             if name in subs and set(d["subjects"]) & set(dsubs)})
        subjects.append({
            "subject": name, "slug": slug(name),
            "studyaids_subject": s, "treatises_subject": t,
            "counts": {"studyaids": len(sa_items), "treatises": len(tre_items),
                       "massachusetts": sum(1 for i in tre_items if i["kind"] == "massachusetts"),
                       "databases": len(db_hits)},
            "databases": db_hits,
        })

    # Course -> subject. Direct title match first, then alias, then Area of Focus.
    # A few required courses are named for the skill rather than the subject its
    # resources are filed under.
    ALIAS = {
        "legal practice skills": "Legal Writing",
        "modern lps: legal innovation & technology": "Legal Writing",
        "transactional skills": "Contracts",
        "business organizations": "Business Entity Fundamentals",
        "wills, trusts and estates": "Trusts & Estates",
        "professional responsibility": "Professional Responsibility",
        "criminal procedure": "Criminal Procedure",
        "constitutional law": "Constitutional Law",
    }
    by_title, unmapped = {}, set()
    lower = {k.lower(): k for k in SUBJECTS}
    lower.update({k: v for k, v in ALIAS.items()})
    for c in courses:
        bt = c["base_title"]
        if bt in by_title:
            continue
        hit = lower.get(bt.lower())
        if not hit:
            hit = ALIAS.get(bt.lower())
        if not hit:
            for k in SUBJECTS:
                if bt.lower().startswith(k.lower()) or k.lower() in bt.lower():
                    hit = k
                    break
        subs = [hit] if hit else []
        for f in c["focus"]:
            subs += FOCUS.get(f["area"], ([], []))[0]
        subs = sorted(set(subs))
        # Even a seminar with no commercial study aid usually has databases,
        # routed through the Area of Focus the registrar already assigned.
        dsubs = set()
        for f in c["focus"]:
            dsubs.update(FOCUS.get(f["area"], ([], []))[1])
        dbnames = sorted({d["title"] for d in dbs if set(d["subjects"]) & dsubs})
        if not subs and not dbnames:
            unmapped.add(bt)
        by_title[bt] = {"title": bt, "slug": c["slug"], "subjects": subs,
                        # The subject the title itself names, separate from the
                        # wider set reached through an Area of Focus.
                        "primary": hit,
                        "databases": dbnames, "direct": bool(hit),
                        "areas": sorted({f["area"] for f in c["focus"]})}

    n = len(by_title)
    with_subj = sum(1 for v in by_title.values() if v["subjects"])
    with_db = sum(1 for v in by_title.values() if v["databases"])
    any_res = sum(1 for v in by_title.values() if v["subjects"] or v["databases"])
    print("  subjects indexed:        %d" % len(subjects))
    print("  courses with study aids: %3d of %d  (%.0f%%)" % (with_subj, n, 100.0 * with_subj / n))
    print("  courses with databases:  %3d of %d  (%.0f%%)" % (with_db, n, 100.0 * with_db / n))
    print("  courses with anything:   %3d of %d  (%.0f%%)" % (any_res, n, 100.0 * any_res / n))
    print("  direct title matches:    %3d" % sum(1 for v in by_title.values() if v["direct"]))
    print("  no resource at all:      %3d  (seminars and electives with no guide subject)"
          % len(unmapped))

    write("crosswalk.json", {
        "verified": TODAY,
        "problems": problems,
        "subjects": subjects,
        "courses": [by_title[k] for k in sorted(by_title)],
        "unmapped_courses": sorted(unmapped),
        "focus_areas": sorted(FOCUS),
        # The curated mapping, not a union over tagged courses. Unioning
        # pulls a course's every subject into every area it touches, which
        # turned "Criminal" into thirteen subjects.
        "focus_subjects": {k: v[0] for k, v in sorted(FOCUS.items()) if v[0]},
    })


if __name__ == "__main__":
    main()

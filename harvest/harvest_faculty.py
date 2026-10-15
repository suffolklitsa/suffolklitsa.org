"""Faculty, joined to what they actually teach.

The adjunct roster is the practitioner layer - 177 people, most teaching a single
section. Their Suffolk profiles carry degrees and courses but not their day jobs,
so "who teaches Immigration here" is answerable now and "who are they
professionally" is a separate enrichment pass.
"""
from __future__ import annotations

import datetime
import difflib
import json
import os
import re

from common import CONTENT, fetch, slug, text, write

TODAY = datetime.date.today().isoformat()
ADJ = "https://www.suffolk.edu/law/faculty-research/faculty/adjunct-faculty"
DIR = "https://www.suffolk.edu/law/faculty-research/faculty/faculty-directory"
CORPUS = "/srv/dev/suffolk-chatbot/data/current_sources"


def load(name):
    p = os.path.join(CORPUS, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []


def main():
    adj = load("law-adjunct-faculty.json")
    full = load("law-faculty-profiles.json") or load("law-faculty-directory.json")
    people = {}
    for a in adj:
        people[a["name"].strip()] = {
            "name": a["name"].strip(), "slug": slug(a["name"]),
            "role": "adjunct", "position": None,
            "degrees": text(a.get("details", "")) or None,
            "profile_url": a.get("profile_url"), "bio": None}
    for f in full:
        n = f["name"].strip()
        people[n] = {"name": n, "slug": slug(n), "role": "faculty",
                     "position": f.get("position"),
                     "degrees": None, "profile_url": f.get("profile_url"),
                     "bio": (f.get("biography") or "")[:600] or None}

    courses = json.load(open(os.path.join(CONTENT, "courses.json"), encoding="utf-8"))["items"]
    for p in people.values():
        p["teaches"], p["areas"], p["concentrations"] = [], set(), set()
    unmatched = set()
    for c in courses:
        for i in c["instructors"]:
            i = i.strip()
            if i not in people:
                # Rosters print "Kevin C. Adam"; the catalog prints "Kevin Adam".
                near = difflib.get_close_matches(i, list(people), 1, 0.80)
                if near and near[0].split()[-1] == i.split()[-1]:
                    i = near[0]
            if i not in people:
                unmatched.add(i)
                people[i] = {"name": i, "slug": slug(i), "role": "unlisted",
                             "position": None, "degrees": None,
                             "profile_url": None, "bio": None,
                             "teaches": [], "areas": set(), "concentrations": set()}
            p = people[i]
            if c["base_title"] not in [t["title"] for t in p["teaches"]]:
                p["teaches"].append({"title": c["base_title"], "slug": c["slug"],
                                     "term": c["term"]})
            p["areas"].update(f["area"] for f in c["focus"])
            p["concentrations"].update(c["concentrations"])

    out = []
    for p in sorted(people.values(), key=lambda x: x["name"].split()[-1]):
        p["areas"] = sorted(p["areas"])
        p["concentrations"] = sorted(p["concentrations"])
        p["teaching_now"] = bool(p["teaches"])
        out.append(p)

    teaching = [p for p in out if p["teaching_now"]]
    print("  people: %d  (teaching 2026-27: %d, adjunct %d, faculty %d)"
          % (len(out), len(teaching),
             sum(1 for p in out if p["role"] == "adjunct"),
             sum(1 for p in out if p["role"] == "faculty")))
    print("  in course data but not on either roster: %d" % len(unmatched))
    write("faculty.json", {"verified": TODAY, "sources": [ADJ, DIR],
                           "note": ("Suffolk adjunct profiles list degrees and courses but "
                                    "not current employer, so practice affiliation is not "
                                    "represented here."),
                           "items": out})


if __name__ == "__main__":
    main()

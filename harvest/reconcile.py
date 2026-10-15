"""Reconcile each concentration's published course list against the live catalog.

Concentration pages list what counts. The catalog lists what is actually running
in 2026-27. The gap between them is the most useful thing we can tell a student
planning a schedule, and nobody publishes it - a requirement that is Spring-only,
or not offered at all this year, is a trap you only discover late.
"""
from __future__ import annotations

import datetime
import difflib
import json
import os
import re

from common import CONTENT, write

TODAY = datetime.date.today().isoformat()


def norm(t: str) -> str:
    t = t.lower()
    t = re.sub(r"\b(hyb|hjd|web|apo)\b", "", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    t = re.sub(r"\b(i|ii|iii|1|2|3)\b", "", t)
    return " ".join(t.split())


def main():
    conc = json.load(open(os.path.join(CONTENT, "concentrations.json"), encoding="utf-8"))
    courses = json.load(open(os.path.join(CONTENT, "courses.json"), encoding="utf-8"))["items"]

    live = {}
    for c in courses:
        live.setdefault(norm(c["base_title"]), []).append(c)
    keys = list(live)

    summary = []
    for c in conc["items"]:
        offered, missing = [], []
        for course in c["courses"]:
            k = norm(course["title"])
            hit = live.get(k)
            if not hit:
                near = difflib.get_close_matches(k, keys, 1, 0.88)
                hit = live.get(near[0]) if near else None
            if hit:
                terms = sorted({("fall" if "Fall" in h["term"] else "spring") for h in hit})
                course["offered"] = terms
                course["instructors"] = sorted({i for h in hit for i in h["instructors"]})
                offered.append(course)
            else:
                course["offered"] = []
                course["instructors"] = []
                missing.append(course)
        fall_only = [x for x in offered if x["offered"] == ["fall"]]
        spring_only = [x for x in offered if x["offered"] == ["spring"]]
        c["reconciliation"] = {
            "listed": len(c["courses"]),
            "offered_2026_27": len(offered),
            "not_offered_2026_27": len(missing),
            "fall_only": [x["title"] for x in fall_only],
            "spring_only": [x["title"] for x in spring_only],
            "missing": [x["title"] for x in missing],
        }
        summary.append((c["name"], len(c["courses"]), len(offered), len(missing),
                        len(fall_only), len(spring_only)))

    print("  %-34s %5s %8s %8s %6s %8s" % ("concentration", "list", "offered", "absent",
                                           "fall", "spring"))
    for n, l, o, m, f, s in summary:
        print("  %-34s %5d %8d %8d %6d %8d" % (n[:34], l, o, m, f, s))

    conc["reconciled"] = TODAY
    conc["reconciliation_note"] = (
        "Courses listed by a concentration but absent from the 2026-27 catalog may be "
        "on a multi-year rotation, renamed, or discontinued. Verify with Academic Services.")
    write("concentrations.json", conc)


if __name__ == "__main__":
    main()

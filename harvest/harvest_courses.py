"""Harvest the Suffolk Law course catalog and the 1L section sequences.

The registrar tags every section with Areas of Focus, concentration membership,
bar-course status and requirement satisfaction. Those tags are the join key
between "the course you are registered for" and "the resources for it" - we do
not have to invent the mapping, only connect two things the school already
maintains separately.
"""
from __future__ import annotations

import datetime
import re

from common import fetch, slug, text, write

TODAY = datetime.date.today().isoformat()
SRC = "https://law2.suffolk.edu/academic/courses/law_courses.cfm"
PUBLIC = "https://www.suffolk.edu/law/academics-clinics/academic-resources/law-course-offerings"

# Section suffixes carry the division. 1A-1E are day cohorts, 4A/5A evening,
# APO the accelerated program, HJD hybrid, WEB fully online.
DIVISION = {"1A": "day", "1B": "day", "1C": "day", "1D": "day", "1E": "day",
            "4A": "evening", "5A": "evening", "APO": "accelerated",
            "HJD": "hybrid", "WEB": "online"}
SECTION_RE = re.compile(r"\s(1[A-E]|4A|5A|APO|HJD|WEB)$")


def cells(row: str):
    return [c for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]


def tag_kind(tag: str):
    """Split the registrar's flat tag list into the axes it actually encodes."""
    t = tag.replace("Law - ", "").replace("Law Areas of Focus - ", "")
    if "Area of Focus" in tag or "Areas of Focus" in tag:
        a = re.sub(r".*Area[s]? of Focus[ -]*", "", tag)
        level = "core" if a.startswith("Core") else (
            "recommended" if a.startswith("Recommended") else "listed")
        name = re.sub(r"^(Core|Recommended|Areas of Focus Core)\s*", "", a).strip()
        name = {"Bankrupt": "Bankruptcy",
                "Juvenile and Family Law": "Juvenile and Family",
                "Environmental and Energy Law": "Environmental and Energy",
                "Labor and Employment Law": "Labor and Employment",
                "Core Corporate Finance and Business": "Corporate Finance and Business",
                }.get(name, name)
        return ("focus", name, level)
    if "Concentration" in tag:
        return ("concentration", re.sub(r"\s*Concentration.*$", "", t).strip(), "")
    return ("flag", t.strip().rstrip("."), "")


def main():
    html = fetch(SRC, "law_courses")
    rows = re.findall(r"<tr.*?</tr>", html, re.S)
    out = []
    for r in rows:
        c = cells(r)
        if len(c) < 12:
            continue
        head = text(c[0])
        m = re.search(r"^(.*?)\s*LAW\s+([\w-]+)\s*$", head)
        if not m:
            continue
        title, section = m.group(1).strip(), m.group(2)
        credits = text(c[4]).replace(" credits", "").replace(" credit", "")
        # Tags are <br />-delimited, not comma-delimited: "Race, Equity and Law"
        # is a single tag whose name contains a comma.
        tags = [text(t) for t in re.split(r"<br\s*/?>", c[9])]
        tags = [t for t in tags if t and t != "No Tags"]
        focus, conc, flags = [], [], []
        for t in tags:
            kind, name, level = tag_kind(t)
            if kind == "focus":
                focus.append({"area": name, "level": level})
            elif kind == "concentration":
                conc.append(name)
            else:
                flags.append(name)
        sm = SECTION_RE.search(title)
        base = SECTION_RE.sub("", title).strip()
        out.append({
            "title": title, "base_title": base, "slug": slug(base),
            "section": section, "cohort": sm.group(1) if sm else None,
            "division": DIVISION.get(sm.group(1)) if sm else None,
            "term": text(c[1]), "status": text(c[2]),
            "meeting": text(c[3]), "credits": float(credits) if credits.replace(".", "").isdigit() else None,
            "delivery": text(c[5]),
            "prerequisites": text(c[6]), "instructors": [i.strip() for i in re.split(r"[|,]", text(c[7])) if i.strip()],
            "description": text(c[8]),
            "focus": focus, "concentrations": conc, "flags": flags,
        })
    print("  sections: %d   unique titles: %d" % (len(out), len({x['base_title'] for x in out})))
    write("courses.json", {"source": PUBLIC, "fetched_from": SRC,
                           "verified": TODAY, "items": out})

    # 1L sequences, keyed by cohort. Five day cohorts run three different orders.
    seq = {}
    for x in out:
        if "First Year" not in x["flags"] or not x["cohort"]:
            continue
        term = "fall" if "Fall" in x["term"] else "spring"
        seq.setdefault(x["cohort"], {"cohort": x["cohort"],
                                     "division": x["division"],
                                     "fall": [], "spring": []})
        if x["base_title"] not in seq[x["cohort"]][term]:
            seq[x["cohort"]][term].append(x["base_title"])
    for v in seq.values():
        v["fall"].sort()
        v["spring"].sort()
    print("  1L cohorts: %s" % ", ".join(sorted(seq)))
    write("sections.json", {"verified": TODAY, "source": PUBLIC,
                            "cohorts": [seq[k] for k in sorted(seq)]})


if __name__ == "__main__":
    main()

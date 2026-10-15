"""Harvest the two by-subject LibGuides: Study Aids & Exam Prep, and Treatises.

These are the doctrinal spine — the A-Z database list has no Contracts, Torts,
Civ Pro or Con Law subject at all, because databases are not how anyone studies
a 1L course. Study aids and treatises are.
"""
from __future__ import annotations

import datetime
import re

from common import boxes, fetch, slug, text, write, access_of

TODAY = datetime.date.today().isoformat()

SA_BASE = "https://lawguides.suffolk.edu/studyaids/"
# "Negotiation" appears in the guide's own tab bar but the page 404s (reported).
SA = [("generalexamprep", "General Exam Prep"), ("barprep", "Bar Exam"),
      ("administrative_law", "Administrative Law"),
      ("business_entity_fundamentals", "Business Entity Fundamentals"),
      ("civilprocedure", "Civil Procedure"), ("constitutionallaw", "Constitutional Law"),
      ("contracts", "Contracts"), ("criminal", "Criminal Law"),
      ("criminalprocedure", "Criminal Procedure"), ("employment_law", "Employment Law"),
      ("environmental_law", "Environmental Law"), ("evidence", "Evidence"),
      ("family_law", "Family Law"), ("immigration_law", "Immigration Law"),
      ("interviewing_and_counseling", "Interviewing & Counseling"),
      ("legalwriting", "Legal Writing"),
      ("professionalresponsibility", "Professional Responsibility"),
      ("property", "Property"), ("Taxation", "Taxation"), ("torts", "Torts"),
      ("trademarks", "Trademarks"), ("trial_advocacy", "Trial Advocacy"),
      ("trusts_and_estates", "Trusts & Estates")]

TRE_HOME = "https://lawguides.suffolk.edu/treatises"


def kind_of(box: str) -> str:
    """Normalise the guides' box headings into one student-facing vocabulary."""
    b = box.lower()
    if "audio" in b or "video" in b or "listen" in b:
        return "audio"
    if "cali" in b:
        return "cali"
    if "exam" in b or "practice" in b and "materials" not in b:
        return "practice"
    if "massachusetts" in b:
        return "massachusetts"
    if "introductory" in b:
        return "intro"
    if "in-depth" in b or "in depth" in b:
        return "depth"
    if "practical" in b:
        return "practical"
    if "review" in b or "outline" in b or "checklist" in b:
        return "outline"
    return "other"


def harvest(base, entries, guide, url_of):
    out = []
    for sl, name in entries:
        html = fetch(url_of(sl), guide + "_" + sl)
        items = []
        for box, links in boxes(html):
            k = kind_of(box)
            for label, u in links:
                if "/studyaids/" in u or "/treatises/" in u:
                    continue
                items.append({"title": label, "url": u, "kind": k,
                              "box": box, "access": access_of(u)})
        seen, uniq = set(), []
        for it in items:
            if it["url"] in seen:
                continue
            seen.add(it["url"])
            uniq.append(it)
        out.append({"subject": name, "slug": slug(name), "source": url_of(sl),
                    "verified": TODAY, "items": uniq})
        print("    %-30s %3d" % (name, len(uniq)))
    return out


def main():
    print("study aids:")
    sa = harvest(SA_BASE, SA, "sa", lambda s: SA_BASE + s)
    write("studyaids.json", {"source_guide": SA_BASE, "verified": TODAY, "subjects": sa})

    print("treatises:")
    home = fetch(TRE_HOME, "tre_home")
    nav = re.findall(r"s-lg-guide-tabs.*?</ul>", home, re.S)[0]
    tabs = []
    for u, a in re.findall(r"href=\"([^\"]+)\"[^>]*>(.*?)</a>", nav, re.S):
        name = text(a)
        if not name or name.lower() == "home":
            continue
        tabs.append((u.replace("&amp;", "&"), name))
    urls = dict((slug(n), u) for u, n in tabs)
    tre = harvest(TRE_HOME, [(slug(n), n) for _, n in tabs], "tre",
                  lambda s: urls[s])
    write("treatises.json", {"source_guide": TRE_HOME, "verified": TODAY, "subjects": tre})


if __name__ == "__main__":
    main()

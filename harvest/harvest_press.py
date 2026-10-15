#!/usr/bin/env python3
"""Press: coverage of Suffolk's legal-technology work, and our own writing.

Curated rather than scraped, deliberately. Suffolk's newsroom and the LIT Lab
blog are both JavaScript shells with no feed, and coverage arrives a few times
a year. A scraper against those would break quietly and tell us nothing; a
list of twenty verified links does not break at all.

What IS automated is the checking. Every run re-fetches each URL and compares
the page title, because suffolk.edu answers 200 with a 404 body, so a status
code proves nothing. A link that stops resolving is marked dead in the JSON
and drops off the page on the next build.

Adding an item is one entry in SOURCES below.

    python3 harvest/harvest_press.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(os.path.dirname(HERE), "content")
OUT = os.path.join(CONTENT, "press.json")
UA = "LITSA-press-check/1.0 (suffolklitsa.org)"

# kind: "coverage" = someone wrote about us; "ours" = we wrote it.
# expect: a distinctive string that must appear in the page <title>. This is
# the whole verification, because a status code is not evidence here.
SOURCES = [
    dict(kind="coverage", date="2026-08-05", outlet="National Jurist",
         title="Law schools preparing lawyers for the AI era",
         note="LITSA's build competition is the lead photograph, captioned to "
              "the organization by name.",
         url="https://nationaljurist.com/american-university-and-case-western-"
             "reserve-lead-the-top-programs-preparing-lawyers-for-the-ai-era/",
         expect="AI era"),
    dict(kind="ours", date="2026-04-09", outlet="Suffolk LIT Lab",
         title="What happens when law students build things",
         note="Sam Darkwa and Ben Westervelt on the first build competition. "
              "Seven teams, two tracks, one evening.",
         url="https://suffolklitlab.org/what-happens-when-law-students-build-things/",
         expect="law students build things"),
    dict(kind="coverage", date="2025-10-29", outlet="Suffolk University",
         title="Amazon teams up with Suffolk for AI hackathon",
         note="The LIT Center and AWS ran a generative AI hackathon at the "
              "Seaport office.",
         url="https://www.suffolk.edu/news-features/news/2025/10/29/01/25/"
             "amazon-teams-up-with-suffolk-for-ai-hackathon",
         expect="Amazon"),
    dict(kind="coverage", date="2025-10-16", outlet="Suffolk University",
         title="Named among the most innovative law schools in America",
         note="preLaw's annual list.",
         url="https://www.suffolk.edu/news-features/news/2025/10/16/18/52/"
             "most-innovative-law-schools-2025",
         expect="Innovative"),
    dict(kind="coverage", date="2025-05-31", outlet="Suffolk University",
         title="Suffolk Law partners with Hotshot for required AI course",
         note="Every first-year student now completes an AI learning track.",
         url="https://www.suffolk.edu/news-features/news/2025/05/31/21/26/"
             "suffolk-law-partners-with-hotshot-for-required-ai-course",
         expect="Hotshot"),
    dict(kind="coverage", date="2025-03-18", outlet="Suffolk University",
         title="An AI tool that helps students practice negotiation",
         note="Students negotiate against bots modeled on experienced "
              "attorneys, in text or voice.",
         url="https://www.suffolk.edu/news-features/news/2025/03/18/20/19/"
             "ai-negotiation-tool",
         expect="Negotiation"),
    dict(kind="coverage", date="2024-11-04", outlet="Suffolk University",
         title="Suffolk Law launches the first STEM-designated LL.M. in legal "
               "innovation and technology",
         note="Twenty-four credits, and the first of its kind in the country.",
         url="https://www.suffolk.edu/news-features/news/2024/11/04/20/21/"
             "lit-llm-announced",
         expect="LLM"),
    dict(kind="coverage", date="2023-11-17", outlet="Suffolk University",
         title="AI meets the justice gap at the design challenge",
         note="Law and business students prototype against access problems "
              "in a day.",
         url="https://www.suffolk.edu/news-features/news/2023/11/17/21/20/"
             "liberty-legal-design-challenge-2023",
         expect="Design Challenge"),
    dict(kind="coverage", date="2021-02-01", outlet="Suffolk University",
         title="Number one in the nation for legal technology",
         note="National Jurist's ranking, the second time Suffolk took the "
              "top spot.",
         url="https://www.suffolk.edu/news-features/news/2021/02/01/18/37/"
             "number-1-in-the-nation",
         expect="Nation"),
    dict(kind="coverage", date="2020-12-08", outlet="Suffolk University",
         title="Rising to the challenge",
         note="The design challenge run remotely through the pandemic year.",
         url="https://www.suffolk.edu/news-features/news/2020/12/08/18/25/"
             "design-challenge-article",
         expect="Challenge"),
    dict(kind="coverage", date="2020-09-02", outlet="The New York Times",
         title="Coverage of the LIT Lab's pandemic court-forms work",
         note="The eviction-moratorium reporting that put Suffolk's mobile "
              "smartforms in front of a national audience.",
         url="https://www.nytimes.com/2020/09/02/your-money/eviction-"
             "moratorium-covid.html",
         expect="Eviction"),
    dict(kind="coverage", date="2019-03-26", outlet="Suffolk University",
         title="LIT Lab named a finalist for the World Justice Challenge",
         note="International recognition for the Lab's access-to-justice work.",
         url="https://www.suffolk.edu/news-features/news/2019/03/26/19/00/"
             "suffolk-legal-innovation-and-technology-lab-named-finalist-for-"
             "world-justice-challenge",
         expect="World Justice"),
    dict(kind="coverage", date="2018-11-02", outlet="Suffolk University",
         title="Named best law school for legal technology",
         note="The first of the National Jurist top rankings.",
         url="https://www.suffolk.edu/news-features/news/2018/11/02/18/38/"
             "suffolk-named-best-law-school-for-legal-technology",
         expect="Legal Technology"),
]


# Where to keep up with this field. Short on purpose: a reading list that lists
# everything is a reading list nobody uses. Same link-checking as the press
# items, so a dead publication drops off the page rather than sitting there.
READING = [
    dict(name="LegalQuants", by="Jamie Tso and Raymond Sun",
         note="A network of lawyers who build their own tools. Invite only, "
              "with a public Substack.",
         url="https://tsojamie.substack.com/", expect="Jamie"),
    dict(name="LawSites", by="Bob Ambrogi",
         note="Twenty years of legal technology reporting, and where a lot "
              "of this field's news lands first.",
         url="https://www.lawnext.com/", expect="Law"),
    dict(name="Suffolk LIT Lab blog", by="The LIT Lab",
         note="What the Lab is shipping, written by the people shipping it. "
              "Document assembly, court forms, teaching notes.",
         url="https://suffolklitlab.org/blog/", expect="Blog"),
    dict(name="Journal of High Technology Law", by="Suffolk students",
         note="Our own journal. Student run, open to anyone, and a write-on "
              "route that carries academic credit.",
         url="https://sites.suffolk.edu/jhtl/", expect="High Technology"),
    dict(name="Legal Innovation & Technology Center", by="Suffolk Law",
         note="The Center's own page, including what the concentration and "
              "the Lab are doing this year.",
         url="https://sites.suffolk.edu/legaltech/", expect="Legal Innovation"),
]


# Some publishers answer any non-browser request with 403. That is not a dead
# link, and treating it as one would quietly drop real coverage. We keep those
# and say plainly that they were not machine-checked.
NO_ROBOTS = ("nytimes.com", "wsj.com", "bostonglobe.com", "law.com",
             "bloomberglaw.com", "reuters.com")


def title_of(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=40) as r:
        html = r.read(200_000).decode("utf-8", "replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main():
    now = datetime.now(timezone.utc)
    items, dead = [], []
    for src in SOURCES:
        rec = {k: v for k, v in src.items() if k != "expect"}
        blocked = any(h in src["url"] for h in NO_ROBOTS)
        try:
            page = title_of(src["url"])
            ok = src["expect"].lower() in page.lower()
            rec["page_title"] = page[:160]
            rec["checked"] = True
        except Exception as e:
            if blocked:
                ok, rec["checked"] = True, False
                rec["page_title"] = "publisher blocks automated checks"
            else:
                ok, rec["checked"] = False, True
                rec["page_title"] = f"fetch failed: {e}"
        rec["live"] = ok
        (items if ok else dead).append(rec)
        mark = "ok  " if ok and rec.get("checked") else (
            "skip" if ok else "DEAD")
        print(f"  {mark}  {src['outlet'][:24]:24s} {src['title'][:46]}")
        time.sleep(1)

    reading = []
    for src in READING:
        rec = {k: v for k, v in src.items() if k != "expect"}
        try:
            page = title_of(src["url"])
            rec["live"] = src["expect"].lower() in page.lower()
        except Exception:
            rec["live"] = False
        reading.append(rec)
        print(f"  {'ok  ' if rec['live'] else 'DEAD'}  reading: {src['name']}")
        time.sleep(1)

    items.sort(key=lambda x: x["date"], reverse=True)
    doc = {
        "items": items,
        "reading": [r for r in reading if r["live"]],
        "dead": dead + [r for r in reading if not r["live"]],
        "last_checked": now.strftime("%Y-%m-%d"),
        "health": {
            "ok": not dead,
            "live": len(items),
            "dead": len(dead),
            "unverified": sum(1 for i in items if not i.get("checked")),
        },
    }
    os.makedirs(CONTENT, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
    print(f"\nwrote {OUT}  live={len(items)} dead={len(dead)}")
    return 0 if not dead else 1


if __name__ == "__main__":
    sys.exit(main())

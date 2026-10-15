"""Harvest the seven Suffolk Law concentrations.

There is currently no working index of these on suffolk.edu - the page at
/law/academics-clinics/jd-program/concentrations returns HTTP 200 with the 404
body, so a student has to already know the name of the concentration they want.
Each one lives under /what-can-i-study/<area>/ with a consistent subpage layout.
"""
from __future__ import annotations

import datetime
import re

from common import fetch, slug, text, write

TODAY = datetime.date.today().isoformat()
BASE = "https://www.suffolk.edu/law/academics-clinics/what-can-i-study/"

# (key, display name, path stem, requirements subpage, credits)
# Credit totals are read off each concentration's own requirements page; Labor
# and Employment publishes a structure but no total, so it stays null.
CONC = [
    ("legal-innovation-technology", "Legal Innovation & Technology",
     "legal-innovation-technology", "enrollment-requirements", 17),
    ("intellectual-property", "Intellectual Property",
     "intellectual-property/ip-area-of-focus-and-concentration", "enrollment-and-requirements", 18),
    ("international-law", "International Law",
     "international-law", "enrollment-requirements", 18),
    ("health-biomedical-law", "Health & Biomedical Law",
     "health-biomedical-law", "enrollment-requirements", 20),
    ("business-law-financial-services", "Business Law & Financial Services",
     "business-law-financial-services", "enrollment-requirements", 21),
    ("trial-appellate-advocacy", "Trial & Appellate Advocacy",
     "trial-appellate-advocacy", "enrollment-requirements", 23),
    ("labor-employment-law", "Labor & Employment Law",
     "labor-employment-law", "enrollment-requirements", None),
]

COURSE_RE = re.compile(r"^(.*?)\s*\((\d+(?:\.\d+)?)\s*Credits?\)\s*$", re.I)


def body(html: str) -> str:
    """Content only.

    suffolk.edu renders the section navigation inside the same .page-content
    wrapper as the article, so scraping list items without dropping the sidebar
    returns the page's own menu instead of the requirements.
    """
    m = re.search(r'<div class="page-content">(.*)', html, re.S)
    b = m.group(1) if m else html
    b = re.sub(r"<(script|style|nav|footer)\b.*?</\1>", "", b, flags=re.S)
    # Drop the sidebar column and any breadcrumb/nav list wholesale.
    b = re.sub(r'<div[^>]*class="[^"]*(tier-sidebar|col-md-4)[^"]*".*?(?=<div[^>]*class="[^"]*col-md-8)',
               "", b, flags=re.S)
    b = re.sub(r'<(ul|div)[^>]*class="[^"]*(t2-nav|t3-nav|breadcrumb|subnav)[^"]*".*?</\1>',
               "", b, flags=re.S)
    return b


def bullets(html: str):
    return [text(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", html, re.S)]


def main():
    out = []
    for key, name, stem, reqpage, credits in CONC:
        req_url = BASE + stem + "/" + reqpage
        crs_url = BASE + stem + "/courses"
        req = body(fetch(req_url, "conc_%s_req" % key))
        crs = body(fetch(crs_url, "conc_%s_crs" % key))

        # Two layouts in use. Most concentrations render grouped tables whose
        # <th> is the requirement ("One (1) Evidence course:") and whose rows
        # are course + credits, with a CourseID link. LIT and Labor instead use
        # "<Title> (N Credits)" list items under <h2>/<h3> group headings.
        courses, seen = [], set()

        def add(title, credits, group, cid=None):
            t = title.strip(" .*\u00a0")
            if not t or t.lower() in seen:
                return
            seen.add(t.lower())
            courses.append({"title": t, "credits": credits,
                            "group": group, "course_id": cid})

        group = ""
        for chunk in re.split(r"(?=<(?:h2|h3|thead)\b)", crs):
            gh = re.search(r"<(?:h2|h3)[^>]*>(.*?)</(?:h2|h3)>", chunk, re.S)
            th = re.search(r"<th[^>]*>(.*?)</th>", chunk, re.S)
            if gh:
                group = text(gh.group(1))
            elif th:
                group = text(th.group(1))
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", chunk, re.S):
                tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
                if len(tds) < 2:
                    continue
                cid = re.search(r"CourseID=(\d+)", tds[0])
                cm = re.search(r"(\d+(?:\.\d+)?)", text(tds[1]))
                add(text(tds[0]), float(cm.group(1)) if cm else None, group,
                    cid.group(1) if cid else None)
            for b in re.findall(r"<li[^>]*>(.*?)</li>", chunk, re.S):
                m = COURSE_RE.match(text(b))
                if m:
                    add(m.group(1), float(m.group(2)), group)

        rtext = text(req)
        i = rtext.find("Requirements")
        # Only the list that follows the Requirements heading.
        seg = re.split(r"<(?:h2|h3|strong)[^>]*>\s*Requirements", req, flags=re.I)
        req_bullets = [b for b in bullets(seg[-1] if len(seg) > 1 else req)
                       if 25 < len(b) < 600 and not b.startswith(("Legal ", "Completion/"))]
        deadline = "October 1 (January graduates) / February 1 (May graduates)"
        out.append({
            "key": key, "name": name, "slug": slug(name),
            "credits_required": credits,
            "requirements_url": req_url, "courses_url": crs_url,
            "enroll_deadline": deadline,
            "requirement_bullets": req_bullets[:14],
            "courses": courses,
            "requirements_text": rtext[i:i + 2400] if i > 0 else rtext[:2400],
            "verified": TODAY,
        })
        print("  %-34s credits=%-5s courses=%d" % (name, credits, len(courses)))

    write("concentrations.json",
          {"source": BASE, "verified": TODAY,
           "note": ("Suffolk publishes no working index of concentrations; the "
                    "jd-program/concentrations path returns the 404 body."),
           "universal": {
               "min_credits_floor": 14,
               "gpa_in_concentration": 3.250,
               "no_grade_below": 2.000,
               "one_at_a_time": True,
               "eligible": "after completing 1L in good standing",
               "completion_form": "November 1 (January graduates) / March 1 (May graduates)",
               "distinction": "concentration thesis, or 3.50 cumulative in concentration courses",
               "rules_url": ("https://www.suffolk.edu/law/academics-clinics/student-life/"
                             "policies-rules/academic-rules-regulations"),
           },
           "items": out})


if __name__ == "__main__":
    main()

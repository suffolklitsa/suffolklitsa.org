"""The building: what a Suffolk Law student already has and mostly doesn't know.

Unlike the databases and guides, this doesn't come from one scrapeable index -
it is spread across LibAnswers FAQs, library service pages, and university pages.
Curated here with a source URL per item so every claim is checkable.
"""
from __future__ import annotations

import datetime

from common import write

TODAY = datetime.date.today().isoformat()
FAQ = "https://law.suffolk.libanswers.com/faq/"
LIB = "https://www.suffolk.edu/law/faculty-research/"

ITEMS = [
    # --- money you already have -------------------------------------------
    dict(title="Printing credits, $62.50 a semester", group="money", access="open",
         renew="Credits roll over fall to spring but are wiped at the end of the academic year.",
         url=FAQ + "430242",
         note="Free black-and-white printing credit every semester. The library itself "
              "has no printers - go across the 6th-floor hall to the IT suite. Colour "
              "and overage come off your Ram Card."),
    dict(title="The New York Times, free", group="money", access="account",
         renew="Re-register every year from your signup date.",
         url="https://www.nytimes.com/activate-access/edu-access",
         note="Full digital access on a joint Moakley and Sawyer subscription. Register "
              "with your @suffolk.edu address. The confirmation email usually lands in spam.",
         extra_url=FAQ + "427458"),
    dict(title="The Wall Street Journal, free", group="money", access="account",
         renew=None, url="https://wsj.com/Suffolk",
         note="Suffolk has its own registration URL. Sign up with your Suffolk email."),
    dict(title="The Washington Post, free", group="money", access="account",
         renew=None, url="https://www.washingtonpost.com/subscribe/signup",
         note="Available through Suffolk. The registration path is less clearly "
              "documented than the Times or the Journal - ask the research desk if it balks."),
    dict(title="Headspace, free for every Suffolk student", group="money", access="account",
         renew=None, url="https://work.headspace.com/suffolkuniversity/member-enroll",
         note="The full app subscription, enrolled through Suffolk. The library surfaces "
              "it alongside Counseling Services and Suffolk CARES.",
         extra_url="https://lawguides.suffolk.edu/academicexcellence/mentalhealth"),
    dict(title="Discounted MBTA passes", group="money", access="account", renew=None,
         url="https://www.suffolk.edu/student-life/student-services/ram-card/mbta-pass-program",
         note="Semester transit passes at a student rate through the Ram Card office."),

    # --- legal tech you already have ---------------------------------------
    dict(title="Lexis+ AI (Protege)", group="tech", access="platform", renew=None,
         url="https://lawguides.suffolk.edu/research-toolkit/lexis",
         note="Suffolk licenses it. Open it from the left sidebar of the Lexis+ homepage. "
              "Drafts, summarises, compares documents, generates deposition questions. "
              "Prompts are not used to train models and prompt history auto-deletes at 90 days."),
    dict(title="CoCounsel and Ask Practical Law AI", group="tech", access="platform", renew=None,
         url="https://lawguides.suffolk.edu/research-toolkit/westlaw",
         note="Both licensed. Use the product switcher at the top left of the Westlaw "
              "homepage. Research, document review with citation links, timeline extraction."),
    dict(title="The library's own guidance on AI fabrications", group="tech", access="open",
         renew=None, url="https://lawguides.suffolk.edu/research-toolkit/ai-fabrications",
         note="Read this before you rely on any of the above. It explains why Lexis+ AI and "
              "CoCounsel behave differently from raw ChatGPT, and carries Suffolk's actual "
              "rules on verification and confidential information."),

    # --- the building ------------------------------------------------------
    dict(title="Study rooms, 20 of them", group="building", access="account", renew=None,
         url="https://www.suffolk.edu/law/faculty-research/about-the-library/library-study-rooms",
         note="Floors 5 to 7. Book 30 minutes to 4 hours, up to 7 days ahead; the day "
              "releases at 12:01am. QR check-in on the wall is required, no earlier than 30 "
              "minutes before and no later than 30 after. Repeated no-shows suspend booking."),
    dict(title="Where you're allowed to take a Zoom call", group="building", access="open",
         renew=None, url=FAQ + "426372",
         note="The whole 6th floor except the reading room, plus the collaborative area at "
              "the top of the 7th-floor stairs. Headphones required."),
    dict(title="Free scanning", group="building", access="open", renew=None,
         url="https://lawguides.suffolk.edu/tips/keyresources",
         note="Library scanners send straight to email or cloud storage at no charge."),
    dict(title="Course reserves, 2-hour checkout", group="building", access="print", renew=None,
         url="https://library.law.suffolk.edu/search/r",
         note="Required and recommended books for your courses. Search by professor surname "
              "or course title. If yours is missing, email your syllabus to "
              "law_circulation@suffolk.edu and they will get it.",
         extra_url=FAQ + "426371"),
    dict(title="Your first two weeks of reading, scanned to Canvas", group="building",
         access="open", renew=None, url=FAQ + "437980",
         note="Some professors send the library their opening readings to scan and post, so "
              "you don't need the casebook on day one. Opt-in by professor - email "
              "law_circulation@suffolk.edu to ask about yours."),
    dict(title="Interlibrary loan", group="building", access="account", renew=None,
         url=LIB + "library-services/interlibrary-loan-request",
         note="Books, chapters and articles from other institutions. Course reserves and "
              "ebooks cannot be requested. Cost and turnaround are not published."),
    dict(title="Borrowing at seven other Boston campuses", group="building", access="account",
         renew=None, url="https://libraries.flo.org/home",
         note="Your Suffolk ID checks out circulating books at Simmons, Emerson, Lesley, "
              "Emmanuel, MassArt, Wentworth and Berklee through the Fenway Library Organization."),
    dict(title="What the library will not lend you", group="building", access="open",
         renew=None, url=FAQ + "432310",
         note="No laptops, no chargers, no cables. It does have a few USB connections, "
              "headphones and assistive reading equipment. Chargers come from IT across the hall."),
    dict(title="Research librarians", group="building", access="open", renew=None,
         url=LIB + "john-joseph-moakley-law-library",
         note="Desk staffed Monday to Thursday 10-6 and Friday 10-5. 617-573-8516, "
              "lawref@suffolk.edu, live chat, or book an appointment. The library itself is "
              "open 8am-11pm weekdays and 9am-11pm weekends."),
    dict(title="The free book shelf", group="building", access="open", renew=None,
         url=FAQ + "428731",
         note="The library doesn't take donations but keeps a shelf of free books to take."),

    # --- competitions and writing -----------------------------------------
    dict(title="iCompete Writing", group="opportunity", access="open", renew=None,
         url="https://www.suffolk.edu/law/academics-clinics/academic-resources/"
             "legal-practice-skills---lps/icompete-writing--a-compilation-of-legal-writing-competitions",
         note="One of the most comprehensive collections of law student writing competitions "
              "anywhere - over 100 entries by date and topic, prizes up to $25,000. Built and "
              "maintained by Suffolk's own LPS program and the law library."),
    dict(title="Perma.cc accounts", group="opportunity", access="account", renew=None,
         url=FAQ + "442564",
         note="Link-rot-proof permanent citations. The library issues accounts only to law "
              "review writers and faculty RAs. Write-on competitors use the placeholder "
              "[PERMALINK] instead."),
    dict(title="Past faculty exams", group="opportunity", access="account", renew=None,
         url=LIB + "library-services/selected-previous-faculty-exams",
         note="Real exams from Suffolk professors, searchable, and not the same set as what "
              "is on Canvas. Suffolk login required off campus."),
    dict(title="CLE while you're still a student", group="opportunity", access="proxy",
         renew=None, url=FAQ + "439601",
         note="MCLE OnlinePass gives you MCLE's CLE programming. Massachusetts has no "
              "mandatory CLE requirement, so this is for the material, not for credit hours."),
]

# What Suffolk does not have. Institutions never publish this, and it saves
# people hunting for something that was never there.
ABSENT = [
    dict(title="WordRake",
         note="Suffolk was the first law school in the country to give students WordRake, "
              "but the licence was not renewed for 2026-27. Library FAQ 424561 still "
              "describes the annual renewal, so it is worth knowing before you email the "
              "research desk about it."),
    dict(title="Quimbee", note="No Suffolk subscription. Zero hits across all 101 databases. "
                               "Use West Academic's study aids and CALI instead."),
    dict(title="Aspen Learning Library",
         note="No Suffolk subscription. The entire commercial study-aid spend is West Academic."),
    dict(title="Bloomberg Law",
         note="The subscription ended June 30, 2021 and the page for it now 404s. Sawyer "
              "Library does still have a Bloomberg financial terminal."),
    dict(title="BARBRI or Themis bar prep",
         note="No institutional subscription. BARBRI appears only as a sign-in provider for "
              "West Academic."),
    dict(title="Free PACER",
         note="The library states plainly that it does not provide it. Use CourtLink inside "
              "your Lexis account for federal and state dockets."),
    dict(title="E-discovery or practice-management software",
         note="No Relativity, Everlaw, Logikcull, Clio, HotDocs or Documate through the "
              "library. Legal tech at Suffolk means Lexis+ AI and CoCounsel."),
    dict(title="An institutional ChatGPT or Claude licence",
         note="Not through the library. Its own student guide tells you to make a free "
              "personal account."),
]

for it in ITEMS:
    it["verified"] = TODAY

write("services.json", {"verified": TODAY, "items": ITEMS, "absent": ABSENT})

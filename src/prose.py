# -*- coding: utf-8 -*-
"""Written copy for the resources and curriculum pages.

Kept apart from the harvested data so a re-harvest never overwrites prose, and
so the whole voice of the site can be read in one file.
"""

ZONES = {
"coursework": dict(
    title="Coursework",
    lede="Study aids, practice questions and recorded lectures, organized by the class "
         "you are taking this semester. Most of this is licensed and waiting for you.",
    note="Suffolk's entire commercial study-aid subscription is West Academic, plus CALI "
         "for interactive lessons. There is no Quimbee and no Aspen."),
"research": dict(
    title="Research",
    lede="The 101 databases Moakley licenses, described in one line each and sorted by how "
         "much stands between you and reading them.",
    note="The library's own A-Z list sorts these alphabetically and tags them by format. "
         "Knowing that a database is a periodical does not tell you when to open it."),
"building": dict(
    title="The building",
    lede="Money, software and space you already have.",
    note="Several of these lapse silently. Printing credits die at the end of the academic "
         "year, and the New York Times needs an annual renewal."),
}

# One line per subject: what the collection is actually good for here.
SUBJECTS = {
"Administrative Law": "Agency structure and judicial review, with the Massachusetts agency practice material sitting alongside it.",
"Admiralty": "A small treatise collection. Nothing in the study aid guide, so start with the hornbooks.",
"Bankruptcy": "Treatises and Massachusetts practice material. The database list runs thin here, so start with the treatises.",
"Business Entity Fundamentals": "Covered in both guides, and one of the doctrinal courses that shows up on the Massachusetts bar.",
"Civil Procedure": "Deep in both guides. Glannon and the Examples and Explanations are the ones people finish.",
"Constitutional Law": "The largest study aid collection of any subject, including ten separate audio lecture series.",
"Construction Law": "Treatises only, with a Massachusetts practice section.",
"Contracts": "Well covered, and the audio lectures suit a commute.",
"Criminal Law": "Strong throughout, and the treatises guide folds criminal law and procedure together with a substantial Massachusetts section.",
"Criminal Procedure": "Shares the treatise collection with criminal law. The study aids are separate and specific.",
"Employment Law": "Light on study aids, better on treatises, and the Labor and Employment concentration lists far more than runs in a given year.",
"Environmental Law": "Study aids and a dedicated research guide. The database collection here is one of the deeper ones.",
"Evidence": "Four Massachusetts titles in the treatises guide, including the Guide to Evidence and MCLE's pocket guide. Useful well past the exam.",
"Family Law": "Thin on paper, but the Juvenile and Family area of focus carries the most tagged courses of any area in the catalog.",
"Immigration Law": "Modest study aid coverage, better treatise coverage, and a strong clinical program behind it.",
"Interviewing & Counseling": "Small on both sides. Most of the learning here happens in the skills courses.",
"Law & Economics": "Treatises, economics literature and news. Built for seminar work rather than exams.",
"Legal Writing": "Study aids plus the LPS program's own material.",
"Professional Responsibility": "Required, tested on the MPRE, and well covered by both guides.",
"Property": "Solid throughout, with Massachusetts conveyancing material in the treatises.",
"Reproductive Justice": "A treatises collection with a long research-tips section. Recent, and actively maintained.",
"Taxation": "Study aids, treatises, Massachusetts material, and Checkpoint Edge for the research itself.",
"Torts": "The Massachusetts Tort Law Manual and MCLE's motor vehicle volume sit next to the usual study aids.",
"Trademarks": "Study aids plus the IP database collection. The concentration lists considerably more than runs each year.",
"Trial Advocacy": "Study aids and the advocacy collection, behind the biggest concentration in the school.",
"Trusts & Estates": "Present in both guides, with Massachusetts probate practice material.",
"International Investment Law": "The single largest treatise collection in the guide, at seventy-two entries.",
"Bar Exam": "Bar books, NCBE's free sample questions for every component, and the Massachusetts Law Component materials.",
"Exam Prep": "General exam technique rather than any one subject. Start here in your first October, not your first December.",
}

ACCESS = {
"open":    ("Open", "No login. Click and read."),
"proxy":   ("Suffolk login", "Routes through the library proxy. Sign in with your Suffolk account."),
"account": ("Extra step", "Needs the proxy and an account you create yourself. Two steps rather than one."),
"platform":("Westlaw or Lexis", "Inside a platform you already have. Sign in there first."),
"print":   ("On the shelf", "Print, in the library. Two-hour reserve for most study aids."),
"code":    ("Needs a code", "Free, but you need an authorization code from the research desk."),
"unknown": ("Check the page", "Access terms are not stated. Ask the research desk."),
}

CURRICULUM = dict(
    title="Curriculum",
    lede="Seven concentrations, nineteen areas of focus, and every course running this year. "
         "Suffolk publishes these one at a time, and the page that would list them together "
         "returns an error.",
    caveat="Requirements are read from each concentration's own page and reconciled against "
           "the live 2026-27 catalog. Verify anything you plan around with Academic Services "
           "before you rely on it.",
    tracking_note="The Academic Rules put completion tracking on you. Students are "
                  "responsible for ensuring they have satisfied their concentration's "
                  "requirements, and the Assistant Dean's stated obligation runs only to "
                  "verifying the form you eventually submit.",
)

CONCENTRATION_NOTES = {
"legal-innovation-technology":
    "The smallest concentration by credits, at seventeen. Its externship requirement is the "
    "most flexible in the school. It takes a credit externship, a non-credit summer placement, either "
    "LIT clinic, or a waiver if you are part-time and already working in the field. You "
    "take three of the four core courses, and two of those four run in spring only, so "
    "plan the order early.",
"intellectual-property":
    "Eighteen credits, and the only concentration with its own patent bar guidance. The "
    "course list is long and about half of it runs in any given year.",
"international-law":
    "Eighteen credits built on two core courses. Study abroad and the International "
    "Internship Program both feed it, and clinic credits count toward the electives.",
"health-biomedical-law":
    "Twenty credits, five of them core. The Health Law Clinic and the Journal of Health and "
    "Biomedical Law both sit under it.",
"business-law-financial-services":
    "Twenty-one credits, with four required core courses covering thirteen to fourteen of "
    "them and an externship or practicum on top.",
"trial-appellate-advocacy":
    "The largest concentration at twenty-three credits, and the most structured. It takes an evidence "
    "course, a pretrial course, an appellate course, an ADR course, and a clinic or trial team.",
"labor-employment-law":
    "Three core courses, two skills courses, a three-credit externship and two electives. It "
    "publishes no total credit figure, and it does not appear in the Academic Rules alongside "
    "the other six, so confirm its status before you enroll.",
}

SECTION_COPY = dict(
    ask="Where are you in the degree?",
    why="1L course order is set by your section letter, and the five day sections run "
        "three different sequences. After that it is electives, so upper-level students "
        "pick an area instead.",
    day="Day", evening="Evening", other="Accelerated, hybrid and online",
    stored="Kept in this browser. Nothing is sent anywhere and there is no account.",
)

CHATBOT = dict(
    label="Ask about any of this",
    hint="The Suffolk assistant can answer questions about these resources in plain language.",
    placeholder="Which study aids cover Civil Procedure?",
)

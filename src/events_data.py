# -*- coding: utf-8 -*-
"""Fall 2026 events, tiered.

Ours, Suffolk's, and Greater Boston's. Verified against live pages 2026-09-15; the BBA tier cross-checked
against bostonbar.org/events/?ical=1. Hand-kept for now: the Suffolk tier does not automate, because
law orgs barely post to SU Connect (4 events out of 1,200 sampled).
"""
import datetime

VERIFIED = "2026-09-15"

# tier: litsa | suffolk | boston | virtual | ai (harvested only)
EVENTS = [
    # ---- ours -----------------------------------------------------------
    dict(tier="litsa", date="2026-09-24", time="5:30–6:30pm",
         name="LITSA General Body Meeting",
         host="LITSA", venue="Faculty Dining Room, Sargent Hall 495F", cost="Free",
         note="What LITSA is running this year, and how to get involved, including "
              "the open 1L and 3L representative seats. Pizza.",
         url=None, flag="ours"),

    dict(tier="litsa", date="2026-11-04", time="6:00–8:00pm",
         name="The Law of Technology: IP, Data and AI in Practice",
         host="LITSA, IP Law Students Association, Data Privacy & Cybersecurity Law Association",
         venue="Smith Commons, Sargent Hall, 5th floor, and on Zoom", cost="Free, RSVP",
         note="A practitioner panel on how AI, privacy and IP questions show up in real client matters, "
              "opened by Prof. Stacey Lantagne and moderated by Prof. Dyane O'Leary, with Patrick J. Concannon (Nutter McClennen & Fish), "
              "Adam L. Littman (ArentFox Schiff), Christopher J. Seusing (Wood Smith Henning & Berman), "
              "Ariel Soiffer (WilmerHale) and Mark B. Solomon (Hamilton, Brook, Smith & Reynolds). Networking at 6:00, panel "
              "6:30 to 8:00, reception after. RSVP at suffolklitsa.org/rsvp.",
         url="/rsvp", flag="ours"),

    # ---- Suffolk --------------------------------------------------------
    dict(tier="suffolk", date="2026-09-02", dates=["2026-09-02", "2026-10-07", "2026-11-04", "2026-12-02"],
         time="4:00pm",
         name="Document Assembly Line workshop",
         host="Suffolk LIT Lab", venue="Virtual", cost="Free",
         note="First Wednesday of the month, all term. Open to anyone.",
         url="https://suffolklitlab.org/events/"),
    dict(tier="suffolk", date="2026-10-25", time="6:00–10:00pm",
         name="American Legal Technology Awards Gala",
         host="ALTA", venue="Suffolk Law, 120 Tremont", cost="$268.61",
         note="In our building. No student tier published. In 2025 the LIT Lab hosted a "
              "free student reception beforehand, announced around Sept 17.",
         url="https://www.lawnext.com/2026/07/american-legal-technology-awards-returns-to-celebrate-innovation-in-law-at-2026-gala-in-boston.html",
         flag="watch"),
    dict(tier="suffolk", date="2026-11-12", time="two days",
         name="New England Experiential Conference",
         host="Suffolk Law", venue="Suffolk Law", cost="Not yet published",
         note="Nov 12–13. Registration not yet live and student access is not addressed. "
              "Worth asking, it is our building.",
         url="https://www.suffolk.edu/law/about/new-england-experiential-conference"),

    # ---- Greater Boston -------------------------------------------------
    dict(tier="boston", date="2026-09-22", time="5:15pm",
         name="AI and the Changing World of M&A",
         host="Gennari Aronson LLP", venue="Workbar Needham", cost="Free",
         note="A law firm running a free AI panel. The second one starts an hour later.",
         url="https://aiweek.boston/schedule"),
    dict(tier="boston", date="2026-09-22", time="6:15pm",
         name="AI: Trends in Entrepreneurial Finance",
         host="Gennari Aronson LLP", venue="Workbar Needham", cost="Free",
         note="Back to back with the M&A panel above.",
         url="https://aiweek.boston/schedule"),
    dict(tier="boston", date="2026-09-23", time="5:30–9:00pm",
         name="Mass AI Coalition End of Summer Reception",
         host="Goodwin, WHOOP, Flagship Pioneering, Modal", venue="Boston", cost="See Luma",
         note="Goodwin co-hosts, which makes this a real networking target rather than a "
              "tech party.",
         url="https://luma.com/qkj2w666"),
    dict(tier="boston", date="2026-09-26", time="6:00–8:00pm",
         name="Human in the Loop Ping Pong Meetup",
         host="Code & Counsel", venue="SPIN Boston, Seaport", cost="Free",
         note="Legal and AI people, informal. Space very limited.",
         url="https://luma.com/nihzmk1n"),
    dict(tier="boston", date="2026-09-27", time="11:00am–2:00pm",
         name="Legal AI Community Hackathon",
         host="Code & Counsel", venue="The Foundry, Cambridge", cost="Free",
         note="Public interest. 18+. No coding required.",
         url="https://luma.com/kt5j0ocm"),
    dict(tier="boston", date="2026-09-28", time="6:00–9:00pm",
         name="When AI Gets Physical",
         host="Greenberg Traurig LLP", venue="InterContinental, 510 Atlantic", cost="Free",
         url="https://aiweek.boston/schedule/when-ai-gets-physical-navigating-the-real-world-risks-and-rewards"),
    dict(tier="boston", date="2026-09-29", time="5:30–8:00pm",
         name="JD → AI: Building What's Next",
         host="Code & Counsel + Reframe.Lawyer", venue="Democracy Brewing, 35 Temple Pl",
         cost="Free panel and happy hour",
         note="Written for attorneys, law students and legal professionals. The optional "
              "Builder Lab is name-your-own-price.",
         url="https://luma.com/j6uxbl9q", flag="pick"),
    dict(tier="boston", date="2026-09-29", time="1:00–5:00pm",
         name="AI in Massachusetts Workforce Development & Career Fair",
         host="Boston AI Week + BU Questrom", venue="Metcalf Hall, BU", cost="Free for students",
         note="Advance registration, dedicated student area.",
         url="https://aiweek.boston/ai-in-massachusetts-workforce-dev-and-career-fair-2026"),
    dict(tier="boston", date="2026-09-30", time="9:00am–12:00pm",
         name="AI Blueprint for Massachusetts",
         host="Boston AI Week", venue="Greater Boston, TBA", cost="Free",
         note="Government, industry and academia in one room on responsible AI.",
         url="https://aiweek.boston/schedule"),
    dict(tier="boston", date="2026-10-01", time="12:00–1:00pm",
         name="AI, Experts, and Evidence",
         host="Boston Bar Association", venue="BBA, 16 Beacon St", cost="Free, lunch provided",
         note="No membership gate on the registration form.",
         url="https://bostonbar.my.site.com/LightningMemberPortal/eventapi__router?event=a1YRc000004nUDx"),
    dict(tier="boston", date="2026-10-02", time="5:30–8:30pm",
         name="Boston AI Week Closing Party",
         host="Boston AI Week", venue="Island Creek Oysters Raw Bar, 99 Autumn Lane, Seaport",
         cost="Free, RSVP required",
         note="Closes Core Festival Week. Space is limited.",
         url="https://aiweek.boston/schedule/boston-ai-week-closing-party"),
    dict(tier="boston", date="2026-10-07", time="2:00–3:30pm",
         name="AI, Disability and the Future of Work",
         host="MA Commission on the Status of Persons with Disabilities",
         venue="Massachusetts State House, Room 428", cost="Free",
         url="https://aiweek.boston/schedule/ai-disability-and-the-future-of-work-2026"),
    dict(tier="boston", date="2026-10-24", time="all day",
         name="Hackachusetts", host="Mass AI Coalition", venue="Boston", cost="See Luma",
         url="https://www.massaicoalition.com/events"),
    dict(tier="boston", date="2026-10-26", time="two days",
         name="ClioCon 2026", host="Clio", venue="Hynes Convention Center", cost="$1,499+",
         note="Oct 26–27. The Access Grant gives law students a free pass and closes "
              "September 11.",
         url="https://cliocon.com/access-grant/", flag="deadline"),
    dict(tier="boston", date="2026-11-12", time="1:00–6:00pm",
         name="Boston AI Showcase", host="Mass AI Coalition, SVB, WHOOP",
         venue="Boston", cost="See Luma", url="https://luma.com/2b4inmb4"),

    # ---- virtual --------------------------------------------------------
    dict(tier="virtual", date="2026-09-29", time="12:00–1:00pm",
         name="Beyond the Prompt: How New Lawyers Can Leverage AI at Work",
         host="Boston Bar Association", venue="Zoom",
         cost="Free for BBA members, $100 otherwise",
         url="https://bostonbar.my.site.com/LightningMemberPortal/eventapi__router?event=a1YRc000004netH"),
    dict(tier="virtual", date="2026-09-10", time="time not posted",
         name="Who Will Steward Humanity's Public Data?",
         host="Harvard Library Innovation Lab", venue="Zoom", cost="Free",
         url="https://lil.law.harvard.edu/events/who-will-steward-humanity-s-public-data-collective-global-stewardship-for-the-long-horizon/"),
    dict(tier="virtual", date="2026-09-11", time="12:30pm",
         name="Frontiers in Law & Technology: AI Governance",
         host="FSU Institute of Law, Technology & Innovation", venue="Zoom",
         cost="No fee listed",
         url="https://law.fsu.edu/academics/institute-law-technology-innovation/frontiers-law-and-technology"),
    dict(tier="virtual", date="2026-09-23", time="12:00pm",
         name="Legal Tech into Self-Help & Legal Aid",
         host="IAALS, University of Denver", venue="Webinar", cost="Free",
         url="https://iaals.du.edu/events/connecting-ecosystem-integrating-legal-tech-self-help-legal-aid-systems"),
    dict(tier="virtual", date="2026-10-22", time="1:00–5:30pm",
         name="Free Speech in the Age of AI symposium",
         host="FSU / First Amendment Foundation", venue="Livestream", cost="Free",
         url="https://www.eventbrite.com/e/free-speech-in-the-age-of-ai-symposium-in-person-tickets-1992952038195"),
    dict(tier="virtual", date="2026-10-26", time="two days",
         name="Virtual ClioCon", host="Clio", venue="Online", cost="Free, CLE-eligible",
         note="Runs alongside the in-person conference. No grant needed.",
         url="https://cliocon.com/virtual-experience/"),
    dict(tier="virtual", date="2026-09-29", time="12:00pm",
         name="FCBA TMT Law & Policy Pipeline Program: info session (1Ls)",
         host="Federal Communications Bar Association", venue="Virtual", cost="Free",
         note="Paid 2027 summer internships, training and mentorship in technology, media, telecom, "
              "AI, privacy and cybersecurity law, for first-year students. Second session Wed Sep 30, "
              "6:00pm. Registration is in CareerBuzz.",
         url="https://www.fcba.org/"),
    dict(tier="virtual", date="2026-09-30", time="6:00pm",
         name="FCBA TMT Law & Policy Pipeline Program: info session (1Ls)",
         host="Federal Communications Bar Association", venue="Virtual", cost="Free",
         note="Evening repeat of the Sep 29 session. Registration is in CareerBuzz.",
         url="https://www.fcba.org/"),
    dict(tier="virtual", date="2026-10-29", time="—",
         name="LSNTAP quarterly community meeting", host="LSNTAP", venue="Virtual",
         cost="Free", url="https://www.lsntap.org/events"),
]

# Paid, but at a student rate worth knowing about.
MCLE = [
    ("2026-09-17", "Protecting Proprietary Information in the AI Age", "$87.50", "2270026WBC"),
    ("2026-09-23", "AI in Legal Practice: Practical Uses, Ethical Risks & Best Practices", "$72.50", "2270078WBC"),
    ("2026-10-05", "Fluency in the Most Useful AI Tools for Law Firms", "$87.50", "2270076WBC"),
    ("2026-11-19", "How to Use ChatGPT, Gemini & Other Generative AI Tools", "$87.50", "2270070WBC"),
    ("2026-12-16", '"Artificial Intelligence" Ethics for Attorneys', "$87.50", "2270072WBC"),
]

TIERS = [
    ("litsa", "Ours", "What LITSA is running. More this fall once dates and speakers are set."),
    ("suffolk", "At Suffolk", "Happening in our building or run by the Law School."),
    ("boston", "Around Boston", "The legal tech calendar most students never see."),
    ("virtual", "From anywhere", "No travel required."),
    ("ai", "Boston's AI scene", "From the Mass AI Coalition's calendar. Not law-specific, but it is "
     "where the people building AI in Boston meet. Most ask you to register for approval."),
]


def when(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%a %b ").replace(" 0", " ") + str(d.day)

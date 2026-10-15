"""The LITSA field taxonomy (families of legal innovation and technology domains).

Copied from the LITSA OrgFair project so this site builds on its own.
"""

FAMILIES = [
 ("Technology for law",
  "Tools that do legal work. This is the part people picture when they hear legal tech, "
  "and it is roughly a third of it.",
  [
   ("Contracts &amp; automation", "Turning contracting from bespoke drafting into something repeatable, with playbooks behind it.",
    "Commercial counsel &middot; Contract manager &middot; CLM implementation", 1),
   ("E-discovery &amp; litigation technology", "Finding the relevant thing inside millions of documents, defensibly.",
    "E-discovery counsel &middot; Litigation support &middot; Discovery project manager", 1),
   ("Knowledge &amp; practice innovation", "Capturing what a firm knows so the next person does not start from nothing.",
    "Knowledge management attorney &middot; Practice innovation counsel", 1),
   ("Building the tools", "Someone writes the software. At Suffolk, often students who learned it here.",
    "Legal engineer &middot; Solutions architect &middot; Developer", 2),
  ]),
 ("Law of technology",
  "Not tools at all. This is doctrine, about technology as a subject. Every field in this "
  "family is open to someone who never touches a line of code.",
  [
   ("Privacy &amp; data protection", "What organizations may collect and keep, and what happens when they get it wrong.",
    "Privacy counsel &middot; Data protection officer &middot; Privacy analyst", 0),
   ("AI governance &amp; regulation", "How automated systems get audited, disclosed, and governed. Barely existed five years ago.",
    "AI governance counsel &middot; Responsible AI lead &middot; Policy counsel", 0),
   ("Cybersecurity &amp; incident response", "What the law requires before, during, and after a breach, and who must be told.",
    "Cyber counsel &middot; Incident response &middot; Compliance", 0),
   ("Product &amp; platform counsel", "Lawyers who work on the product itself rather than on disputes about it.",
    "Product counsel &middot; Trust &amp; safety &middot; Platform policy", 0),
  ]),
 ("How law reaches people",
  "Innovation that is not really about technology. It is about who gets served, how badly "
  "the process works, and whether anyone can understand it.",
  [
   ("Access to justice", "Most people in civil court have no lawyer. This is the work of helping them anyway.",
    "Legal aid technologist &middot; Court innovation staff &middot; A2J fellow", 1),
   ("Legal design", "Making legal information usable by the people it is aimed at. Plain language, better forms.",
    "Legal designer &middot; Content designer &middot; Forms specialist", 0),
   ("Legal operations", "How a legal department actually runs: process, spend, vendors, and whether it works.",
    "Legal operations manager &middot; Legal ops analyst", 0),
   ("Court technology &amp; ODR", "Online dispute resolution, e-filing, and modernizing courts. Suffolk runs a clinic in this.",
    "Court technologist &middot; ODR program staff", 1),
  ]),
]

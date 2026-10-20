import shell as sh

ITEMS = [
 ("LIT Concentration", "https://www.suffolk.edu/law/academics-clinics/what-can-i-study/legal-innovation-technology",
  "The first in the country, with <span class='peek' tabindex='0'>four core courses and twenty-one electives<span class='pop'><b>Core, take three of four</b>Twenty-First Century Legal Profession &middot; Process Improvement and Legal Project Management &middot; Legal Technology for Small Firm Practice &middot; Generative AI and the Delivery of Legal Services<b>Electives, a selection</b>Artificial Intelligence and the Law &middot; Cybersecurity Law and Policy &middot; Digital Evidence &middot; E-Discovery Law &middot; Emerging AI Regulatory Frameworks &middot; Design Thinking for Lawyers &middot; Legal Operations and Management of Legal Services &middot; ODR &middot; Privacy and Data Security Requirements &middot; Race, Ethical AI and Cyber Civil Rights &middot; Blockchain, Cryptocurrency and the Law &middot; Lawyers as Leaders &middot; Transactional Skills</span></span> covering everything from AI regulation to digital evidence.",
  "Declare it late if you want. Taking one elective tells you more than a year of wondering."),
 ("The LIT Lab", "https://suffolklitlab.org",
  "Where students build real tools. Its pandemic court-forms work put mobile "
  "smartforms in front of people when courthouses were closed, and was covered "
  "by the New York Times and the Boston Globe.",
  "Over 20,000 court forms filed through <a href='https://courtformsonline.org'>Court Forms Online</a>, including 3,500 fee waivers."),
 ("ODR Innovation Clinic", "https://sites.suffolk.edu/legaltech/",
  "Run with the <a href='https://www.adr.org'>American Arbitration Association</a>. Students design an online "
  "workflow for uncontested and low-contest divorce in Massachusetts.",
  "Now in its third year. Grant funded, and it carries clinic credit."),
 ("Journal of High Technology Law", "https://sites.suffolk.edu/jhtl/",
  "Student run, and open to everyone rather than only students concentrating in "
  "intellectual property.",
  "Joined through a summer write-on competition, and it carries academic credit. Plan for the summer, not the fall."),
 ("LIT Con", "https://suffolklitlab.org/events/lit-con/",
  "A legal innovation conference held at Suffolk every spring, hybrid since 2023.",
  "Educators, legal services, courts and nonprofits come here for it, so the practitioners arrive without you having to travel."),
 ("STEM-designated LIT LLM", "https://www.suffolk.edu/news-features/news/2024/11/04/20/21/lit-llm-announced",
  "Announced in 2024, the first STEM-designated LLM in legal innovation and "
  "technology in the country. Twenty-four credits.",
  "Mostly relevant after the JD, but it changes what a Suffolk degree is worth."),
]

CSS = """
<style>
.entries{margin-top:var(--s6);}
.scene{margin-top:var(--s7); border-top:2px solid var(--gold); padding-top:var(--s3);}
.scene img{display:block; width:100%; height:auto;}
.scene figcaption{margin-top:var(--s3); font-size:var(--t-xs); color:var(--ink-3);}
.entry{display:grid; grid-template-columns:minmax(0,7fr) minmax(0,5fr);
  gap:var(--s6) var(--s7); padding-block:var(--s6);
  border-top:1px solid var(--line-soft);}
.entry:first-child{border-top:2px solid var(--gold);}
.entry h3{margin-bottom:var(--s3);}
.entry .what{color:var(--ink-2);}
.entry .note{font-size:var(--t-sm); color:var(--ink-3); line-height:1.6;
  border-left:2px solid var(--gold); padding-left:var(--s4);}
.entry .note b{color:var(--ink-2); font-weight:600;}
@media (max-width:820px){.entry{grid-template-columns:1fr; gap:var(--s4);}}
</style>
"""

LABELS = ['One detail', 'In practice', 'The catch', 'Timing', 'The upside', 'Later, but soon']

def entry(i, k=0):
    name, href, what, note = i
    return (f'<article class="entry"><div><h2 class="h3"><a href="{href}">{name}</a></h2>'
            f'<p class="what">{what}</p></div>'
            f'<p class="note"><b>{LABELS[k % len(LABELS)]}.</b> {note}</p></article>')

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="S">
    <p class="rail-label">At Suffolk</p>
    <div>
      <h1 style="max-width:15ch">What Suffolk already gives you.</h1>
      <p class="lede" style="margin-top:var(--s5)">All of this exists whether or not
      you ever join LITSA, and most of it is easy to miss in a first year.</p>
      <figure class="scene">
        <img src="/img/suffolk-atrium-pixel.webp" width="2172" height="724"
          alt="Sargent Hall’s central atrium, viewed upward past its columns and suspended American flag."
          fetchpriority="high">
        <figcaption>Sargent Hall&rsquo;s central atrium, based on a 2019 Suffolk University photograph.</figcaption>
      </figure>
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Six things</p>
    <div class="entries">{"".join(entry(i, k) for k, i in enumerate(ITEMS))}</div>
    {sh.scene("moot-courtroom-pixel-panorama.png", "A modern law-school moot courtroom.",
      "A modern moot courtroom.", size=(1983, 793))}
  </div>
</section>

{sh.step()}

<section class="slab tight">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">Then what</p>
    <div>
      <h2>Building is one of the things we do.</h2>
      <p class="lede" style="margin-top:var(--s5)">The institute, the lab and the
      clinic belong to the school. LITSA is the student side of it, and it is the
      part with room for you.</p>
      <p style="margin-top:var(--s6)"><a href="/planner/">Plan your semester with the course planner &rarr;</a></p>
      <p style="margin-top:var(--s3)"><a href="/build/">What we build &rarr;</a></p>
      <p style="margin-top:var(--s3)"><a href="/curriculum/">All seven concentrations,
      with what each one requires &rarr;</a></p>
      <p style="margin-top:var(--s3)"><a href="/resources/">Everything Suffolk already
      pays for on your behalf &rarr;</a></p>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("At Suffolk · LITSA",
        "The LIT concentration, the LIT Lab, the AAA dispute resolution clinic, "
        "the Journal of High Technology Law, LIT Con and the STEM LLM, annotated "
        "for students.", "/suffolk/", BODY,
        assistant_seed="What is legal innovation and technology at Suffolk?")

import shell as sh

ACTS = [
 ("1906", "The instinct",
  ["Gleason Leonard Archer, raised poor in rural Maine, is loaned money by a "
   "Boston businessman named George Frost to finish his degree. Frost refuses "
   "repayment and tells him: <i>if you ever have a chance to pass this favor on "
   "to others, do it for me.</i>",
   "Archer begins giving law lectures in his own parlour in Roxbury, at night, so "
   "that working people could attend. The stated goal is legal education "
   "regardless of economic class, race or religion. The first Suffolk student "
   "passes the bar in 1908, and by 1930 it is one of the largest law schools in "
   "the country, largely serving working-class immigrants shut out everywhere else.",
   "The first Suffolk student to pass the bar, in 1908, was a machinist named "
   "Roland E. Brown."]),
 ("2013", "The institution",
  ["Dean Camille Nelson founds the Institute on Law Practice Technology and "
   "Innovation and appoints <a href='https://www.suffolk.edu/academics/faculty/a/p/aperlman'>Andrew Perlman</a> its first director. The LIT blog&rsquo;s "
   "earliest post is from March of that year. Perlman goes on to found the LIT "
   "concentration, the first in the country, and to help establish the LIT Lab. He "
   "becomes Dean Perlman in 2018.",
   "In October 2018 Suffolk and the Stanford Legal Design Lab release <b>Learned "
   "Hands</b>, a game in which players label real legal problems drawn from social "
   "media to train an issue-spotting classifier. It draws <a href='https://www.abajournal.com/news/article/new_game_lets_players_train_ai_and_close_the_justice_gap/'>coverage</a> from "
   "the ABA Journal, Artificial Lawyer, Massachusetts Lawyers Weekly and LawSites "
   "in a single week. That fall, <i>preLaw</i> ranks Suffolk first for legal "
   "technology, out of thirty schools.",
   "A Pew grant in July 2019 turns that labelled data into <b>Spot</b>. LITSA&rsquo;s "
   "own record on SUConnect begins in January 2019 , three months after "
   "Learned Hands."]),
 ("2020", "The proof",
  ["At the outset of the pandemic the LIT Lab launches the <b>Document Assembly "
   "Line</b> under <a href='https://suffolklitlab.org/team/'>David Colarusso and Quinten Steenhuis</a>: mobile smartforms for "
   "Massachusetts courts, closer to a guided interview than a web form, built for "
   "people who could not physically reach a courthouse.",
   "Over twenty thousand court forms are downloaded, including 3,500 fee waivers, "
   "500 restraining order petitions and 550 emergency housing injunctions. The "
   "<a href='https://www.nytimes.com/2020/09/02/your-money/eviction-moratorium-covid.html'><i>New York Times</i></a> and the <a href='https://www.bostonglobe.com/2020/04/02/nation/pandemic-poses-significant-access-to-justice-obstacles-cambridge-technologist-is-developing-solutions/'><i>Boston Globe</i></a> cover it. <i>preLaw</i> ranks "
   "Suffolk first again for legal technology in 2021.",
   "Twenty thousand forms is twenty thousand people who could not reach a "
   "courthouse filing anyway."]),
 ("2024", "to present",
  ["Every first-year student now completes an AI learning track. Six new courses "
   "arrive in twelve to fifteen months, including one on AI regulatory frameworks "
   "and international governance. The Online Dispute Resolution Innovation Clinic "
   "launches with the American Arbitration Association.",
   "In November 2024 Suffolk announces the country&rsquo;s first STEM-designated "
   "LLM in Legal Innovation and Technology. In October 2025 <i>National Jurist</i> puts "
   "Suffolk and North Carolina Central at the head of its twelve most "
   "innovative law schools. In August 2026 <i>preLaw</i> grades Suffolk A+ for "
   "technology law, one of twelve schools in the top tier.",
   "In March 2026 LITSA runs its first build competition. One track puts teams "
   "inside a legal aid organization facing a surge of intake; the other makes "
   "them the junior associate on a commercial lease dispute. Teams have a single "
   "evening and no preparation. The winning build handled document management "
   "with AI fact-checking that flagged contradictions across a client file."]),
]


BEATS = [
 ("1908", "Roland E. Brown, a machinist, becomes the first Suffolk student to pass the Massachusetts Bar."),
 ("1914", "The school receives its degree-granting charter and moves to 45 Mount Vernon Street."),
 ("1915", "Thomas Vreeland Jones graduates, among the first African American graduates of Suffolk Law."),
 ("1920", "A day division is added. Governor Calvin Coolidge lays the cornerstone of the Archer Building."),
 ("1929", "Harry Hom Dow graduates and becomes the first Chinese American admitted to the Massachusetts Bar."),
 ("1930", "Suffolk is one of the largest law schools in the country."),
 ("1937", "The first female student enrollls."),
 ("1966", "The school opens 41 Temple Street, later Judge Donahue Hall."),
 ("1967", "The Suffolk University Law Review publishes its first issue."),
 ("1972", "Dicta, the student newspaper, begins publication."),
 ("1976", "The Suffolk Transnational Law Journal is established."),
 ("1999", "Sargent Hall opens with the 96,000 square foot Moakley Law Library."),
]

def beats():
    rows = "".join('<div class="beat"><b>%s</b><p>%s</p></div>' % b for b in BEATS)
    return ('<div class="act"><div class="yr num">1908<small>to 1999</small></div>'
            '<div class="body"><p>Archer&rsquo;s stated goal was legal education '
            'regardless of economic class, race or religion. The record of who '
            'actually got through the door is the part worth reading.</p>'
            '<div class="beats">' + rows + '</div></div></div>')

CSS = """
<style>
.act{display:grid; grid-template-columns:var(--rail) minmax(0,1fr);
  column-gap:var(--gap); padding-block:var(--s8);
  border-top:1px solid var(--line-soft);}
.act:first-of-type{border-top:0; padding-top:var(--s6);}
.act .yr{font-family:var(--display); font-size:var(--t-2xl); line-height:1;
  letter-spacing:.01em; color:var(--ink);}
.act .yr small{display:block; font-size:var(--t-xs); letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin-top:var(--s3);}
.act .body{max-width:var(--measure);}
.act .body p + p{margin-top:var(--s5);}
figure.plate{margin-top:var(--s7); max-width:340px;}
figure.plate img{width:100%; height:auto; filter:grayscale(1) contrast(1.06);}
figure.sig{margin-top:var(--s6); max-width:300px;}
figure.sig img{width:100%; height:auto; mix-blend-mode:multiply;}
.coda{max-width:52ch;}
@media (max-width:680px){
  .act{grid-template-columns:1fr; row-gap:var(--s4);}
}
</style>
"""

def para(k, yr, p):
    cls = ' class="dropcap"' if (k == 0 and yr == "1906") else ""
    return "<p%s>%s</p>" % (cls, p)

def act(a, extra=""):
    yr, name, paras = a
    return (f'<article class="act" id="y{yr}"><div class="yr num" data-ghost="{yr}">'
            f'<a href="#y{yr}">{yr}</a><small>{name}</small></div>'
            f'<div class="body">{"".join(para(k, yr, p) for k, p in enumerate(paras))}{extra}</div></article>')

PLATE = """
<figure class="plate">
  <picture>
    <source srcset="/img/archer-1915.webp" type="image/webp">
    <img src="/img/archer-1915.jpg" width="680" height="992"
         alt="Gleason Leonard Archer, founder of Suffolk University Law School, photographed in 1915.">
  </picture>
  <figcaption><b>Gleason Leonard Archer, 1915.</b> He began by teaching law in his
  own parlour in Roxbury, at night. Public domain, via Wikimedia Commons.</figcaption>
</figure>
<figure class="sig">
  <picture>
    <source srcset="/img/archer-signature.webp" type="image/webp">
    <img src="/img/archer-signature.jpg" width="509" height="73"
         alt="Gleason Leonard Archer's handwritten signature, 1918.">
  </picture>
  <figcaption>His signature, 1918. Public domain, via Wikimedia Commons.</figcaption>
</figure>
"""

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="H">
    <p class="rail-label">History</p>
    <div>
      <h1 style="max-width:15ch">A night school, and what came of it.</h1>
      <p class="lede" style="margin-top:var(--s5)">Suffolk Law was founded in 1906 so
      that people who worked during the day could become lawyers at night.</p>
      {sh.scene("history-night-school-pixel.webp", "An early twentieth-century Boston townhouse used for evening law classes.", "A period interpretation of the Roxbury rooms where Gleason Archer began teaching law at night in 1906.", True)}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap">
    {act(ACTS[0], PLATE)}
    {beats()}
    {act(ACTS[1])}
    {act(ACTS[2])}
    {act(ACTS[3])}
    {sh.scene("history-evening-classroom-pixel.webp", "An early twentieth-century evening law classroom with wooden desks and law books.", "An evening law classroom in the early twentieth century.")}
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Cite this</p>
    <div>
      <p class="cite" data-cite="LITSA, &quot;A night school, and what came of it&quot;, suffolklitsa.org/history, 2026."
         title="Click to copy"><code>LITSA, &ldquo;A night school, and what came of it&rdquo;,
      suffolklitsa.org/history, 2026.</code><br>Every date here is drawn from Suffolk
      University records, the Suffolk LIT Lab, <i>preLaw</i> magazine and the National
      Jurist. Photographs are public domain via Wikimedia Commons.</p>
    </div>
  </div>
</section>

{sh.step()}

<section class="slab tight">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">2026</p>
    <div class="coda">
      <h2>The list keeps going.</h2>
      <p class="lede" style="margin-top:var(--s5)">Every line above started with
      someone building what the school did not have yet. Archer taught the first
      class in his own front room. The LIT Lab shipped court forms out of a
      courthouse nobody could enter. The most recent entry did not exist eighteen
      months ago.</p>
      <p class="lede" style="margin-top:var(--s4)">The next one is unwritten, and
      it is not going to be written by the faculty.</p>
      <p class="pull" style="color:#F0E3C6;border-color:var(--gold)">If you ever
      have a chance to pass this favor on to others, do it for me.</p>
      <p class="small" style="color:#8FA0B5">George Frost to Gleason Archer, before 1906</p>
      <p style="margin-top:var(--s6)"><a href="/join/">Join LITSA &rarr;</a></p>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("History · LITSA",
        "Legal innovation at Suffolk Law, from Gleason Archer's 1906 night school "
        "to the LIT Lab, the Document Assembly Line and the present.",
        "/history/", BODY)

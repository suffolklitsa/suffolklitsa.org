import shell as sh

LANES = [
 ("Chatbot testing", "Open now",
  "Suffolk runs a chatbot for student questions. It gets things wrong often "
  "enough to be worth testing properly, and finding out where needs no "
  "engineering background at all.",
  "Fill in a short form each time you catch it being wrong. We collect them and work out which gaps matter.",
  "The fastest way to do real work in your first month."),
 ("The build competition", "Spring",
  "Teams ship a working legal tool in a single evening from a cold start. Seven "
  "teams entered the first one. The winners were two first-year evening students "
  "who built a document system that flagged contradictions across a client file.",
  "Enter it, judge it, write the problem sets, or run a track.",
  "We want it bigger this year, and open to other schools."),
 ("Legal aid tooling", "Open now",
  "Most people in civil court have no lawyer. Intake and drafting are the parts "
  "of that a law student can move.",
  "Interview the people doing intake, map one workflow end to end, draft the forms.",
  "The access-to-justice work and the building work are the same work."),
 ("Simulated legal practice", "Coming",
  "Ongoing simulated matters that give students repetitions on real legal work "
  "before anyone lets them do it for real.",
  "Nothing to do yet. Join the roster and you will hear about it first.",
  "In design. We will say more when there is something to try."),
 ("Open-source court forms", "Open now",
  "The LIT Lab's Document Assembly Line is open source, and it puts mobile court "
  "forms in front of people who cannot get to a courthouse. Over twenty thousand "
  "have been downloaded.",
  "Test a form, report what breaks, or write a new one.",
  "Your work ships to people using it the same month."),
]

CSS = """
<style>
.lanes{margin-top:var(--s6);}
.lane{border-top:2px solid var(--gold); padding-block:var(--s6) var(--s7);}
.lane:last-child{border-bottom:1px solid var(--line-soft);}
.lane .hd{display:flex; justify-content:space-between; align-items:baseline;
  gap:var(--s4); flex-wrap:wrap;}
.lane .status{font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.12em; text-transform:uppercase; color:var(--ink-3);}
.lane .what{color:var(--ink-2); margin-top:var(--s4); max-width:58ch;}
.lane .rows{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  gap:var(--s5) var(--s7); margin-top:var(--s5);}
.lane .rows .lab{font-family:var(--display); font-size:var(--t-xs);
  letter-spacing:.13em; text-transform:uppercase; color:var(--ink-3);
  margin-bottom:var(--s2);}
.lane .rows p{font-size:var(--t-base); line-height:1.55;}
@media (max-width:760px){.lane .rows{grid-template-columns:1fr;}}
</style>
"""

def lane(l):
    name, status, what, how, note = l
    return (f'<article class="lane"><div class="hd"><h2 class="h3">{name}</h2>'
            f'<span class="status">{status}</span></div>'
            f'<p class="what">{what}</p><div class="rows">'
            f'<div><p class="lab">What helping looks like</p><p>{how}</p></div>'
            f'<div><p class="lab">The catch</p><p>{note}</p></div></div></article>')

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="B">
    <p class="rail-label">What we build</p>
    <div>
      <h1 style="max-width:17ch">Five things you could work on.</h1>
      <p class="lede" style="margin-top:var(--s5)">Interviewing, testing, writing
      problem sets, judging, mapping how a process actually runs, sitting with
      someone while they try to use the thing. Pick one and we will find you
      something small enough to finish.</p>
      {sh.scene("build-workshop-pixel.webp", "A legal-technology workshop with laptops, legal pads and Boston outside at night.", "A legal-technology workshop set up for a team build.", True)}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">The lanes</p>
    <div class="lanes">{"".join(lane(l) for l in LANES)}</div>
    {sh.scene("build-court-forms-pixel.webp", "A workflow connecting a paper court form, a phone and a courthouse filing tray.", "A court-form workflow across paper, mobile and filing systems.")}
  </div>
</section>

{sh.step()}

<section class="slab tight">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">Getting in</p>
    <div>
      <h2>Turning up is the whole entry requirement.</h2>
      <p class="lede" style="margin-top:var(--s5)">No application and no screening.
      Join on SUConnect and tell us which of these sounds interesting, or email
      <a href="mailto:sam.darkwa@su.suffolk.edu?subject=Getting%20involved%20in%20a%20LITSA%20project">sam.darkwa@su.suffolk.edu</a>
      with the one you want and we will set up a first task.</p>
      <div class="acts" style="margin-top:var(--s6); display:flex; gap:var(--s4); flex-wrap:wrap">
        <a class="btn btn--solid" href="mailto:sam.darkwa@su.suffolk.edu?subject=Getting%20involved%20in%20a%20LITSA%20project">Email to get involved</a>
        <a class="btn btn--ghost" href="/join/">How to join</a>
      </div>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("What we build · LITSA",
        "Chatbot testing, the build competition, legal aid tooling and open-source "
        "court forms. Four projects at Suffolk Law, all of them open to new people.",
        "/build/", BODY)

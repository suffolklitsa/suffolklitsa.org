import shell as sh

CSS = """
<style>
.steps{margin-top:var(--s6); counter-reset:s;}
.stepitem{display:grid; grid-template-columns:56px minmax(0,1fr); gap:var(--s5);
  padding-block:var(--s6); border-top:1px solid var(--line-soft);}
.stepitem:first-child{border-top:2px solid var(--gold);}
.stepitem .n{font-family:var(--display); font-size:var(--t-xl); color:var(--gold);
  line-height:1; letter-spacing:.01em;}
.stepitem h3{margin-bottom:var(--s3);}
.stepitem p{color:var(--ink-2); max-width:54ch;}
.stepitem .btn{margin-top:var(--s5);}
.btn{font-family:var(--display); font-size:var(--t-sm); letter-spacing:.1em;
  text-transform:uppercase; padding:14px 22px; display:inline-block;}
.btn--solid{background:var(--blue); color:var(--paper);}
.btn--solid:hover{background:var(--blue-deep); text-decoration:none;}
.faq{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s6) var(--s7); margin-top:var(--s6);}
.faq h3{font-family:var(--display); font-size:var(--t-md); letter-spacing:.02em;
  margin-bottom:var(--s3);}
.faq p{color:var(--ink-2); font-size:var(--t-base); line-height:1.55;}
@media (max-width:760px){.faq{grid-template-columns:1fr;}}
</style>
"""

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="J">
    <p class="rail-label">Joining</p>
    <div>
      <h1 style="max-width:14ch">Join, in about two minutes.</h1>
      <p class="lede" style="margin-top:var(--s5)">Membership runs through
      SUConnect, so it counts as an official Suffolk affiliation and shows up on
      your involvement record. There is no application and no screening.</p>
      {sh.scene("join-sargent-entry-pixel.webp", "The entrance to a Boston law school, with a student-organization check-in table.", "A student-organization check-in table inside a Boston law school.", True)}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Two steps</p>
    <div class="steps">
      <article class="stepitem">
        <span class="n num">1</span>
        <div>
          <h2 class="h3">Join on SUConnect</h2>
          <p>Sign in with your Suffolk login and press join on the LITSA page.
          That is the official roster, and it is how you get on the mailing list
          for anything we run.</p>
          <a class="btn btn--solid" href="https://suffolk.campuslabs.com/engage/organization/litsa">Join on SUConnect</a>
        </div>
      </article>
      <article class="stepitem">
        <span class="n num">2</span>
        <div>
          <h2 class="h3">Tell us what you actually want</h2>
          <p>Ninety seconds. What you would want out of LITSA, which of the three
          families interests you, and whether you would rather build, attend, or
          watch for a while first. &ldquo;Not sure yet&rdquo; is the most common
          answer and a perfectly good one.</p>
          <a class="btn btn--solid" href="/join/#survey">Take the survey</a>
        </div>
      </article>
    </div>
    {sh.scene("join-roster-pixel.webp", "A membership table with a blank roster, name badges, law books and a laptop.", "A membership table with a roster, name badges and a laptop.")}
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Reasonable questions</p>
    <div class="faq">
      <div><h3>Do I need to code?</h3><p>No. Eleven of the twelve domains in this
      field need none at all, and one whole family of four is doctrine rather than
      software. <a href="/field/">See the field</a>.</p></div>
      <div><h3>I am a 1L. Is it too early?</h3><p>It is the best time. Nothing here
      assumes background, and the pair who won last spring&rsquo;s build
      competition were first-year evening students.</p></div>
      <div><h3>How much time does it take?</h3><p>As little as showing up to one
      thing a semester. The work is scoped so that a small contribution is still a
      finished contribution.</p></div>
      <div><h3>I am an evening student.</h3><p>So is a good share of the school,
      and the format is built around that. Suffolk was founded as a night school in 1906. <a href="/history/">the history is worth reading</a>.</p></div>
      <div><h3>Can I just watch for a bit?</h3><p>Yes. Join the roster and read the
      emails. Nobody will chase you.</p></div>
      <div><h3>I am not a Suffolk student.</h3><p>Email
      <a href="mailto:sam.darkwa@su.suffolk.edu">sam.darkwa@su.suffolk.edu</a>. Some of
      what we run is open, and we are interested in what other schools are doing.</p></div>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("Join · LITSA",
        "Join LITSA through SUConnect and tell us what you want out of it. "
        "No application, no screening, and no coding required.",
        "/join/", BODY)

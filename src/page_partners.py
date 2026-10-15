import shell as sh

CSS = """
<style>
.two{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s7); margin-top:var(--s6);}
.card{border-top:2px solid var(--gold); padding-top:var(--s4);}
.card h3{margin-bottom:var(--s3);}
.card p{color:var(--ink-2); font-size:var(--t-base); line-height:1.55;}
.facts{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px;
  background:var(--line-soft); border:1px solid var(--line-soft);
  margin-top:var(--s7);}
.facts div{background:var(--paper-2); padding:var(--s5);}
.facts b{font-family:var(--display); font-size:var(--t-xl); display:block;
  line-height:1;}
.facts span{font-size:var(--t-sm); color:var(--ink-3); display:block;
  margin-top:var(--s3); line-height:1.5;}
@media (max-width:760px){.two,.facts{grid-template-columns:1fr;}}
</style>
"""

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="P">
    <p class="rail-label">Partners</p>
    <div>
      <h1 style="max-width:17ch">For faculty, firms and other schools.</h1>
      <p class="lede" style="margin-top:var(--s5)">We run events, test tools, and put
      students in front of real problems. If any of that is useful to you, write to
      us and we will work out what it looks like.</p>
      <div class="facts">
        <div><b class="num">A+</b><span>Suffolk, technology law, <i>preLaw</i> magazine 2026</span></div>
        <div><b class="num">12</b><span>domains mapped across three families of the field</span></div>
        <div><b class="num">1906</b><span>the year Suffolk was founded as a night law school</span></div>
      </div>
      {sh.scene("partners-roundtable-pixel.webp", "A law-school conference table set with case files, legal pads and laptops.", "A conference table prepared for a working session.", True)}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">What we can offer</p>
    <div class="two">
      <div class="card"><h2 class="h3">Practitioners</h2>
        <p>A room of students who want to hear how the work actually gets done,
        rather than a careers panel. Short formats work better than long ones and
        we will handle the logistics.</p></div>
      <div class="card"><h2 class="h3">Faculty</h2>
        <p>A student body to test things on. Course material, tools, research
        instruments, or an idea that needs a first cohort. We can also route
        students into work that needs hands.</p></div>
      <div class="card"><h2 class="h3">Firms and legal tech companies</h2>
        <p>Students who chose this field on purpose, at the school graded A+ for
        technology law. Sponsor an event, set a problem for the build competition,
        or hire out of it.</p></div>
      <div class="card"><h2 class="h3">Other student organizations</h2>
        <p>Compare notes with us. The build-competition format is designed to be
        copied, and we will hand over the problem sets and the run sheet.</p></div>
    </div>
    {sh.scene("partners-exchange-pixel.webp", "A table with campus maps, court forms and two connected laptops.", "Materials for sharing a legal-technology project between schools.")}
  </div>
</section>

{sh.step()}

<section class="slab tight">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">Contact</p>
    <div>
      <h2>One address, and a person reads it.</h2>
      <p class="lede" style="margin-top:var(--s5)">
        <a href="mailto:sam.darkwa@su.suffolk.edu">sam.darkwa@su.suffolk.edu</a>
      </p>
      <p class="small" style="margin-top:var(--s5);color:#8FA0B5;max-width:52ch">
      LITSA is a registered student organization of Suffolk University Law School.
      It speaks for its members, not for the university.</p>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("Partners · LITSA",
        "For faculty, practitioners, firms and other student organizations "
        "interested in working with LITSA at Suffolk Law.",
        "/partners/", BODY)

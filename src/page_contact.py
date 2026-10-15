import shell as sh

BOARD = [
 ("Sam Darkwa Jr.", "President"),
 ("Noy Lohr", "Vice President"),
 ("Morgan Walters", "Chief Operating Officer"),
 ("Pedro Barbosa", "Technology Liaison"),
 ("Kevin Shang", "Treasurer"),
]

CSS = """
<style>
.board{margin-top:var(--s6);}
.member{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  gap:var(--s5); padding-block:var(--s5); border-top:1px solid var(--line-soft);
  align-items:baseline;}
.member:first-child{border-top:2px solid var(--gold);}
.member .nm{font-family:var(--display); font-size:var(--t-md); letter-spacing:.02em;}
.member .ti{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.13em;
  text-transform:uppercase; color:var(--ink-3);}
.member .ow{font-size:var(--t-base); color:var(--ink-2); line-height:1.5;}
@media (max-width:760px){.member{grid-template-columns:1fr; gap:var(--s2);}}
.ways{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:var(--s7);
  margin-top:var(--s6);}
.way{border-top:2px solid var(--gold); padding-top:var(--s4);}
.way h3{margin-bottom:var(--s3);}
.way p{color:var(--ink-2); font-size:var(--t-base); line-height:1.55;}
@media (max-width:760px){.ways{grid-template-columns:1fr;}}
</style>
"""

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="C">
    <p class="rail-label">Contact</p>
    <div>
      <h1 style="max-width:13ch">Talk to a person.</h1>
      <p class="lede" style="margin-top:var(--s5)">One address reaches the whole
      board. Say what you want and it will get to whoever handles it.</p>
      <p style="margin-top:var(--s6);font-size:var(--t-lg)">
        <a href="mailto:sam.darkwa@su.suffolk.edu">sam.darkwa@su.suffolk.edu</a></p>
      <p style="margin-top:var(--s3);font-size:var(--t-md);color:var(--ink-2)">
        Or reach Sam directly at
        <a href="mailto:Sam.Darkwa@su.suffolk.edu">Sam.Darkwa@su.suffolk.edu</a>.</p>
      {sh.scene("contact-correspondence-pixel.webp", "A shared office desk with an inbox, envelopes, a phone and Boston buildings outside.", "A shared correspondence desk for board email and mail.", True)}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Who we are</p>
    <div>
      <h2>The 2026&ndash;27 board</h2>
      <div class="board">
        {"".join('<div class="member"><span class="nm">%s</span>'
                 '<span class="ti">%s</span></div>' % m for m in BOARD)}
      </div>
      {sh.scene("contact-board-table-pixel.webp", "An executive-board work table with agenda sheets, folders, a task board and Beacon Hill outside.", "An executive-board table after a planning meeting.")}
    </div>
  </div>
</section>

{sh.step()}

<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Depending on what you want</p>
    <div class="ways">
      <div class="way"><h2 class="h3">You want to join</h2>
        <p>Go straight to <a href="https://suffolk.campuslabs.com/engage/organization/litsa">SUConnect</a>.
        No email needed, and it puts you on the roster properly.</p></div>
      <div class="way"><h2 class="h3">You want to speak or partner</h2>
        <p>Write to us. Short formats work better than long ones, and we handle
        the logistics. <a href="/partners/">More on that here</a>.</p></div>
      <div class="way"><h2 class="h3">You are press</h2>
        <p>Write to us and we will point you at whoever ran the thing you are
        asking about.</p></div>
      <div class="way"><h2 class="h3">You are at another school</h2>
        <p>We will hand over the build-competition problem sets and the run
        sheet. Ask.</p></div>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("Contact · LITSA",
        "Reach the LITSA board at Suffolk University Law School.",
        "/contact/", BODY)

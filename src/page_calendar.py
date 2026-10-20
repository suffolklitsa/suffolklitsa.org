from urllib.parse import quote
import shell as sh

FEED = "https://suffolklitsa.org/feeds/academic-calendar.ics"
WEBCAL = "webcal://suffolklitsa.org/feeds/academic-calendar.ics"
NAME = "Suffolk Law academic calendar"
SOURCE = "https://www.suffolk.edu/law/academics-clinics/academic-resources/academic-calendar---law"

LINKS = [
    ("Google Calendar", "https://calendar.google.com/calendar/r?cid=" + quote(WEBCAL, safe="")),
    ("Apple Calendar or iPhone", WEBCAL),
    ("Outlook", "https://outlook.office.com/calendar/addfromweb?url=" + quote(FEED, safe="")
     + "&name=" + quote(NAME)),
]

CSS = """
<style>
.subs{display:flex; flex-wrap:wrap; gap:var(--s3); margin-top:var(--s6);}
.subs a{display:inline-block; padding:var(--s3) var(--s5); border:2px solid var(--gold);
  font-weight:600; text-decoration:none;}
.subs a:hover,.subs a:focus-visible{background:var(--gold); color:var(--ink);}
.feed-url{margin-top:var(--s6); font-size:var(--t-sm); color:var(--ink-3);}
.feed-url code{word-break:break-all;}
</style>
"""

BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">Calendar</p>
    <div>
      <h1 style="max-width:16ch">Suffolk Law&rsquo;s 2026&ndash;27 calendar, in yours.</h1>
      <p class="lede" style="margin-top:var(--s5)">Classes beginning and ending, add/drop,
      Legal Writing Requirement deadlines, exams, holidays, recesses, reading days, make-up
      days and commencement. Subscribe once and the dates stay current.</p>
      <div class="subs">{"".join(f'<a href="{href}">{label}</a>' for label, href in LINKS)}</div>
      <p class="feed-url">Another app? Subscribe by URL with <code>{FEED}</code></p>
      <p style="margin-top:var(--s6); font-size:var(--t-sm); color:var(--ink-3)">Built by LITSA
      from <a href="{SOURCE}">Suffolk&rsquo;s published academic calendar</a>. Suffolk&rsquo;s
      page is the official version. The source is in
      <a href="https://github.com/suffolklitsa/suffolk-guides">suffolk-guides</a>.</p>
    </div>
  </div>
</section>
{sh.step()}
"""

def render():
    return sh.page("Academic calendar · LITSA",
        "Subscribe to Suffolk Law's 2026-27 academic calendar in Google, Apple or Outlook.",
        "/calendar/", BODY)

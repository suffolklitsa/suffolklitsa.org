import shell as sh
BODY = f"""
<section class="tight">
  <div class="wrap rail">
    <p class="rail-label">404</p>
    <div>
      <h1 style="max-width:14ch">That page does not exist.</h1>
      <p class="lede" style="margin-top:var(--s5)">It may have moved, or it may
      never have been here. Either way, the useful pages are below.</p>
      <ul style="margin-top:var(--s7); display:grid; gap:var(--s3)">
        <li><a href="/field/">What legal innovation covers</a></li>
        <li><a href="/suffolk/">What Suffolk already gives you</a></li>
        <li><a href="/build/">What we build</a></li>
        <li><a href="/history/">History, 1906 to now</a></li>
        <li><a href="/join/">Join</a></li>
      </ul>
    </div>
  </div>
</section>
{sh.step()}
"""
def render():
    return sh.page("Not found · LITSA", "That page does not exist.", "/404", BODY)

# -*- coding: utf-8 -*-
"""/me/ — stop counting this browser's visits.

Not linked anywhere. At five to fifteen real visits a day, the board's own clicking
is a large share of the numbers, so each of us opens this once per browser and device.
It sets a localStorage flag that the page-view loader (shell.py) and the click counter
(analytics.js) both check. Clearing site data or a private window counts again.
"""
import shell as sh

BODY = """
<section class="wrap" style="max-width:62ch">
  <h1>Don&rsquo;t count me</h1>
  <p class="lede" style="margin-top:var(--s5)">For LITSA board members. Press the button once
  in each browser you use, on each device, and your visits stop showing up in the site&rsquo;s
  numbers. A private window, or clearing this site&rsquo;s data, starts counting again.</p>
  <p id="me-state" class="lede" style="margin-top:var(--s6)"><b>Checking&hellip;</b></p>
  <div style="display:flex; gap:var(--s4); flex-wrap:wrap; margin-top:var(--s5)">
    <button class="btn btn--solid" id="me-off" type="button">Stop counting this browser</button>
    <button class="btn btn--ghost" id="me-on" type="button">Count me again</button>
  </div>
</section>
<script>
(function () {
  var KEY = "litsa.notrack", state = document.getElementById("me-state");
  function show() {
    var off = false;
    try { off = localStorage.getItem(KEY) === "1"; } catch (e) {
      state.innerHTML = "<b>This browser blocks site storage, so it can\u2019t be excluded.</b>"; return;
    }
    state.innerHTML = off ? "<b>This browser is not counted.</b>" : "<b>This browser is counted.</b>";
  }
  document.getElementById("me-off").onclick = function () { try { localStorage.setItem(KEY, "1"); } catch (e) {} show(); };
  document.getElementById("me-on").onclick = function () { try { localStorage.removeItem(KEY); } catch (e) {} show(); };
  show();
})();
</script>
"""


def render():
    return sh.page("Don't count me — LITSA", "Exclude this browser from the site's visit counts.",
                   "/me/", BODY, reference=True)

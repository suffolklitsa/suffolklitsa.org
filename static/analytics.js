/* LITSA analytics. Provider-agnostic: it queues events and flushes to whichever
   backend is configured. Nothing here blocks rendering, and it no-ops cleanly
   if no backend is set. */
(function () {
  var CFG = window.LITSA_ANALYTICS || {};
  var POSTHOG_KEY  = CFG.posthogKey  || null;
  var POSTHOG_HOST = CFG.posthogHost || "https://us.i.posthog.com";

  var page = location.pathname;
  var OFF = false;
  try { OFF = localStorage.getItem("litsa.notrack") === "1"; } catch (_) {}
  if (location.pathname.indexOf("/me/") === 0) OFF = true;

  /* A click that leaves the site (SUConnect, an email, a competition's own page) is
     the closest thing this site has to a conversion. Counterscale only counts page
     views, so each one is sent as a view of /out/<where it went>, with the page it
     came from in the referrer field. The weekly digest reads them back from there. */
  function outPath(href) {
    if (/^mailto:/i.test(href)) {
      return "/out/email/" + href.slice(7).split("?")[0].split("@")[0].toLowerCase();
    }
    var m = /^https?:\/\/([^\/?#]+)([^?#]*)/i.exec(href);
    if (!m || /(^|\.)suffolklitsa\.org$/i.test(m[1])) return null;
    if (/suffolk\.campuslabs\.com$/i.test(m[1])) return "/out/suconnect";
    return ("/out/" + m[1].replace(/^www\./, "") + m[2]).replace(/\/+$/, "").slice(0, 160);
  }
  /* Counterscale only counts page views, so anything else is sent as a view of a made-up
     path with the real page in the referrer field: /out/... for clicks, /depth/<pct> for how
     far down the page someone got, /time/<bucket> for how long they stayed. */
  function hit(p) {
    if (OFF || !p) return;
    var u = "https://analytics.suffolklitsa.org/collect?sid=litsa" +
      "&h=" + encodeURIComponent("https://suffolklitsa.org") +
      "&p=" + encodeURIComponent(p) + "&r=" + encodeURIComponent(page);
    try { fetch(u, { mode: "no-cors", keepalive: true }); }
    catch (_) { (new Image()).src = u; }
  }
  function countOut(href) { hit(outPath(href)); }
  var t0 = Date.now();
  var maxScroll = 0;
  var sent = false;

  function track(name, props) {
    props = props || {};
    props.path = page;
    props.$current_url = location.href;
    if (window.posthog && window.posthog.capture) {
      window.posthog.capture(name, props);
    }
    (window.dataLayer = window.dataLayer || []).push(
      Object.assign({ event: name }, props));
  }
  window.litsaTrack = track;

  /* --- PostHog, loaded only if a key is configured ------------------- */
  if (POSTHOG_KEY) {
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){
    function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]);
    t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}
    (p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",
    p.async=!0,p.src=s.api_host+"/static/array.js",
    (r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);
    var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],
    u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),
    t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},
    o="init me ws ys ps bs capture je Di ks register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty Ss xs createPersonProfile Es gs opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing ys debug ks getPageViewId captureTraceFeedback captureTraceMetric".split(" "),
    n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      capture_pageview: true,
      capture_pageleave: true,
      autocapture: true,
      persistence: "localStorage+cookie"
    });
  }

  /* --- scroll depth --------------------------------------------------
     Each quarter is sent once, as it is crossed, so a phone closing the tab does not lose
     it. Within 2% of the bottom counts as the bottom. A page that fits on one screen
     sends nothing. */
  var MARKS = [25, 50, 75, 100], marked = {};
  addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight;
    if (h <= 0) return;
    var pct = Math.min(100, Math.round(scrollY / h * 100));
    if (pct > maxScroll) maxScroll = pct;
    for (var i = 0; i < MARKS.length; i++) {
      if (pct >= MARKS[i] - 2 && !marked[MARKS[i]]) {
        marked[MARKS[i]] = 1;
        hit("/depth/" + MARKS[i]);
      }
    }
  }, { passive: true });

  /* --- clicks worth knowing about ------------------------------------ */
  addEventListener("click", function (e) {
    var a = e.target.closest("a, button");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var label = (a.textContent || "").trim().slice(0, 60);
    countOut(href);
    if (a.matches(".btn, .cta")) {
      track("cta_click", { label: label, href: href });
    } else if (/^https?:/.test(href) && !href.includes("suffolklitsa.org")) {
      track("outbound_click", { label: label, href: href,
        host: (href.split("/")[2] || "") });
    } else if (a.matches("[data-filter]")) {
      track("field_filter", { level: a.getAttribute("data-filter") });
    } else if (href.startsWith("mailto:")) {
      track("email_click", { href: href });
    } else if (href.startsWith("/")) {
      track("internal_nav", { label: label, href: href });
    }
  }, true);

  /* --- dwell time and depth, on the way out -------------------------- */
  function bucket(s) {
    return s < 10 ? "0-10s" : s < 30 ? "10-30s" : s < 60 ? "30-60s" :
      s < 180 ? "1-3m" : s < 600 ? "3-10m" : "10m+";
  }
  function leave() {
    if (sent) return; sent = true;
    var seconds = Math.round((Date.now() - t0) / 1000);
    hit("/time/" + bucket(seconds));
    track("page_exit", { seconds: seconds, scroll_pct: maxScroll });
  }
  addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") leave();
  });
  addEventListener("pagehide", leave);
})();

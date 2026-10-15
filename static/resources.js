/* Filters, the section picker, and the assistant entry point.
   Everything here is progressive: with JS off the page is a complete,
   readable list. Nothing is fetched and nothing leaves the browser. */
(function () {
  "use strict";

  /* ---------------------------------------------------------------- filters */
  function wireFilters(barId, rowsId, countId, match) {
    var bar = document.getElementById(barId);
    var rows = document.getElementById(rowsId);
    var count = document.getElementById(countId);
    if (!bar || !rows) return;
    var items = [].slice.call(rows.children);
    var active = {};

    function apply() {
      var shown = 0;
      for (var i = 0; i < items.length; i++) {
        var ok = match(items[i], active);
        items[i].hidden = !ok;
        if (ok) shown++;
      }
      if (count) count.innerHTML = "Showing <b>" + shown + "</b> of " + items.length;
      rows.setAttribute("aria-busy", "false");
    }

    bar.addEventListener("click", function (e) {
      var b = e.target.closest(".chip");
      if (!b) return;
      var f = b.dataset.f, v = b.dataset.v;
      active[f] = active[f] || [];
      var at = active[f].indexOf(v);
      if (at === -1) { active[f].push(v); b.setAttribute("aria-pressed", "true"); }
      else { active[f].splice(at, 1); b.setAttribute("aria-pressed", "false"); }
      if (!active[f].length) delete active[f];
      apply();
      // Reflect filter state in the URL so a filtered view can be linked and
      // so analytics sees a distinct path rather than one undifferentiated hit.
      var q = [];
      for (var k in active) q.push(k + "=" + active[k].map(encodeURIComponent).join(","));
      history.replaceState(null, "", location.pathname + (q.length ? "?" + q.join("&") : ""));
    });

    // Restore filters from the URL, so a shared link opens filtered.
    var params = new URLSearchParams(location.search);
    params.forEach(function (val, key) {
      val.split(",").forEach(function (v) {
        var b = bar.querySelector('.chip[data-f="' + key + '"][data-v="' + CSS.escape(v) + '"]');
        if (b) { active[key] = active[key] || []; active[key].push(v); b.setAttribute("aria-pressed", "true"); }
      });
    });
    if (Object.keys(active).length) apply();
  }

  function has(list, wanted) {
    for (var i = 0; i < wanted.length; i++) if (list.indexOf(wanted[i]) !== -1) return true;
    return false;
  }

  wireFilters("db-filters", "db-rows", "db-count", function (el, active) {
    if (active.access && active.access.indexOf(el.dataset.access) === -1) return false;
    if (active.subject && !has((el.dataset.subjects || "").split("|"), active.subject)) return false;
    return true;
  });

  wireFilters("crs-filters", "crs-rows", "crs-count", function (el, active) {
    if (active.term && active.term.indexOf(el.dataset.term) === -1) return false;
    if (active.mode && active.mode.indexOf(el.dataset.mode) === -1) return false;
    if (active.areas && !has((el.dataset.areas || "").split("|"), active.areas)) return false;
    if (active.flags && !has((el.dataset.flags || "").split("|"), active.flags)) return false;
    return true;
  });

  /* --------------------------------------------------- the section picker */
  var KEY = "litsa.cohort";
  var picker = document.getElementById("picker");
  if (picker) {
    var out = document.getElementById("mine-out");
    var cards = [].slice.call(document.querySelectorAll("#subject-cards .card"));

    function highlight(cohort) {
      var data = window.LITSA_SECTIONS || {};
      var mine = data[cohort];
      cards.forEach(function (c) { c.classList.remove("mine"); });
      if (!mine) { if (out) out.hidden = true; return; }
      var now = new Date().getMonth() >= 6 && new Date().getMonth() <= 11 ? "fall" : "spring";
      var titles = (mine[now] || []).concat(mine[now === "fall" ? "spring" : "fall"] || []);
      var thisTerm = mine[now] || [];
      cards.forEach(function (c) {
        if (thisTerm.indexOf(c.dataset.subject) !== -1) c.classList.add("mine");
      });
      if (out) {
        out.hidden = false;
        var cs = mine.courses || {};
        var nxt = now === "fall" ? "spring" : "fall";
        out.innerHTML = "Section <b>" + cohort + "</b>. This term: <b>" +
          ((cs[now] || thisTerm).join(", ") || "nothing listed") + "</b>. Next term: <b>" +
          ((cs[nxt] || mine[nxt] || []).join(", ") || "nothing listed") +
          "</b>. <a href=\"#coursework\">Jump to your subjects</a>.";
      }
      // Move the student's own subjects to the front of the list.
      var parent = document.getElementById("subject-cards");
      cards.slice().reverse().forEach(function (c) {
        if (c.classList.contains("mine")) parent.insertBefore(c, parent.firstChild);
      });
    }

    // Year first. 1Ls have a section; everyone else picks an area of focus.
    function showBranch(year) {
      ["1L", "upper"].forEach(function (y) {
        var el = document.getElementById("branch-" + y);
        if (el) el.hidden = y !== year;
      });
    }

    function focusLabel(name, subs) {
      var note = (window.LITSA_FOCUS_NOTE || {})[name];
      return "<b>" + name + "</b>. Subjects: <b>" + (subs.join(", ") || "none mapped") + "</b>." +
        (note ? " " + note : "");
    }

    function highlightSubjects(list, label) {
      cards.forEach(function (c) { c.classList.remove("mine"); });
      (list || []).forEach(function (name) {
        var c = cards.filter(function (x) { return x.dataset.subject === name; })[0];
        if (c) c.classList.add("mine");
      });
      var parent = document.getElementById("subject-cards");
      cards.slice().reverse().forEach(function (c) {
        if (c.classList.contains("mine")) parent.insertBefore(c, parent.firstChild);
      });
      if (out) {
        out.hidden = false;
        out.innerHTML = label + ' <a href="#coursework">Jump to your subjects</a>.';
      }
    }

    picker.addEventListener("click", function (e) {
      var y = e.target.closest("[data-year]");
      if (y) {
        picker.querySelectorAll("[data-year]").forEach(function (x) {
          x.setAttribute("aria-pressed", String(x === y));
        });
        showBranch(y.dataset.year);
        try { localStorage.setItem(KEY + ".year", y.dataset.year); } catch (_) {}
        return;
      }
      var f = e.target.closest("[data-focus]");
      if (f) {
        var on = f.getAttribute("aria-pressed") === "true";
        picker.querySelectorAll("[data-focus]").forEach(function (x) {
          x.setAttribute("aria-pressed", "false");
        });
        if (on) { try { localStorage.removeItem(KEY + ".focus"); } catch (_) {} highlightSubjects([], ""); return; }
        f.setAttribute("aria-pressed", "true");
        try { localStorage.setItem(KEY + ".focus", f.dataset.focus); } catch (_) {}
        var subs = (window.LITSA_FOCUS || {})[f.dataset.focus] || [];
        highlightSubjects(subs, focusLabel(f.dataset.focus, subs));
        return;
      }
      var b = e.target.closest("[data-cohort]");
      if (!b) return;
      var on = b.getAttribute("aria-pressed") === "true";
      picker.querySelectorAll("[data-cohort]").forEach(function (x) {
        x.setAttribute("aria-pressed", "false");
      });
      if (on) { try { localStorage.removeItem(KEY); } catch (_) {} highlight(null); return; }
      b.setAttribute("aria-pressed", "true");
      try { localStorage.setItem(KEY, b.dataset.cohort); } catch (_) {}
      highlight(b.dataset.cohort);
    });

    var saved = null, savedYear = null, savedFocus = null;
    try {
      saved = localStorage.getItem(KEY);
      savedYear = localStorage.getItem(KEY + ".year");
      savedFocus = localStorage.getItem(KEY + ".focus");
    } catch (_) {}
    if (savedYear) {
      var yb = picker.querySelector('[data-year="' + savedYear + '"]');
      if (yb) yb.setAttribute("aria-pressed", "true");
      showBranch(savedYear);
    }
    if (saved) {
      var b0 = picker.querySelector('[data-cohort="' + saved + '"]');
      if (b0) { b0.setAttribute("aria-pressed", "true"); highlight(saved); }
    }
    if (savedFocus) {
      var fb = picker.querySelector('[data-focus="' + CSS.escape(savedFocus) + '"]');
      if (fb) {
        fb.setAttribute("aria-pressed", "true");
        var fs = (window.LITSA_FOCUS || {})[savedFocus] || [];
        highlightSubjects(fs, focusLabel(savedFocus, fs));
      }
    }
  }

  /* --------------------------------------------- assistant entry point */
  var cfg = window.LITSA_ASSISTANT;
  if (cfg && cfg.url && !document.getElementById("ask")) {
    var ask = document.createElement("a");
    ask.id = "ask";
    ask.href = cfg.url;
    ask.rel = "noopener";
    ask.innerHTML = '<span class="ask-i" aria-hidden="true">?</span>' +
                    '<span class="ask-t">' + (cfg.label || "Ask") + '</span>';
    ask.setAttribute("aria-label", cfg.hint || cfg.label || "Ask a question");
    document.body.appendChild(ask);
  }
})();

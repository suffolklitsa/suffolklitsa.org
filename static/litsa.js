/* Delights. Every one degrades to a working page if this file never loads. */
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* --- scroll progress, stepped ------------------------------------- */
  var prog = document.createElement("div");
  prog.id = "prog"; document.body.appendChild(prog);
  function onScroll() {
    var h = document.documentElement.scrollHeight - innerHeight;
    var pct = h > 0 ? scrollY / h : 0;
    prog.style.width = (Math.round(pct * 20) / 20 * 100).toFixed(0) + "%";
  }
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  /* --- the measurement grid overlay --------------------------------- */
  var grid = document.createElement("div");
  grid.id = "grid";
  var inner = "";
  for (var i = 1; i < 12; i++) inner += '<div class="col" style="left:' + (i * 100 / 12) + '%"></div>';
  for (var y = 0; y < 60; y++) inner += '<div class="u" style="top:' + (y * 48) + 'px"></div>';
  inner += '<div class="badge">GRID &middot; 12u &middot; PRESS G</div>';
  grid.innerHTML = inner; document.body.appendChild(grid);

  addEventListener("keydown", function (e) {
    var tg = e.target;
    if (tg && tg.matches && tg.matches("input,textarea")) return;
    var k = e.key.toLowerCase();
    if (k === "g") { document.body.classList.toggle("grid-on");
      window.litsaTrack && window.litsaTrack("grid_toggle", {on: document.body.classList.contains("grid-on")}); }
    if (k === "l" && e.shiftKey) document.body.classList.toggle("grid-on");
  });

  /* --- torch assembles module by module, once per session ----------- */
  var mast = document.querySelector(".masthead .mark svg.torch");
  if (mast && !reduce && !sessionStorage.getItem("litsa-lit")) {
    var rects = [].slice.call(mast.querySelectorAll("rect"));
    rects.forEach(function (r, i) {
      r.style.opacity = 0;
      setTimeout(function () {
        r.style.transition = "opacity .18s steps(2)"; r.style.opacity = 1;
      }, 120 + i * 14);
    });
    sessionStorage.setItem("litsa-lit", "1");
  }

  /* --- field page: filter domains by how much code they need -------- */
  var filters = document.querySelectorAll("[data-filter]");
  if (filters.length) {
    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var lvl = btn.getAttribute("data-filter");
        var on = btn.getAttribute("aria-pressed") === "true";
        filters.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        var cards = document.querySelectorAll(".dom");
        if (on) { cards.forEach(function (c) { c.classList.remove("dim"); }); return; }
        btn.setAttribute("aria-pressed", "true");
        cards.forEach(function (c) {
          c.classList.toggle("dim", c.getAttribute("data-level") !== lvl);
        });
      });
    });
  }

  /* --- copy the citation ------------------------------------------- */
  var cite = document.querySelector("[data-cite]");
  if (cite) {
    cite.addEventListener("click", function () {
      navigator.clipboard && navigator.clipboard.writeText(cite.dataset.cite);
      var was = cite.textContent; cite.textContent = "Copied to clipboard";
      setTimeout(function () { cite.textContent = was; }, 1600);
    });
  }
})();

/* bar bands describe themselves */
(function(){
  var out = document.getElementById("barout");
  if (!out) return;
  var idle = out.textContent;
  document.querySelectorAll(".bar span[data-fields]").forEach(function(b){
    function show(){ out.innerHTML = "<b>" + b.dataset.lab + "</b>" + b.dataset.fields + "."; }
    function hide(){ out.textContent = idle; }
    b.addEventListener("mouseenter", show); b.addEventListener("focus", show);
    b.addEventListener("mouseleave", hide); b.addEventListener("blur", hide);
  });
})();

/* ===================== delights, second pass ========================== */
(function () {
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* compact masthead + back-to-top */
  var top = document.createElement("button");
  top.id = "totop"; top.type = "button"; top.textContent = "TOP";
  top.setAttribute("aria-label", "Back to top");
  top.addEventListener("click", function () {
    scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
  });
  document.body.appendChild(top);
  addEventListener("scroll", function () {
    document.body.classList.toggle("scrolled", scrollY > 220);
  }, { passive: true });

  /* copy-link anchors on every h2 and h3 */
  var n = 0;
  document.querySelectorAll("main h2, main h3").forEach(function (h) {
    if (!h.id) {
      h.id = (h.textContent || "s").toLowerCase().replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "").slice(0, 40) || ("s" + (++n));
    }
    var a = document.createElement("a");
    a.className = "anchor"; a.href = "#" + h.id; a.textContent = "¶";
    a.setAttribute("aria-label", "Link to this section");
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var url = location.origin + location.pathname + "#" + h.id;
      history.replaceState(null, "", "#" + h.id);
      navigator.clipboard && navigator.clipboard.writeText(url);
      a.textContent = "copied"; setTimeout(function(){ a.textContent = "¶"; }, 1400);
      window.litsaTrack && window.litsaTrack("anchor_copy", { id: h.id });
    });
    h.appendChild(a);
  });

  /* reading time, on long pages only */
  var main = document.getElementById("main");
  if (main && !document.body.hasAttribute("data-no-readtime")) {
    var words = (main.textContent || "").trim().split(/\s+/).length;
    if (words > 500) {
      var mins = Math.max(1, Math.round(words / 220));
      var lede = main.querySelector(".lede");
      if (lede) {
        var rt = document.createElement("p");
        rt.className = "readtime";
        rt.textContent = mins + " min read · " + words.toLocaleString() + " words";
        lede.parentNode.insertBefore(rt, lede.nextSibling);
      }
    }
  }

  /* scroll-spy for the history timeline */
  var acts = [].slice.call(document.querySelectorAll(".act[id]"));
  if (acts.length > 2) {
    var rail = document.querySelector(".rail-label");
    if (rail) {
      var spy = document.createElement("nav");
      spy.className = "spy"; spy.setAttribute("aria-label", "Timeline");
      spy.innerHTML = acts.map(function (a) {
        var yr = a.querySelector(".yr");
        var lbl = (yr.querySelector("a") ? yr.querySelector("a").textContent
                   : yr.firstChild.textContent).trim();
        return '<a href="#' + a.id + '">' + lbl + "</a>";
      }).join("");
      rail.appendChild(spy);
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          var link = spy.querySelector('a[href="#' + e.target.id + '"]');
          if (link) link.classList.toggle("on", e.isIntersecting);
        });
      }, { rootMargin: "-25% 0px -60% 0px" });
      acts.forEach(function (a) { io.observe(a); });
    }
  }

  /* keyboard shortcut sheet */
  var keys = document.createElement("div");
  keys.id = "keys"; keys.setAttribute("role", "dialog");
  keys.setAttribute("aria-label", "Keyboard shortcuts");
  keys.innerHTML = '<div class="card"><h3>Keyboard</h3><dl>' +
    '<dt>G</dt><dd>Show the measurement grid this site is drawn on</dd>' +
    '<dt>?</dt><dd>This sheet</dd>' +
    '<dt>ESC</dt><dd>Close</dd></dl>' +
    '<p class="small" style="margin-top:18px">Type <b>litsa</b> anywhere to light the torches.</p></div>';
  document.body.appendChild(keys);
  keys.addEventListener("click", function(){ document.body.classList.remove("keys-on"); });

  /* easter egg: type litsa */
  var buf = "";
  addEventListener("keydown", function (e) {
    var tg = e.target;
    if (tg && tg.matches && tg.matches("input,textarea")) return;
    var k = e.key.toLowerCase();
    if (k === "escape") { document.body.classList.remove("keys-on", "search-on"); return; }
    if (k === "?" || (k === "/" && e.shiftKey)) {
      document.body.classList.toggle("keys-on"); e.preventDefault(); return;
    }
    if (k.length !== 1) return;           // ignore Shift, Meta, arrows and friends
    buf = (buf + k).slice(-5);
    if (buf === "litsa") {
      var gold = [].slice.call(document.querySelectorAll("svg rect")).filter(function (r) {
        return (r.getAttribute("fill") || "").toLowerCase() === "#e5ad2d";
      });
      gold.forEach(function (r, i) {
        setTimeout(function () {
          var was = r.getAttribute("fill");
          r.setAttribute("fill", "#FFD25E");
          setTimeout(function () { r.setAttribute("fill", was); }, 1100);
        }, i * 4);
      });
      var toast = document.createElement("div");
      toast.id = "toast"; toast.textContent = "The torches are lit.";
      document.body.appendChild(toast);
      setTimeout(function () { toast.remove(); }, 2200);
      window.litsaTrack && window.litsaTrack("easter_egg", { name: "litsa" });
    }
  });
})();

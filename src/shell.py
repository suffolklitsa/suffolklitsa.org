"""Page shell: head, masthead, footer, and the identity SVGs."""
import json as _json
from urllib.parse import quote as _quote
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import glyphs as G, torch as T, emit as E, variants as V

G.TRACK = 2.45

_STATIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


def _v(name):
    """/name?v=<content hash>. Pages cache for four hours; without this a deploy that
    changes markup and CSS together shows new markup with last deploy's CSS."""
    import hashlib
    with open(os.path.join(_STATIC, name), "rb") as fh:
        return f"/{name}?v={hashlib.sha1(fh.read()).hexdigest()[:10]}"
INK, GOLD, BLUE, PAPER = "#18212F", "#E5AD2D", "#1769E0", "#F7F8FA"

# Top nav carries what a student came for. History, Partners and Contact still
# exist and still ship in the footer; seven items in a bar is a list, not a nav.
# The logo is the way home, so Home is not in the list.
NAV = [("/resources/", "Resources"), ("/curriculum/", "Curriculum"), ("/events/", "Events"),
       ("/compete/", "Compete"), ("/watch/", "Watching"), ("/suffolk/", "At Suffolk"),
       ("/build/", "What we build")]
FOOT_NAV = NAV + [("/field/", "The field"), ("/history/", "History"),
                  ("/partners/", "Partners"), ("/contact/", "Contact")]
# The footer groups the same pages by what a visitor came to do.
FOOT_GROUPS = [
    ("Learn", [("/resources/", "Resources"), ("/curriculum/", "Curriculum"), ("/field/", "The field"),
               ("/watch/", "Watching")]),
    ("Do", [("/events/", "Events"), ("/compete/", "Compete"), ("/planner/", "Course planner"), ("/build/", "What we build"),
            ("/join/", "Join")]),
    ("About", [("/suffolk/", "At Suffolk"), ("/history/", "History"), ("/partners/", "Partners"),
               ("/contact/", "Contact")]),
]

def torch_animated(cls="live"):
    """The colour torch, flickering. Four sprite frames cycled with CSS steps;
    the bowl and shaft are static, only the flame moves."""
    frames = T.flame_frames(4)
    gs = "".join('<g class="fr fr%d">%s</g>' % (i, E.rects(g)) for i, g in enumerate(frames))
    return ('<svg class="%s" viewBox="-1 -1 24 46" role="img" '
            'aria-label="The LITSA torch, burning" shape-rendering="crispEdges">%s</svg>'
            % (cls, gs))

def torch_flat(cls="", colour="#EFE0BE"):
    """Solid single-tint silhouette for architectural-scale use. Flat, never
    an opacity fade."""
    import numpy as _np
    g = T.final(44).copy()
    for r in range(26):                      # fill the flame solid, no knockout
        w = _np.where(g[r])[0]
        if len(w): g[r, w.min():w.max()+1] = T.G
    return ('<svg class="%s" viewBox="-1 -1 24 46" aria-hidden="true" '
            'shape-rendering="crispEdges">%s</svg>'
            % (cls, E.rects(g, mono=colour)))

def torch_svg(cls="torch", mono=None, ink_as=None):
    g = T.final(44)
    body = E.rects(g, mono=mono)
    if ink_as and not mono:
        body = body.replace('fill="%s"' % T.INK, 'fill="%s"' % ink_as)
    return ('<svg class="%s" viewBox="-1 -1 24 46" role="img" aria-label="LITSA torch" '
            'shape-rendering="crispEdges">%s</svg>' % (cls, body))

def word_svg(cls="word", fill=INK, label="LITSA"):
    svg, box = V.v0()
    inner = svg.split(">\n", 1)[1].rsplit("</svg>", 1)[0]
    inner = inner.replace('fill="#18212f"', 'fill="%s"' % fill)
    x0, y0, x1, y1 = box
    return ('<svg class="%s" viewBox="%.2f %.2f %.2f %.2f" role="img" aria-label="%s" '
            'shape-rendering="crispEdges">%s</svg>'
            % (cls, x0-0.5, y0-0.5, (x1-x0)+1, (y1-y0)+1, label, inner))

def step(colour=GOLD, w=1200):
    """The identity's stair-step, used wherever structure changes."""
    return ('<div class="step" aria-hidden="true"><svg viewBox="0 0 %d 14" '
            'preserveAspectRatio="none" shape-rendering="crispEdges">'
            '<rect x="0" y="0" width="64" height="14" fill="%s"/>'
            '<rect x="64" y="5" width="44" height="9" fill="%s"/>'
            '<rect x="108" y="10" width="%d" height="4" fill="%s"/>'
            '</svg></div>' % (w, colour, colour, w-108, colour))

def head(title, desc, path, bodyattr=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://suffolklitsa.org{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://suffolklitsa.org{path}">
<meta name="theme-color" content="{PAPER}">
<link rel="stylesheet" href="{_v("litsa.css")}">
<link rel="preload" href="/font/LITSADisplay.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/font/literata-roman.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:image" content="https://suffolklitsa.org/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="view-transition" content="same-origin">
<link rel="dns-prefetch" href="https://suffolk.campuslabs.com">
<link rel="dns-prefetch" href="https://suffolklitlab.org">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Organization",
"name":"Legal Innovation and Technology Student Association","alternateName":"LITSA",
"url":"https://suffolklitsa.org","email":"sam.darkwa@su.suffolk.edu",
"logo":"https://suffolklitsa.org/og.png",
"parentOrganization":{{"@type":"CollegeOrUniversity","name":"Suffolk University Law School"}},
"sameAs":["https://www.instagram.com/litsa_suls/",
"https://www.linkedin.com/company/suffolk-law-school-legal-innovation-technology-student-association",
"https://suffolk.campuslabs.com/engage/organization/litsa"]}}</script>
</head>
<body{bodyattr}>
<a class="skip" href="#main">Skip to content</a>
'''

def masthead(path):
    links = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == path else "", t)
        for h, t in NAV)
    return f'''<header class="masthead">
  <div class="wrap bar">
    <a class="mark" href="/" aria-label="LITSA home">
      {torch_svg()}{word_svg()}
    </a>
    <nav aria-label="Primary">{links}<a class="cta" href="/join/">Join</a></nav>
    <a class="cta mcta" href="/join/">Join</a>
    <details class="mnav"><summary>Menu</summary>
      <nav aria-label="Primary, small screens">{links}</nav></details>
  </div>
</header>
<main id="main">
'''

def footer(extra=""):
    word_big = word_svg(cls="", label="")
    return f'''</main>
<footer class="foot">
  <div class="wrap cols">
    <div>
      <p class="fh">LITSA</p>
      <p class="small" style="max-width:38ch">Legal Innovation &amp; Technology
      Student Association at Suffolk University Law School, Boston.</p>
      <p class="small" style="margin-top:16px"><a href="mailto:sam.darkwa@su.suffolk.edu">sam.darkwa@su.suffolk.edu</a></p>
    </div>
{"".join('<div><p class="fh">%s</p><ul>%s</ul></div>' % (head, "".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in links)) for head, links in FOOT_GROUPS)}
    <div>
      <p class="fh">Elsewhere</p>
      <ul>
        <li><a href="https://suffolk.campuslabs.com/engage/organization/litsa">SUConnect</a></li>
        <li><a href="https://www.instagram.com/litsa_suls/">Instagram</a></li>
        <li><a href="https://www.linkedin.com/company/suffolk-law-school-legal-innovation-technology-student-association">LinkedIn</a></li>
        <li><a href="https://suffolklitlab.org">Suffolk LIT Lab</a></li>
        <li><a href="https://sites.suffolk.edu/legaltech/">LIT Center</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap">
    <p class="small" style="margin-top:32px">Press <span class="kbd">G</span> for
    the grid this site is drawn on, or <span class="kbd">?</span> for everything else.</p>
    <div class="bigmark" aria-hidden="true">{word_big}</div>
  </div>
</footer>
<script>window.LITSA_ANALYTICS={{posthogKey:null,posthogHost:"https://us.i.posthog.com"}};</script>
{extra}
<script src="{_v("analytics.js")}" defer></script>
<script>/* Page views go to Counterscale unless this browser opted out at /me/. */
(function () {{
  var off = false;
  try {{ off = localStorage.getItem("litsa.notrack") === "1"; }} catch (e) {{}}
  if (off || location.pathname.indexOf("/me/") === 0) return;
  var s = document.createElement("script");
  s.id = "counterscale-script"; s.defer = true;
  s.setAttribute("data-site-id", "litsa");
  s.src = "https://analytics.suffolklitsa.org/tracker.js";
  document.head.appendChild(s);
}})();</script>
<script src="{_v("litsa.js")}" defer></script>
<script src="{_v("resources.js")}" defer></script>
</body>
</html>
'''

WM = {"/history/":  "top:-6%; right:-9%; width:min(24vw,300px);",
      "/suffolk/":  "bottom:-12%; left:-6%; width:min(20vw,240px);",
      "/field/":    "top:2%; right:-11%; width:min(22vw,270px);",
      "/build/":    "bottom:-14%; right:-7%; width:min(21vw,255px);",
      "/contact/":  "top:-4%; right:-8%; width:min(19vw,230px);",
      "/partners/": "bottom:-10%; right:-9%; width:min(20vw,245px);",
      "/join/":     "top:0%; right:-10%; width:min(20vw,245px);"}

def watermark(path):
    if path not in WM:
        return ""
    return ('<div class="mark-wm" style="%s">%s</div>'
            % (WM[path], torch_flat(colour="#EEF1F5")))

def scene(src, alt, caption, eager=False, size=(2172, 724)):
    priority = ' fetchpriority="high"' if eager else ' loading="lazy"'
    return (f'<figure class="editorial-scene"><img src="/img/{src}" '
            f'width="{size[0]}" height="{size[1]}" alt="{alt}"{priority}>'
            f'<figcaption>{caption}</figcaption></figure>')

ASSISTANT = {"url": "https://chat.suffolklitsa.org",
             "label": "Ask about this",
             "hint": "The Suffolk assistant can answer questions about these resources."}


def assistant_config(seed=None):
    """Persistent entry point to the Suffolk assistant.

    The seed rides along as /chat?q= so a click from a subject page arrives with
    the question already typed into the composer (the visitor still presses send).
    /chat, not the root: the root is the assistant's landing page, which drops it.
    """
    url = ASSISTANT["url"]
    if seed:
        url += "/chat?q=" + _quote(seed)
    return ('<script>window.LITSA_ASSISTANT=%s;</script>'
            % _json.dumps(dict(ASSISTANT, url=url)))


def page(title, desc, path, body, extra="", assistant_seed=None, reference=False):
    extra = (extra or "") + assistant_config(assistant_seed)
    bodyattr = ' data-no-readtime' if reference else ""
    return (head(title, desc, path, bodyattr) + masthead(path)
            + watermark(path) + body + footer(extra))

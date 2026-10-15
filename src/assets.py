"""Generated static assets: OG image, animated favicon, manifest, sitemap."""
import os, subprocess, json
import shell as sh, torch as T, emit as E

INK, GOLD, PAPER = "#18212F", "#E5AD2D", "#F7F8FA"
ROUTES = ["/", "/resources/", "/curriculum/", "/curriculum/courses/", "/events/",
          "/compete/", "/watch/", "/field/", "/suffolk/", "/build/", "/history/",
          "/join/", "/partners/", "/contact/"]

def og_image(out):
    """1200x630 social card, drawn from the identity rather than a screenshot."""
    torch = E.rects(T.final(44))
    word = sh.word_svg(cls="", fill=PAPER)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" '
           f'viewBox="0 0 1200 630" shape-rendering="crispEdges">'
           f'<rect width="1200" height="630" fill="{INK}"/>'
           f'<rect x="0" y="0" width="1200" height="14" fill="{GOLD}"/>'
           f'<g transform="translate(96,150) scale(8.4)">{torch}</g>'
           f'<g transform="translate(360,232) scale(9.1)">'
           f'{word.split(">",1)[1].rsplit("</svg>",1)[0]}</g>'
           f'<text x="362" y="430" fill="#C3CCD8" font-family="Helvetica,Arial" '
           f'font-size="30">Legal Innovation &amp; Technology Student Association</text>'
           f'<text x="362" y="474" fill="{GOLD}" font-family="Helvetica,Arial" '
           f'font-size="26" letter-spacing="2">SUFFOLK UNIVERSITY LAW SCHOOL</text>'
           f'</svg>')
    p = os.path.join(out, "og.svg"); open(p, "w").write(svg)
    png = os.path.join(out, "og.png")
    # rsvg-convert where it exists (the laptop); headless Chrome on sam-dev, which has no
    # rsvg. Without one of them every link preview on LinkedIn goes out with no image, so
    # say so loudly rather than skip it.
    renderers = [["rsvg-convert", "-w", "1200", p, "-o", png],
                 ["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                  "--hide-scrollbars", "--window-size=1200,630", f"--screenshot={png}",
                  "file://" + os.path.abspath(p)]]
    for cmd in renderers:
        try:
            subprocess.run(cmd, check=True, timeout=90, capture_output=True)
            if os.path.getsize(png) > 1000:
                return
        except Exception:
            continue
    print("WARNING: og.png not rendered; link previews will have no image")

def favicon(out):
    """Animated favicon. The flame flickers even in the tab."""
    frames = T.flame_frames(4)
    gs = ""
    for i, g in enumerate(frames):
        gs += (f'<g opacity="0">{E.rects(g)}'
               f'<animate attributeName="opacity" values="1;1;0;0;0;0;0;0" '
               f'dur="0.64s" begin="{i*0.16:.2f}s" repeatCount="indefinite"/></g>')
    open(os.path.join(out, "favicon.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 24 46" '
        f'shape-rendering="crispEdges">{gs}</svg>')

def manifest(out):
    open(os.path.join(out, "site.webmanifest"), "w").write(json.dumps({
        "name": "LITSA — Legal Innovation & Technology Student Association",
        "short_name": "LITSA",
        "start_url": "/",
        "display": "browser",
        "background_color": PAPER,
        "theme_color": PAPER,
        "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]
    }, indent=2))

def sitemap(out, today):
    urls = "".join(
        f"<url><loc>https://suffolklitsa.org{r}</loc>"
        f"<lastmod>{today}</lastmod></url>" for r in ROUTES)
    open(os.path.join(out, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + urls + "</urlset>")
    open(os.path.join(out, "robots.txt"), "w").write(
        "User-agent: *\nAllow: /\n\nSitemap: https://suffolklitsa.org/sitemap.xml\n")

def build_all(out, today):
    og_image(out); favicon(out); manifest(out); sitemap(out, today)

"""LITSA wordmark, rebuilt as grid geometry measured off the selected direction.

Grid: cap height = 12u, vertical stroke = 3u, horizontal stroke ~2.25u.
Every glyph is a list of (x, y, w, h) rects in units, origin at glyph top-left.
Change a constant here and all variants reflow together.
"""

INK  = "#0d203a"
GOLD = "#e5ad2d"
BLUE = "#1769e0"

CAP     = 12.0     # cap height in units
VS      = 3.0      # vertical stroke (measured 2.97-3.08)
HS      = 2.42     # horizontal stroke, top bars (measured 2.42)
HS_BOT  = 2.15     # horizontal stroke, baseline bars (measured 2.15)
TRACK   = 2.31     # letterspacing (measured gaps: 2.15 2.26 2.31 2.53)

# glyph -> (advance width, [rects]).  All values measured off the selected
# direction, not estimated.  House rule of this face: where a horizontal meets
# a vertical it STEPS rather than joins (see the L foot and the A crossbar).
GLYPHS = {
    "L": (11.40, [
        (0,    0,    3,     12.0),   # stem
        (3,    8.59, 1.30,  3.41),   # stair step into the foot
        (0,    9.85, 11.40, 2.15),   # foot
    ]),
    "I": (3.03, [
        (0,    0,    3.03,  12.0),
    ]),
    "T": (12.61, [
        (0,    0,    12.61, 2.42),   # crossbar
        (4.73, 0,    3.03,  12.0),   # stem, centred
    ]),
    "S": (12.28, [
        (0,    0,    12.28, 2.42),   # top bar
        (0,    0,    3,     7.38),   # left stem
        (0,    5.06, 12.28, 2.32),   # middle bar
        (9.28, 5.06, 3,     6.94),   # right stem
        (0,    9.85, 12.28, 2.15),   # bottom bar
    ]),
    "A": (11.94, [
        (0,    0,    11.94, 2.42),   # top bar
        (0,    0,    3,     12.0),   # left stem
        (8.97, 0,    2.97,  12.0),   # right stem
        (4.45, 6.33, 7.49,  2.04),   # crossbar
        (3,    7.76, 1.45,  1.49),   # stair step down into the stem
    ]),
}

WORD = "LITSA"

def layout(word=WORD, track=None):
    """Return (total_width, [(letter, x_offset, rects)])."""
    track = TRACK if track is None else track   # read at call time, not def time
    out, x = [], 0.0
    for ch in word:
        adv, rects = GLYPHS[ch]
        out.append((ch, x, rects))
        x += adv + track
    return x - track, out

def rects_svg(rects, dx=0.0, dy=0.0, fill=INK):
    return "\n".join(
        '  <rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>'
        % (x + dx, y + dy, w, h, fill)
        for (x, y, w, h) in rects
    )

def svg(width, height, body, pad=0.0):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="%.3f %.3f %.3f %.3f" width="%.1f" height="%.1f">\n%s\n</svg>\n'
        % (-pad, -pad, width + 2*pad, height + 2*pad, (width+2*pad)*10, (height+2*pad)*10, body)
    )

if __name__ == "__main__":
    total, placed = layout()
    body = "\n".join(rects_svg(r, dx=x) for _, x, r in placed)
    open("build/wordmark-v0-plain.svg", "w").write(svg(total, CAP, body, pad=1.0))
    print("v0 plain: %.2fu x %.2fu  ->  build/wordmark-v0-plain.svg" % (total, CAP))

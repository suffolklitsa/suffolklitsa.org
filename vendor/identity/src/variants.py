"""LITSA sticker variants.  Every variant is generated from the same glyph
table and the same flame grid, so they stay a family."""
import numpy as np
import glyphs as G, torch as T, emit as E

INK, GOLD, BLUE, PAPER = "#18212f", "#e5ad2d", "#1769e0", "#f7f8fa"
G.TRACK = 2.45

def flame_rects(grid, mod, cx, bottom_y, mono=None):
    """Place a flame grid so its horizontal centre is cx and its base is
    bottom_y.  Returns (svg, top_y, left_x, right_x)."""
    R, C = grid.shape
    w, h = C*mod, R*mod
    x0, y0 = cx - w/2, bottom_y - h
    return (E.rects(grid, u=mod, dx=x0, dy=y0, mono=mono), y0, x0, x0+w)

def word_rects(skip=(), extra=None):
    total, placed = G.layout()
    parts=[]
    for ch, x, rects in placed:
        if ch in skip: continue
        parts.append(G.rects_svg(rects, dx=x, fill=INK))
    if extra: parts.append(extra)
    return "\n".join(parts), total, {ch:(x,rects) for ch,x,rects in placed}

def xof(ch):
    _, placed = G.layout()
    for c,x,r in placed:
        if c==ch: return x, G.GLYPHS[ch][0]
    raise KeyError(ch)

def wrap(body, x0,y0,x1,y1, pad=1.5, scale=26, bg=None):
    w,h = x1-x0+2*pad, y1-y0+2*pad
    rect = ('  <rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>\n'
            %(x0-pad,y0-pad,w,h,bg)) if bg else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.3f %.3f %.3f %.3f" '
            'width="%.0f" height="%.0f" shape-rendering="crispEdges">\n%s%s\n</svg>\n'
            %(x0-pad,y0-pad,w,h,w*scale,h*scale,rect,body))

# ------------------------------------------------------------------ v0 ------
def v0():
    body,total,_ = word_rects()
    return wrap(body, 0,0,total,G.CAP), (0,0,total,G.CAP)

# ------------------------------------------------------------------ v1 ------
def v1(mod=0.62):
    """I becomes the torch: its bar is the handle, flame rises above cap."""
    ix, iw = xof("I")
    fl,ty,fx0,fx1 = flame_rects(T.flame_duo(13), mod, ix+iw/2, -0.4)
    body,total,_ = word_rects(extra=fl)
    return wrap(body, min(0,fx0), ty, max(total,fx1), G.CAP), (min(0,fx0),ty,max(total,fx1),G.CAP)

# ------------------------------------------------------------------ v2 ------
def v2(mod=0.62):
    """T becomes the torch: the crossbar reads as the bowl."""
    tx, tw = xof("T")
    fl,ty,fx0,fx1 = flame_rects(T.flame_duo(13), mod, tx+tw/2, -0.4)
    body,total,_ = word_rects(extra=fl)
    return wrap(body, min(0,fx0), ty, max(total,fx1), G.CAP), (min(0,fx0),ty,max(total,fx1),G.CAP)

# ------------------------------------------------------------------ v3 ------
def v3(mod=0.36):
    """Flame knocked out of the I and the T stem.  Stays inside cap height.
    The flame must be tall-and-narrow: a square flame scaled to fit severs the
    3u stroke."""
    narrow = T.flame_narrow(11,5)
    ix,iw = xof("I"); tx,tw = xof("T")
    holes=[]
    for cx in (ix+iw/2, tx+4.73+3.03/2):
        r,_,_,_ = flame_rects(narrow, mod, cx, G.CAP-1.4, mono="#000")
        holes.append(r)
    body,total,_ = word_rects()
    mask = ('<mask id="k"><rect x="-2" y="-2" width="%.2f" height="%.2f" fill="#fff"/>\n%s</mask>'
            %(total+4, G.CAP+4, "\n".join(holes)))
    return wrap('<defs>%s</defs>\n<g mask="url(#k)">\n%s\n</g>'%(mask,body),
                0,0,total,G.CAP), (0,0,total,G.CAP)

# ------------------------------------------------------------------ v4 ------
def v4(mod=0.62):
    """LIT lights up: one bowl spans the I and the T, one flame above both."""
    ix,iw = xof("I"); tx,tw = xof("T")
    left, right = ix, tx+tw
    bowl = '  <rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>'%(
            left, 0, right-left, G.HS, INK)
    istem = '  <rect x="%.3f" y="0" width="%.3f" height="%.3f" fill="%s"/>'%(ix,iw,G.CAP,INK)
    tstem = '  <rect x="%.3f" y="0" width="3.03" height="%.3f" fill="%s"/>'%(tx+4.73,G.CAP,INK)
    fl,ty,fx0,fx1 = flame_rects(T.flame_duo(13), mod, (left+right)/2, -0.4)
    body,total,_ = word_rects(skip=("I","T"), extra="\n".join([bowl,istem,tstem,fl]))
    return wrap(body, min(0,fx0), ty, max(total,fx1), G.CAP), (min(0,fx0),ty,max(total,fx1),G.CAP)

def v4b(mod=0.78):
    """v4 without merging the bowl: letterforms intact, one large flame
    straddling the I-T pair.  Keeps LITSA legible; loses the 'LIT' concept."""
    ix,iw = xof("I"); tx,tw = xof("T")
    fl,ty,fx0,fx1 = flame_rects(T.flame_duo(13), mod, (ix + tx+tw)/2, -0.4)
    body,total,_ = word_rects(extra=fl)
    return wrap(body, min(0,fx0), ty, max(total,fx1), G.CAP), (min(0,fx0),ty,max(total,fx1),G.CAP)

BUILD = {"v0-plain":v0, "v1-torch-i":v1, "v2-torch-t":v2, "v3-flame-cut":v3,
         "v4-lit":v4, "v4b-lit-straddle":v4b}

if __name__=="__main__":
    for name,fn in BUILD.items():
        svg,box = fn()
        open("build/wordmark-%s.svg"%name,"w").write(svg)
        print("%-14s box %.2f %.2f -> %.2f %.2f" % (name,*box))

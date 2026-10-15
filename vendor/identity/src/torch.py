"""Torch symbol, redrawn on the wordmark's grid.

The source PNG only LOOKS pixel-gridded: its step sizes run 14,18,26,30,31,34,
38,66,77px with no common lattice.  Vectorising it directly would import that
irregularity and fight the letterforms.  So it is re-quantised onto a regular
lattice, forced symmetric, and de-speckled.
"""
import os
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "sources", "litsa-pixel-cut-torch-transparent.png")
MASTER = os.path.join(HERE, "..", "masters", "torch-symbol.svg")
GOLD,BLUE,INK = "#e5ad2d","#1769e0","#18212f"
EMPTY,G,B,K = 0,1,2,3

def build(N=32):
    if not os.path.exists(P):
        if N != 44:
            base = build(44)
            h, w = base.shape
            cols = max(2, int(round(w * N / h)))
            out = np.zeros((N, cols), int)
            for r in range(N):
                for c in range(cols):
                    cell = base[int(r*h/N):max(int((r+1)*h/N), int(r*h/N)+1),
                                int(c*w/cols):max(int((c+1)*w/cols), int(c*w/cols)+1)]
                    vals, counts = np.unique(cell, return_counts=True)
                    out[r, c] = vals[counts.argmax()]
            return out
        # The checked-in master is the portable source of truth. Its rects
        # occupy integer grid cells despite the small SVG antialiasing bleed.
        root = ET.parse(MASTER).getroot()
        out = np.zeros((44, 22), int)
        palette = {GOLD: G, BLUE: B, INK: K}
        for rect in root.findall("{http://www.w3.org/2000/svg}rect"):
            x = int(round(float(rect.attrib["x"])))
            y = int(round(float(rect.attrib["y"])))
            width = int(round(float(rect.attrib["width"])))
            colour = palette[rect.attrib["fill"].lower()]
            out[y, x:x + width] = colour
        return out
    a=np.array(Image.open(P).convert("RGBA")).astype(int)
    op=a[...,3]>128
    d=np.stack([((a[...,:3]-np.array(c))**2).sum(-1) for c in
                [(250,188,16),(2,102,200),(8,42,84)]],-1)
    lab=np.where(op,d.argmin(-1)+1,0)
    ys,xs=np.where(op); sub=lab[ys.min():ys.max()+1, xs.min():xs.max()+1]
    H,W=sub.shape; cols=int(round(W/(H/N)))
    if cols%2: cols+=1                                  # even, so it can mirror
    g=np.zeros((N,cols),int)
    for r in range(N):
        for c in range(cols):
            cell=sub[int(r*H/N):int((r+1)*H/N), int(c*W/cols):int((c+1)*W/cols)]
            v,n=np.unique(cell,return_counts=True); g[r,c]=v[n.argmax()]

    # 1. force symmetry: a cell is filled if EITHER side is, colour from the
    #    side nearer the centre (keeps the flame's inner blue core intact)
    half=cols//2
    for r in range(N):
        for c in range(half):
            l,rt=g[r,c],g[r,cols-1-c]
            v = l if l else rt
            if l and rt: v = max(l,rt)                  # ink > blue > gold
            g[r,c]=g[r,cols-1-c]=v

    # 2. de-speckle: drop any filled cell with fewer than 2 filled orthogonal
    #    neighbours (orphans read as noise and are fragile to weed)
    for _ in range(3):
        rm=[]
        for r in range(N):
            for c in range(cols):
                if not g[r,c]: continue
                n=sum(1 for dr,dc in ((1,0),(-1,0),(0,1),(0,-1))
                      if 0<=r+dr<N and 0<=c+dc<cols and g[r+dr,c+dc])
                if n<2: rm.append((r,c))
        if not rm: break
        for r,c in rm: g[r,c]=0
    return g

def to_svg_rects(g, u=1.0, dx=0.0, dy=0.0):
    fill={G:GOLD,B:BLUE,K:INK}
    out=[]
    for r in range(g.shape[0]):
        c=0
        while c<g.shape[1]:                              # merge runs -> fewer rects
            if not g[r,c]: c+=1; continue
            v=g[r,c]; s=c
            while c<g.shape[1] and g[r,c]==v: c+=1
            out.append('  <rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="%s"/>'
                       % (dx+s*u, dy+r*u, (c-s)*u, u, fill[v]))
    return "\n".join(out)

if __name__=="__main__":
    g=build(32); N,C=g.shape
    print("torch grid %d rows x %d cols" % (N,C))
    CH={0:".",G:"o",B:"+",K:"#"}
    for r in range(N): print("  "+"".join(CH[v] for v in g[r]))
    print("\nsymmetric:", bool((g==g[:,::-1]).all()))
    body=to_svg_rects(g)
    open("build/torch-symbol.svg","w").write(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 %d %d" width="%d" height="%d">\n%s\n</svg>\n'
      % (C+2,N+2,(C+2)*20,(N+2)*20,body))
    print("rects:", body.count("<rect"))

# ---------------------------------------------------------------- cleanup ---
def fill_gaps(g):
    """Close 1-cell gaps inside a colour run (turns '++.++' into '+++++')."""
    N,C=g.shape; h=g.copy()
    for r in range(N):
        for c in range(1,C-1):
            if not g[r,c] and g[r,c-1] and g[r,c-1]==g[r,c+1]: h[r,c]=g[r,c-1]
    for c in range(C):
        for r in range(1,N-1):
            if not h[r,c] and h[r-1,c] and h[r-1,c]==h[r+1,c]: h[r,c]=h[r-1,c]
    return h

def bridge_rows(g):
    """No fully-empty row may sit between two occupied rows (floating parts)."""
    N,C=g.shape; h=g.copy()
    occ=[r for r in range(N) if g[r].any()]
    for r in range(occ[0],occ[-1]+1):
        if not h[r].any():
            above=h[r-1]; below=h[r+1]
            wa=np.where(above)[0]; wb=np.where(below)[0]
            lo,hi=max(wa.min(),wb.min()),min(wa.max(),wb.max())
            if lo>hi: lo,hi=wb.min(),wb.max()
            h[r,lo:hi+1]=above[wa].max()
    return h

def symmetrise(g):
    N,C=g.shape
    for r in range(N):
        for c in range(C//2):
            l,rt=g[r,c],g[r,C-1-c]
            g[r,c]=g[r,C-1-c]=(max(l,rt) if (l and rt) else (l or rt))
    return g

def clean(N=44):
    g=build(N)
    for _ in range(2):
        g=symmetrise(bridge_rows(fill_gaps(g)))
    return g

def components(mask):
    """Count 4-connected components in a boolean mask."""
    m=mask.copy(); n=0
    for r in range(m.shape[0]):
        for c in range(m.shape[1]):
            if m[r,c]:
                n+=1; st=[(r,c)]; m[r,c]=False
                while st:
                    y,x=st.pop()
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        if 0<=y+dy<m.shape[0] and 0<=x+dx<m.shape[1] and m[y+dy,x+dx]:
                            m[y+dy,x+dx]=False; st.append((y+dy,x+dx))
    return n

# Hand-authored override for the blue flame's lower petals.  The automatic
# cleanup left the central gap narrow-wide-narrow, which reads as a cross.
# Columns are inclusive ranges on the 22-col grid; rows 12-19 stay as built.
BLUE_PETALS = {
    20: [(6,9),(12,15)],
    21: [(6,9),(12,15)],
    22: [(6,8),(13,15)],
    23: [(6,8),(13,15)],
    24: [(6,8),(13,15)],
    25: [(6,8),(13,15)],
}

def final(N=44):
    g=clean(N)
    if N==44:
        for r,spans in BLUE_PETALS.items():
            g[r][g[r]==B]=EMPTY                       # clear existing blue
            for a,b in spans: g[r,a:b+1]=B
    return g

def flame_frames(n=4):
    """Deterministic sprite frames; only the flame edge moves."""
    base = final(44)
    frames = []
    for frame in range(n):
        grid = base.copy()
        for row in range(2, 26):
            cols = np.where(grid[row] == G)[0]
            if len(cols) < 2:
                continue
            lo, hi = cols.min(), cols.max()
            wobble = ((row * 7 + frame * 13) % 5) - 2
            if wobble > 0 and lo > 0 and grid[row, lo - 1] == EMPTY and row % 2 == frame % 2:
                grid[row, lo - 1] = G
            if wobble < 0 and hi + 1 < grid.shape[1] and grid[row, hi + 1] == EMPTY and row % 3 == frame % 3:
                grid[row, hi + 1] = G
            if wobble == 0 and row > 4 and row % 4 == frame % 4:
                grid[row, lo] = EMPTY
        frames.append(symmetrise(grid))
    return frames

def flame(rows=13):
    """Simplified flame for letterform integration.

    The 44-row torch is too detailed to sit inside a 12u cap height, so the
    flame region is re-quantised to a coarse grid whose step size sits in the
    same visual family as the letterforms' own 1.3-1.45u stairs.
    """
    g=final(44)[0:26]                       # flame only, above the bowl
    N,C=g.shape; cols=int(round(C*rows/N))
    if cols%2: cols+=1
    h=np.zeros((rows,cols),int)
    for r in range(rows):
        for c in range(cols):
            cell=g[int(r*N/rows):int((r+1)*N/rows), int(c*C/cols):int((c+1)*C/cols)]
            v,n=np.unique(cell,return_counts=True)
            nz=[(vv,nn) for vv,nn in zip(v,n) if vv]
            h[r,c]= max(nz,key=lambda t:t[1])[0] if nz and sum(n[i] for i,vv in enumerate(v) if vv)>=cell.size*0.4 else 0
    h=symmetrise(h)
    for _ in range(2): h=symmetrise(fill_gaps(h))
    return h

def flame_solid(rows=13):
    """Solid flame silhouette: outer contour filled, no interior detail.
    Survives small sizes where the two-colour flame turns to mud."""
    f=flame(rows); h=np.zeros_like(f)
    for r in range(f.shape[0]):
        w=np.where(f[r])[0]
        if len(w): h[r,w.min():w.max()+1]=G
    return h

def flame_duo(rows=13):
    """Solid gold silhouette with the blue core knocked back in."""
    h=flame_solid(rows); f=flame(rows)
    h[f==B]=B
    return h

def flame_narrow(rows=10, cols=5):
    """Flame quantised to an explicit tall-narrow aspect, for knocking out of
    a 3u stem.  A square flame scaled down cuts straight through the stroke."""
    g=final(44)[0:26]; N,C=g.shape
    h=np.zeros((rows,cols),int)
    for r in range(rows):
        for c in range(cols):
            cell=g[int(r*N/rows):int((r+1)*N/rows), int(c*C/cols):int((c+1)*C/cols)]
            h[r,c]= G if (cell>0).mean()>=0.45 else 0
    h=symmetrise(h)
    for _ in range(2): h=symmetrise(fill_gaps(h))
    for r in range(rows):                       # solid silhouette
        w=np.where(h[r])[0]
        if len(w): h[r,w.min():w.max()+1]=G
    return h

def solid_torch():
    """One-colour torch: the flame filled as a silhouette.  Mono-filling the
    normal torch leaves its interior gaps as paper, so it reads as a hollow
    outline rather than a torch."""
    base=final(44)
    g=base.copy()
    for r in range(26):                       # fill the flame body solid...
        w=np.where(g[r])[0]
        if len(w): g[r,w.min():w.max()+1]=G
    g[base==B]=EMPTY                          # ...then void the inner flame
    return g

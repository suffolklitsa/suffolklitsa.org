import numpy as np, torch as T
EPS=0.02
FILL={T.G:T.GOLD, T.B:T.BLUE, T.K:T.INK}

def rects(g, u=1.0, dx=0.0, dy=0.0, mono=None):
    out=[]
    for r in range(g.shape[0]):
        c=0
        while c<g.shape[1]:
            if not g[r,c]: c+=1; continue
            v=g[r,c]; s=c
            while c<g.shape[1] and g[r,c]==v: c+=1
            out.append('  <rect x="%.4f" y="%.4f" width="%.4f" height="%.4f" fill="%s"/>'
                %(dx+(s-EPS)*u, dy+(r-EPS)*u, (c-s+2*EPS)*u, (1+2*EPS)*u,
                  mono or FILL[v]))
    return "\n".join(out)

def svg(w,h,body,pad=1.0,scale=24):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.3f %.3f %.3f %.3f" '
            'width="%.0f" height="%.0f" shape-rendering="crispEdges">\n%s\n</svg>\n'
            %(-pad,-pad,w+2*pad,h+2*pad,(w+2*pad)*scale,(h+2*pad)*scale,body))

if __name__=="__main__":
    g=T.final(44); N,C=g.shape
    open("build/torch-symbol.svg","w").write(svg(C,N,rects(g)))
    open("build/torch-symbol-ink.svg","w").write(svg(C,N,rects(g,mono=T.INK)))
    print("torch %dx%d written"%(C,N))

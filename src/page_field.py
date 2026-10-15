import shell as sh, taxonomy as D

CSS = """
<style>
.fam{margin-top:var(--s8);}
.scene{margin-top:var(--s7); border-top:2px solid var(--gold); padding-top:var(--s3);}
.scene img{display:block; width:100%; height:auto;}
.scene figcaption{margin-top:var(--s3); font-size:var(--t-xs); color:var(--ink-3);}
.fam:first-of-type{margin-top:var(--s6);}
.fam > h2{max-width:18ch;}
.fam > .blurb{color:var(--ink-2); max-width:56ch; margin-top:var(--s4);
  font-size:var(--t-md);}
.grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:var(--s6) var(--s7); margin-top:var(--s6);}
.dom{border-top:2px solid var(--gold); padding-top:var(--s4);}
.dom .top{display:flex; justify-content:space-between; align-items:baseline;
  gap:var(--s3);}
.dom h3{max-width:16ch;}
.dom .what{color:var(--ink-2); margin-top:var(--s3); font-size:var(--t-base);
  line-height:1.55;}
.dom .roles{font-family:var(--display); font-size:var(--t-xs); letter-spacing:.05em;
  color:var(--ink); margin-top:var(--s4); line-height:1.6;}
.key{display:flex; gap:var(--s4); flex-wrap:wrap; align-items:center;
  margin-top:var(--s6); font-size:var(--t-sm); color:var(--ink-3);}
.tally{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px;
  background:var(--line-soft); border:1px solid var(--line-soft);
  margin-top:var(--s7);}
.tally div{background:var(--paper-2); padding:var(--s5) var(--s5) var(--s6);}
.tally b{font-family:var(--display); font-size:var(--t-3xl); display:block;
  line-height:1; letter-spacing:.01em;}
.tally span{font-size:var(--t-sm); color:var(--ink-3); display:block;
  margin-top:var(--s3); line-height:1.5;}
@media (max-width:820px){.grid,.tally{grid-template-columns:1fr;}}
</style>
"""

CODE = {0:("No code","tag--none"), 1:("Some, learnable","tag--some"),
        2:("Yes, real code","tag--code")}

def dom(d):
    name, what, roles, lvl = d
    label, cls = CODE[lvl]
    return (f'<article class="dom" data-level="{lvl}"><div class="top"><h3>{name}</h3>'
            f'<span class="tag {cls}">{label}</span></div>'
            f'<p class="what">{what}</p><p class="roles">{roles}</p></article>')

PLATES = ["<svg class='plate' viewBox='0 0 10 10' aria-hidden='true' shape-rendering='crispEdges'><rect x='0' y='6' width='4' height='4'/><rect x='6' y='6' width='4' height='4'/><rect x='3' y='0' width='4' height='4'/></svg>", "<svg class='plate' viewBox='0 0 10 10' aria-hidden='true' shape-rendering='crispEdges'><rect x='0' y='0' width='10' height='3'/><rect x='0' y='4' width='6' height='2.5'/><rect x='0' y='7.5' width='10' height='2.5'/></svg>", "<svg class='plate' viewBox='0 0 10 10' aria-hidden='true' shape-rendering='crispEdges'><rect x='0' y='0' width='3' height='10'/><rect x='4' y='3' width='3' height='7'/><rect x='8' y='6' width='2' height='4'/></svg>"]

def fam(f, idx=0):
    name, blurb, ds = f
    return (f'<div class="fam"><h2>{PLATES[idx]}<span>{name}</span></h2><p class="blurb">{blurb}</p>'
            f'<div class="grid">{"".join(dom(d) for d in ds)}</div></div>')

lv = [d[3] for d in D.DOMAINS]
BODY = CSS + f"""
<section class="tight">
  <div class="wrap rail initial" data-initial="F">
    <p class="rail-label">The field</p>
    <div>
      <p class="eyebrow">A map of the field</p>
      <h1 style="margin-top:var(--s4);max-width:16ch">Legal innovation is more than software.</h1>
      <p class="lede" style="margin-top:var(--s5)">The field covers three kinds of work.
      Some people build tools for legal practice. Some govern technologies such as AI,
      privacy and cybersecurity. Others redesign courts, legal services and the way
      people reach help. Eleven of the twelve areas mapped below do not require coding.</p>
      <div class="key">
        <button class="tag tag--none filter" data-filter="0" aria-pressed="false"><i>No code</i></button>
        <button class="tag tag--some filter" data-filter="1" aria-pressed="false"><i>Some, learnable</i></button>
        <button class="tag tag--code filter" data-filter="2" aria-pressed="false"><i>Yes, real code</i></button>
        <span>Each tag says how much code that field really takes. Click one to filter.</span>
      </div>
      <div class="tally">
        <div><b class="num">{lv.count(0)}</b><span>fields need no code at all</span></div>
        <div><b class="num">{lv.count(1)}</b><span>need some, and it is learnable here</span></div>
        <div><b class="num">{lv.count(2)}</b><span>needs real software work</span></div>
      </div>
      <div class="bar" aria-label="Six fields need no code, five need some, one needs real code.">
        <span class="b-none" style="width:{100*lv.count(0)/12:.1f}%" tabindex="0"
          data-fields="Privacy and data protection, AI governance and regulation, cybersecurity and incident response, product and platform counsel, legal design, legal operations" data-lab="No code"></span>
        <span class="b-some" style="width:{100*lv.count(1)/12:.1f}%" tabindex="0"
          data-fields="Contracts and automation, e-discovery and litigation technology, knowledge and practice innovation, access to justice, court technology and ODR" data-lab="Some, learnable"></span>
        <span class="b-code" style="width:{100*lv.count(2)/12:.1f}%" tabindex="0"
          data-fields="Building the tools" data-lab="Yes, real code"></span>
      </div>
      <p class="barout" id="barout">Hover a band to see which fields sit in it.</p>
      <figure class="scene">
        <img src="/img/boston-beacon-hill-pixel-panorama.png" width="2172" height="724"
          alt="Boston and Beacon Hill." loading="lazy">
        <figcaption>Boston&rsquo;s courts and public agencies are within walking distance of Suffolk Law.</figcaption>
      </figure>
    </div>
  </div>
</section>

{sh.step()}

<section>
  <div class="wrap rail">
    <p class="rail-label">Three families</p>
    <div>{"".join(fam(f, k) for k, f in enumerate(D.FAMILIES))}</div>
    {sh.scene("field-court-records-pixel.webp",
      "A courthouse records room with a document scanner, filing cabinets and digital case records.",
      "Court records move between paper forms, scanners and filing systems.")}
  </div>
</section>

{sh.step()}

<section class="slab tight">
  <div class="wrap rail">
    <p class="rail-label" style="color:#8FA0B5">Where to start</p>
    <div>
      <h2>This work follows lawyers into every practice.</h2>
      <p class="lede" style="margin-top:var(--s5)">Litigators use e-discovery.
      Transactional lawyers work inside contract systems. Public-interest lawyers
      redesign intake and court forms. Privacy and AI rules increasingly reach all
      three. Legal innovation can be a career, but it is also part of ordinary legal practice.</p>
      <p style="margin-top:var(--s6)"><a href="/suffolk/">See what Suffolk already
      gives you &rarr;</a></p>
    </div>
  </div>
</section>
"""

def render():
    return sh.page("The field · LITSA",
        "Twelve domains across three families of legal innovation, each tagged by "
        "how much code it actually requires. Eleven of twelve need none.",
        "/field/", BODY)

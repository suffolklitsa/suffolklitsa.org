# LITSA Site — DESIGN.md

Read this before writing a single component. Re-read it at the start of every
session. Unspecified axes regress to the training mean; this document is the
specification that prevents that.

---

## 1. Thesis

**A legal instrument drawn on an exposed engineering grid.**

A law student's world is documents built from numbered sections and precise
citations. The LITSA identity is literally a measured modular grid: cap 12u,
stem 3u, stair step 1.45u. Both are systems of precision. The site does not
choose between "law" and "technology" — it shows the grid instead of hiding it.

One aesthetic, fully committed. No blending.

## 2. The governing rule

**The typeface has no curves and no diagonals. Neither does the interface.**

- `border-radius: 0` everywhere. No exceptions, including images and buttons.
- No diagonal lines, no rotation, no skew.
- Where a diagonal is unavoidable in meaning, it becomes a **stair-step**,
  the same move the L foot and A crossbar make.
- Dividers are stair-steps, not rules.

This is the site's signature. It is also the fastest way to tell that a human
made deliberate decisions here.

## 3. Colour

Three greys, one accent. The grey ramp is tinted toward the ink hue (blue-cool),
never neutral.

| Token | Value | Role |
| --- | --- | --- |
| `--ink` | `#18212F` | Primary text, dark surfaces |
| `--ink-2` | `#3A4657` | Secondary text |
| `--ink-3` | `#697788` | Tertiary text, captions |
| `--line` | `#D5DBE3` | Hairlines only where spacing cannot do the job |
| `--line-soft` | `#E6EAEF` | Section separation |
| `--paper` | `#F7F8FA` | Page ground |
| `--paper-2` | `#FFFFFF` | Raised surface |
| `--blue` | `#1769E0` | **Interaction only** |
| `--gold` | `#E5AD2D` | **Identity only** |

**The two colour laws, which are not negotiable:**

1. **Blue means you can act on it.** Links, buttons, focus rings, active states.
   Blue never decorates.
2. **Gold means identity.** The flame, the stair-step motif, the rule under a
   page title. Gold never marks anything interactive. A gold button is a bug.

No gradients. No shadows. Elevation is expressed by surface and spacing, never
by blur. Never pure black or pure white for text.

## 4. Type

Two families, doing conceptual work: the serif carries the law, the modular
face carries the technology.

**Display — LITSA Display** (ours, `static/font/`). Headings, the wordmark,
figures, section labels.
- All caps: tracking `+0.06em`
- Sentence case: tracking `+0.015em`
- Line height `1.05`–`1.15`
- Never below 18px. It is a display face; at body size it turns to mud.

**Body — Literata.** Long-form reading, sturdy, bookish without nostalgia.
- Body tracking `0`, line height `1.62`
- Measure `65ch` maximum, `58ch` preferred

**Scale** (hand-picked, wider gaps at the top):
`12 / 14 / 16 / 18 / 21 / 26 / 33 / 44 / 60 / 82`

Numbers that sit in columns get `font-variant-numeric: tabular-nums`.
Curly quotes, real ellipses, `→` never `->`.

## 5. Space

Scale: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128 / 192`.
Everything lands on it.

- **More space between groups than within them.** The single most common
  amateur tell. Check every block against this.
- Section padding `96–128px` vertical. Generous reads as confidence.
- Content max-width `1180px`; prose max-width `65ch`.
- **Asymmetry is the default.** One dominant column and one support column.
  Perfect symmetry reads as a template.

## 6. Motion

**Budget: two orchestrated moments for the entire site.** Not per page.

1. The torch assembles module by module on first load, once per session.
2. Stair-step dividers draw in as a section enters, once each.

Nothing else moves. No scattered scroll fades, no hover lifts, no parallax.
All motion respects `prefers-reduced-motion` by rendering the end state
immediately.

## 7. Images

- Every image lives in `static/img/` and is listed in `static/img/SOURCES.md`
  with its origin and licence. No exceptions, so a swap is ever only one line.
- Served as `.webp` with a `.jpg` fallback, explicit `width`/`height` to
  reserve layout, `loading="lazy"` below the fold.
- **Landing page carries no photography.** The identity system carries it.
- **History page uses genuine archival material**, public domain, attributed.
- Any generated imagery is faceless. Never AI-generated people.
- Images are square-cornered like everything else, and are never given a
  drop shadow.

## 8. Forbidden

Explicit prohibitions outperform positive guidance. None of the following may
appear, and if one does it is a defect, not a preference:

1. Inter, Roboto, Poppins, Space Grotesk, or any system-UI fallback as a
   visible design choice.
2. Any gradient. Especially purple-to-blue.
3. Rounded corners of any radius.
4. Drop shadows, glassmorphism, blur effects.
5. A three-equal-card feature grid.
6. Centred body text or centred-everything layouts.
7. A "trusted by" logo strip.
8. Emoji as section markers or bullets.
9. Numbered markers (01 / 02 / 03) on content that is not genuinely a sequence.
   The history page may use dates, because dates carry information.
10. Scroll-triggered fade-ins beyond the two budgeted moments.
11. Stock photography of smiling people at laptops.
12. Vague aspirational copy. Every claim carries a source or a specific.
13. `h-screen` / `100vh`. Use `100dvh`.
14. Any colour outside the token table.

## 9. Accessibility, treated as a design constraint

The org's own thesis is that most people face courts alone. A site about access
that is itself inaccessible is a contradiction.

- All text meets WCAG AA against its actual background. Gold on paper is
  1.91:1 and therefore **may never carry text**; it is a graphic element only.
- Visible focus ring on every interactive element: 2px blue, 2px offset,
  square.
- Real landmarks, one `h1` per page, headings in order.
- Every image has meaningful alt text or `alt=""` if decorative.
- Targets 44px minimum.
- Works keyboard-only, and works with CSS disabled well enough to read.

## 10. Verification, before anything is called done

- Contrast computed, not eyeballed, for every text/background pair.
- Rendered at 390px, 768px, 1280px, 1600px.
- No horizontal scroll at any width.
- HTML validates; no broken internal links.
- Every forbidden item above checked for explicitly.

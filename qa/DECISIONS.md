# Design Decisions: salta.dev home redesign

Rules source: tasteskill v2. Reference: bnbchain.org (structure and rhythm only).
Research baseline: `qa/reference/PHASE0.md`.

## Phase 1: mode, dials, levers

**Design read**: redesign-overhaul with content preserved, for a tech-community landing
(developers, designers, entrepreneurs, students, sponsors of northern Argentina), dark
polished technical-communal language, built on the existing terracotta brand system inside
the Django + Tailwind v4 stack. Structural skeleton borrowed from bnbchain.org; skin,
voice and identity stay SaltaDev.

**Dials** (current site reads 3 / 4 / 4; reference reads ~6 / 6 / 5):
- `DESIGN_VARIANCE: 6`. Mixed header alignments, one asymmetric bento, marquee, split
  sections. Above current flatness, below Awwwards chaos: this is a community trust site.
- `MOTION_INTENSITY: 6`. The page really animates: hero entrance, scroll reveals, counter
  roll-up, logo marquee, snap carousel. Everything collapses under `prefers-reduced-motion`.
- `VISUAL_DENSITY: 5`. Tighter than today (bnb-like compact meta and stat strips), still
  breathing at `py-20/24`.

**Modernisation levers (11.D), priority order**:
1. Typography hierarchy: same brand family (Space Grotesk), new scale/weight/color ramp.
2. Spacing and rhythm: consistent section grid, alternating header alignments.
3. Color recalibration: 3-level ink ramp instead of all-white; accent lock on terracotta;
   retire per-platform accent colors and `red-700` hovers.
4. Motion layer: GSAP reveals + counters + marquee + carousel, all motivated, all reduced-motion safe.
5. Hero + key-section recomposition (hero, staff, community bento, norte band).
6. Full block replacement only where unsalvageable (uniform card grids).

## Section mapping (bnbchain structure -> salta.dev content)

| # | bnbchain.org | salta.dev redesigned | layout family | content source |
|---|---|---|---|---|
| 1 | Slim nav 64px | Nav restyled <=72px, labels/links intact | utility nav | nav.html |
| 2 | Stacked-claims hero | "El Hub Tech del Norte Argentino" claims stack + subtext + 2 CTAs; photo card w/ avatar overlay "+1000 miembros" | asymmetric split hero | current hero |
| 3 | Stat bar (5 metrics) | 3 sourced metrics: +1000 miembros, +{{count}} colaboradores, 6 plataformas; animated counters | stat strip | hero/#partners/#community |
| 4 | 3 solution cards | Pilares: Empleos / Cursos / Eventos (existing copy), one featured cell | 3-card grid (1 featured) | current stat strip copy |
| 5 | Logo strip "Trusted by" | #partners: logo marquee (19 real logos) + "Ver todos" expandable grid | logo marquee | #partners |
| 6 | Programs carousel | #events: "Próximos Eventos" scroll-snap carousel, real flyers, fecha/lugar + Registrarme | media carousel | /eventos data |
| 7 | Example cards w/ tags | #community: "Sumate a la charla" 6-cell asymmetric bento (Discord+WhatsApp featured) | bento (6 items = 6 cells) | #community |
| 8 | (no equivalent) | Norte band: full-width poncho-stripe band with "Impulsando el futuro digital del norte." | full-width manifesto band | footer tagline (real copy) |
| 9 | (no equivalent) | #staff: "Quiénes Somos" split heading + 3 horizontal profile rows | split + profile rows | #staff |
| 10 | (no equivalent) | #contact: split, left heading + direct email, right form (fields intact) | split form | current form |
| 11 | Mega footer | Footer reorganized to reference rhythm (brand+social row, link columns, legal bar) | mega footer | current footer |

At least 4 distinct layout families: split hero, stat strip, 3-card grid, marquee,
carousel, bento, manifesto band, profile rows, split form. Tasteskill divergence points:
hero, staff, norte band (section 8, the identity section bnbchain does not have).

## Token decisions (single file: `saltadev/tailwind/source.css`)

Existing token names and values preserved (other pages depend on them). Additions, all
derived from the brand terracotta and warm dark scheme:

| Token | Value | Why |
|---|---|---|
| `--color-ink` | `#f3ece9` | Primary text. Replaces pure `#fff` (banned); 15.4:1 on bg-dark. |
| `--color-ink-faint` | `#9d8b87` | Tertiary/meta text; 5.5:1 on bg-dark (AA body). |
| `--color-primary-soft` | `#c0625d` | Terracotta tint for LARGE accent text and icons (4.4:1, >=3:1 large-text AA). |
| `--color-primary-bright` | `#d98a83` | Terracotta tint for SMALL accent text (6.7:1 body AA). Fixes the current site's #94413d-on-dark accent text, which measures 2.6:1 (AA fail). |
| `--color-primary-deep` | `#6e2f2c` | Pressed states and strong accent borders. |
| `--color-surface-raised` | `#2b2220` | Elevated tint above surface-dark for featured cells. |
| `--ease-brand` | `cubic-bezier(0.16,1,0.3,1)` | One easing curve for all motion. |

Shape rule (Shape Consistency Lock): cards, buttons and inputs use `rounded-lg` (1rem);
`rounded-full` only for circular media (avatars, logo dots). No mixed radius systems.
Accent lock: terracotta is the only accent on the page. Existing secondary token
`--color-text-muted` (#c4b5b3) is the mid step of the ink ramp.
Type stays Space Grotesk (brand fidelity; hierarchy comes from scale/weight/color, not a
new family; zero extra font downloads keeps LCP budget).

## Build decisions log (Phase 2, appended per section)

### 1. Nav
- 64px height (was 80), single line at every viewport. Hamburger now runs through `md`
  because at 768px the 6 labels + CTA cannot fit on one line without wrapping (QA shot
  caught the login CTA breaking into two lines).
- Link ramp: `text-muted -> ink` on hover; CTA uses `primary -> primary-hover` (retired
  `red-700`). Global `:focus-visible` outline added in base.css.
- Retired: body-wide `animated-bg` 18s gradient drift (unmotivated motion, mobile GPU cost).

### 2. Hero (asymmetric split, claims stack)
- Structure follows the reference's claims-hero role but keeps SaltaDev's split layout:
  7-col claims stack + 5-col real photo. Anti-center rule holds (VARIANCE 6).
- Claims stack: badge eyebrow "Comunidad salteña" (1 of max 3 eyebrows on the page,
  pulsing green dot removed: decorative status dot tell), H1 two lines with second line
  in `primary-soft` (typographic emphasis replaces the hand-drawn SVG squiggle),
  20-word subtext in `text-muted`, 2 CTAs. Exactly 4 text elements.
- Photo card: real community photo as `<img>` (was CSS background) with width/height,
  `loading="lazy"` so the `hidden lg:block` card never downloads on mobile; avatar stack
  + "+1000 miembros" overlay preserved as social proof ON the visual, not in the text stack.
- Assets: generated WebP derivatives (hero 3872px/2.1MB -> 960x1200/172KB; avatars
  728KB jpg -> 4-8KB webp). Mobile LCP element is now the H1 text.
- Retired: bouncing `code` icon card, cursor-glow, floating scroll stepper buttons
  (scroll cues), `window scroll` listeners in index.js.
- Motion: staggered hero entrance (reading order) + scroll reveals via `[data-reveal]`,
  gated behind `prefers-reduced-motion`.

### 3. Stat strip
- 3 sourced metrics only: +1000 miembros (site copy), +N organizaciones (live DB count,
  renders +20 in production), 6 plataformas (the six community platforms). No invented
  numbers. Reference's 5-metric bar trimmed to what has a source.
- Counters roll up once on scroll (GSAP); markup ships the final value so no-JS and
  reduced-motion users see real numbers. `tabular-nums` prevents digit jitter.
- Old strip mixed one metric with three category labels at equal visual weight; that
  hierarchy conflict is what made it read flat. Metrics and pillars are now separate rows
  (matching the reference rhythm: stat bar, then solution cards).

### 4. Pillars (Empleos / Cursos / Eventos)
- 3-card grid with the third cell featured (terracotta gradient + poncho pattern +
  stronger border), mirroring the reference's badge-card asymmetry without inventing a
  badge metric. Breaks the banned "three identical cards" pattern.
- Copy verbatim from the old strip. No extra CTA here: /eventos/ is already reachable
  from the hero and the events section (duplicate-intent rule).

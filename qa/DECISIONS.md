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

### 5. Partners (#partners): logo marquee + directory
- Full-bleed marquee (the single marquee allowed per page), CSS keyframe on a doubled
  track, paused on hover and focus-within, edge fades. Tiles are LOGO-ONLY per the
  logo-wall rule.
- "Ver todos los colaboradores" (existing label) expands a named directory grid: names
  are justified there because most partners are local organizations whose marks alone
  are not recognizable; that grid is a directory, not a trust wall.
- Under reduced motion the marquee is removed and the directory renders expanded.
- UNSA (empty link in the data) renders as a span, not an empty-href anchor.

### 6. Events (#events): scroll-snap carousel
- Native CSS scroll-snap; at 1440 all three cards fit so the arrow controls hide
  (no dead UI); on mobile the next card peeks at 85vw as the scroll affordance.
  Region is keyboard-focusable; arrows honor reduced motion via instant scroll.
- No autoplay: motion here is user-driven, so nothing needs pausing (extras rule).
- Flyers render at their real 1200x630 ratio as img elements; the old date pill
  overlaid on the image was removed (overlaid-pills tell) and date/time/location live
  in the card body with a single midpoint separator.
- Element-level scroll listener only syncs button disabled state (cheap, passive);
  the window-scroll animation ban stays respected.

### 7. Community (#community): asymmetric bento
- 6 items = 6 cells, 4+2 / 2+2+1+1. Discord featured horizontally with a terracotta
  radial wash; WhatsApp on raised surface; background diversity without inventing
  imagery. Accent lock enforced: the per-platform brand colors are gone.

### 8. Norte band (identity section, no reference equivalent)
- Poncho salteño translated to CSS: horizontal weave stripes masked away from the type
  area plus a right-edge vertical franja. Static by design.
- Copy is the real footer tagline recomposed: eyebrow (2nd of 3 allowed) + display line
  with terracotta emphasis on "del norte."

### 9. Staff (#staff): split + profile rows
- 4-col heading, 8-col profile rows with hairline dividers (distinct family from every
  card grid on the page). Roles moved from #94413d (2.6:1, AA fail) to primary-bright
  (6.7:1). Social links became 36px bordered tiles (real touch targets).

### 10. Contact (#contact): split form
- Left: heading + direct mailto link (same address as the form action). Right: form
  card. Fields, names, labels, placeholders, required flags and mailto action verbatim.
- Placeholders moved to ink-faint (5.5:1) from the old muted-on-dark combination.

### 11. Footer
- Reference mega-footer rhythm: brand + social tiles row, hairline, three link columns
  (labels and hrefs verbatim), legal bar. "Volver al inicio" kept mobile-only.

---

## Phase 3: closing audits (2026-07-15)

### Em-dash audit
- Shipped code (templates, CSS, JS, tokens): **zero U+2014 and U+2013**. PASS.
- Data note: the "Cultura C3 en Salta" event description in the production DB contains
  one en-dash ("Salta – Sábado"). It renders on /eventos/ only (not the home top-3).
  It is database content outside the redesign's write scope; fix via admin edit.

### Preservation audit (must be empty)
Modified URLs: **none** (no urls.py/views/models touched, verified via git diff).
Modified nav labels: **none** (rendered check: Inicio | Colaboradores | Staff |
Comunidad | Eventos | Reglamento + "Iniciar sesión").
Modified form fields: **none** (name, email, subject, body; mailto action intact).
Modified anchors: **none** (top, partners, community, events, staff, contact all render).
Modified title/meta/canonical: **none** (verbatim, including the accent-less
"diseniadores" meta per contract). Logo file and treatment: unchanged. Lang: es. PASS.

### Brand fidelity audit
- Accent: #94413d terracotta remains the only accent; extensions (#c0625d, #d98a83,
  #6e2f2c) are tints/shades of it, documented in Phase 1. PASS.
- Typography: Space Grotesk remains the sole family (display + body). PASS.
- Logo: same webp asset, same nav/footer placement, wordmark beside it. PASS.
- Identity motif: poncho pattern preserved and extended (featured pillar cell, hero
  backdrop, norte band weave). PASS.

### Layout-repetition audit (one family per section)
split hero / stat strip / 3-card grid (1 featured) / logo marquee / bento 6-cell /
snap carousel / manifesto band / split + profile rows / split + form / mega footer.
10 sections, 10 distinct families (well above the 4 minimum). PASS.

### Hero discipline audit
Headline 2 lines at every viewport; subtext exactly 20 words, 3 lines max; badge +
headline + subtext + CTA row = 4 text elements; CTAs visible without scroll at 375
and 1440 (QA shots); top spacing within the pt-24 cap; social proof lives on the photo
card (avatar stack + "+1000 miembros"), which is the placement the brief's mapping
table specifies, not a 5th text element. PASS.

### Pre-Flight Check (tasteskill Section 14)
- Brief inference declared: PASS (Phase 1 design read).
- Dials explicit and reasoned: PASS (6/6/5).
- Design system honest: PASS (Tailwind v4 tokens + native CSS, no framework cosplay).
- Redesign mode + audit: PASS (Phase 0, 11.B).
- Zero em-dashes in shipped output: PASS (see data note above).
- Page Theme Lock: PASS (single dark theme; `html.dark` + color-scheme dark are the
  existing brand decision, documented override of dual-mode default).
- Color Consistency Lock: PASS (terracotta only; platform colors removed).
- Shape Consistency Lock: PASS (cards/buttons/inputs/chips = 1rem; rounded-full only
  on avatar media; hero badge corrected from pill to 1rem during this audit).
- Button Contrast: PASS (ink on primary 5.85:1; all CTAs measured against tokens).
- CTA wrap: PASS (all one line at 1440; nav CTA nowrap guarded).
- Form Contrast: PASS (labels ink 15:1, placeholders ink-faint 5.5:1, terracotta focus ring).
- Serif discipline: PASS (no serif introduced).
- Premium-consumer palette ban: N/A (brand palette mandated and preserved).
- Italic descender clearance: N/A (no italic display type).
- Hero fits viewport / top padding / stack <=4: PASS (see hero audit).
- Eyebrow count (mechanical): PASS. Eyebrows above headlines: hero badge + norte band
  label = 2, ceiling for 10 sections is 4. (Stat-strip unit labels sit under their
  values; they are data labels, not section eyebrows.)
- Split-Header Ban: PASS (right columns carry interactive/content elements: toggle
  button, carousel controls, profile rows, form; no floating explainer paragraphs).
- Zigzag Alternation Cap: PASS (no consecutive image+text splits).
- Duplicate CTA intent: PASS with note. "Unirse a la comunidad" is the single join
  CTA. "Ver Eventos" (hero, brief-mandated) and "Ver calendario completo" (events
  header, existing site copy) both reach /eventos/; kept as distinct micro-intents
  (start browsing vs see the full calendar), both preserved original labels.
- Logo wall logos-only: PASS (marquee). The expanded "Ver todos" grid shows names by
  design: local organizations are not recognizable by mark alone; it is a directory.
- Bento background diversity: PASS (feature radial wash + raised cell + plain cells).
- Trusted-by under hero with real logos: PASS (real partner assets, not text spans).
- Copy self-audit: PASS (all strings are preserved site copy or plain functional labels).
- Motion motivated: PASS (entrance = reading order, reveals = hierarchy, counters =
  data emphasis, marquee = breadth, carousel = user-driven browsing).
- Marquee max one per page: PASS.
- Nav one line, <=80px: PASS (64px).
- Section-Layout-Repetition: PASS (10 families).
- Bento exact cell count: PASS (6 = 6).
- Long lists use the right component: PASS (19 logos -> marquee + disclosure grid).
- Real images: PASS (community photo, event flyers, staff photos, partner logos; no
  div screenshots; hand-drawn squiggle SVG removed).
- No pills/labels overlaid on images: PASS (event date pills moved into card bodies;
  hero avatar overlay is brief-specified social proof, not decoration).
- No photo credits / version footers / micro-meta / decoration strips / floating
  corner text / progress bars / locale strips / scroll cues / version labels /
  numbered eyebrows / decorative dots: PASS (scroll steppers, cursor glow and the
  pulsing badge dot were removed).
- No border-t+border-b row striping: PASS (staff uses single divide-y).
- Content density: PASS (short headlines, 20-25 word subtexts, clamped descriptions).
- Quotes: N/A.
- Motion claimed = shown: PASS (MOTION 6 with five real motion systems).
- GSAP sticky-stack / horizontal-pan skeletons: N/A (not used).
- No window scroll listeners: PASS (grep-verified; carousel syncs on element scroll,
  reveal/counters use ScrollTrigger).
- Reduced motion: PASS (GSAP guard, marquee -> static grid, carousel instant scroll,
  smooth-scroll fallback to auto).
- Dark mode both modes: consciously N/A; single dark theme is the preserved brand
  (brief: "un solo theme en toda la página").
- Mobile collapse explicit: PASS (every grid declares its < 768 behavior; QA at 375).
- Viewport stability: PASS (min-h with dvh, no h-screen; images have dimensions or
  fixed-box containers).
- useEffect cleanups: N/A (vanilla JS, page-lifetime listeners).
- Empty/loading/error states: PASS where applicable (events empty state; native form
  validation; mailto has no async states).
- Cards omitted in favor of spacing where possible: PASS (staff rows, stat strip).
- Icons from allowed set: PASS (Material Symbols = existing project icon system,
  reused; platform marks are brand logos).
- Motion isolated + no AI tells + one design system: PASS.
- Core Web Vitals: PASS on evidence below.

### Final QA evidence (qa/final/)
- Preservation contract verified in rendered DOM (see qa/final/qa-report.txt).
- Keyboard walk (60 tab stops): nav -> hero CTAs -> partners toggle -> marquee links
  (marquee pauses on focus) -> bento -> events link -> carousel region -> Registrarme
  x3 -> staff socials -> form -> footer. Focus ring missing count: 0.
- LCP mobile 375px with ~1.6Mbps / 150ms RTT / 4x CPU throttle: **1296ms** (< 2500ms
  budget; local server, production adds CDN + Render latency but the 1.2s margin and
  the text-LCP hero keep it safe).
- Console errors: none on /, /eventos/, /reglamento/ at 375/768/1440, two full passes.
- Horizontal overflow: none at any viewport on any page.
- /eventos/ and /reglamento/ visually verified healthy with the new nav/footer/tokens.

### Known flags left for the owner (data/config, not redesign scope)
1. "Cultura C3" description en-dash (DB edit).
2. "Santader Tecnología" typo in staff bio (DB edit).
3. UNSA collaborator has empty link (DB edit).
4. Events shown under "Próximos Eventos" are past dates (DB data).
5. Sitemap references URL name `events_list` vs actual `events` (pre-existing code).
6. og:image relative path; reglamento canonical empty (pre-existing, meta contract).
7. Production CSP script-src may not list jsDelivr (GSAP source, pre-existing).

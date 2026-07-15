# Phase 0 Research: salta.dev redesign (bnbchain.org as structural reference)

Date: 2026-07-14. Mode: Greenfield-with-content-preserved. Rules source: tasteskill v2.
Screenshots: `qa/reference/{bnbchain,saltadev}-{1440,375}.png` + DOM outlines (`*-outline.json`).

---

## 1. Stack confirmation

- Django 5.2.11, Python >= 3.12, deployed on Render.com (`build.sh`: tailwind build -> collectstatic -> migrate).
- CSS: django-tailwind-cli 4.5.1 with **Tailwind v4** (CSS-first config). Tokens live in `saltadev/tailwind/source.css` (`@theme` block). Built to `saltadev/static/css/tailwind.css`, injected via `{% tailwind_css %}`.
- Handwritten CSS: `saltadev/static/assets/css/{base,index,events,reglamento,auth,dashboard}.css`.
- JS: no build tooling. Vanilla files in `saltadev/static/assets/js/` (`index.js` GSAP reveals + cursor glow + floating scroll, `events.js` countdown, `reglamento.js` TOC spy, `fingerprint.js`). GSAP 3.12.7 + ScrollTrigger from jsDelivr CDN with SRI.
- Templates: centralized in `saltadev/templates/` (base.html + includes/{head,nav,footer}.html + home/index.html, events/index.html, code_of_conduct/index.html). Blocks: title, meta_description, canonical, og_*, twitter_*, structured_data, page_css, content, page_js.
- Static: WhiteNoise CompressedManifestStaticFilesStorage. Media: Cloudinary (cloud `dxspj6n5r`) in prod/dev, local `media/` in DEBUG.
- Home view context (60s cache): `latest_events` (3 APPROVED, ordered -event_start_date), `staff_members` (max 6, ordered by `order`), `collaborators` + count.
- Conclusion: redesign happens inside Django templates + Tailwind v4 tokens + assets CSS/JS. No framework migration needed.

### Technical flags found (pre-existing, not introduced by redesign)
1. Production CSP `CSP_SCRIPT_SRC` does not list cdn.jsdelivr.net although head.html loads GSAP from there. Verify before adding more CDN JS; self-hosting JS is safer.
2. `sitemaps.py` references URL name `events_list` but `events/urls.py` names it `events`. Verify sitemap renders.
3. `og:image` uses a relative static path (not absolute URL) on all pages.
4. Reglamento page canonical block is empty.
5. Meta descriptions have stripped accents in source ("diseniadores", "Codigo") — they are part of the preservation contract, change only with explicit approval.
6. Dead asset: `static/assets/fonts/Railey.ttf` referenced nowhere.
7. Stale duplicate built CSS at `static/static/css/tailwind.css`.

---

## 2. URL / preservation contract (INTOCABLE without explicit approval)

| URL | View name | Behavior |
|---|---|---|
| `/` | `home` | home page |
| `/eventos/` | `events` | events page |
| `/reglamento/` | `code_of_conduct` | code of conduct |
| `/login/` | `login` | login page (200) |
| `/whatsapp/` | `redirect_whatsapp` | 301 -> chat.whatsapp.com/E3pCz7UySrmKiIVO5PA4Cz?mode=gi_t |
| `/discord/` | `redirect_discord` | 301 -> discord.gg/kqzWbStGQ6 |
| `/linkedin/` | `redirect_linkedin` | 301 -> linkedin.com/company/saltadev/ |
| `/github/` | `redirect_github` | 301 -> github.com/Salta-Dev |
| `/x/` | `redirect_twitter` | 301 -> x.com/SaltaDevAr |
| `/instagram/` | `redirect_instagram` | 301 -> instagram.com/salta.dev.ar/ |

- Anchors on home: `#partners`, `#community`, `#events`, `#staff`, `#contact` (nav uses `/#partners`, `/#staff`, `/#community`). `<main id="top">`.
- Nav labels (order): Inicio, Colaboradores, Staff, Comunidad, Eventos, Reglamento + CTA "Iniciar sesión" -> `/login/`.
- Titles: `SaltaDev - Comunidad de Desarrolladores` / `Eventos - SaltaDev` / `Reglamento de Conducta - SaltaDev`. Meta descriptions preserved verbatim (see agent inventory below).
- Contact form: action `mailto:comusaltadev@gmail.com`, fields `name` (Nombre), `email` (Email), `subject` (Asunto, required), `body` (Mensaje, textarea, required), submit "Enviar Mensaje". Field names are mailto query params: do not rename.
- Logo: `static/assets/img/logo.webp` (hashed .33d2e3d926f3). Language: `<html class="dark" lang="es">`, es-AR voseo in copy.

---

## 3. Content inventory (real content, live site 2026-07-14)

### Hero (home)
- Badge: "Comunidad salteña" (with pulsing green dot).
- H1: "El Hub Tech del" / "Norte Argentino" (terracotta + hand-drawn SVG underline).
- Sub: "Conectamos desarrolladores, diseñadores y emprendedores en Salta. Impulsamos el talento local a través de la colaboración, el aprendizaje y eventos."
- CTAs: "Unirse a la comunidad" -> `/whatsapp/` (primary) | "Ver Eventos" -> `/eventos/`.
- Photo card: `assets/img/seed-latam-salta.jpg` + avatar stack (`people_1/2/3.jpg`) + "+1000 miembros".

### Stat strip
`+1000` Miembros activos | EMPLEOS Compartimos ofertas laborales | CURSOS Compartimos recursos educativos | EVENTOS Organizamos y difundimos eventos.

### Partners (#partners) — 19 rendered (copy says "Más de 20 organizaciones confían en el talento de nuestra comunidad.")
Cloudinary base `res.cloudinary.com/dxspj6n5r/image/upload/v1/media/partners/`:
AbadiaDev (x.com/Abadiadev, abadiadev_hlnexi), Bitget (bitget.com/es, bitget_lxjzlj), CloudyCoding (cloudycoding.com, cloudy_ufkygu), Crecimiento (crecimiento.build, crecimiento_u8dx6x), Develop Inglés Laboral (instagram develop.ingleslaboral, develop_nvlciv), Eurekant (eurekant.com, eurekant_t0gprb), Express Telecomunicaciones (express.com.ar/inicio, express_l0j0xe), JPG Pics (instagram jpgpics_, jpgpics_en7cik), Nisuta (tiendanisuta.com, nisuta_oxln0h), Poncho Capital (ponchocapital.com, ponchocapital_qcfzyn), Pragmore (pragmore.com, pragmore_fm2lpv), Salta Cybersecurity Club (saltacybersecurity.club, saltacyber_h8vbbu), Salta Game Devs (instagram salta_game_dev, saltagamedevs_fysli1), Tasty Control (tastycontrol.com, tastycontrol_ucgpyh), Universidad Nacional de Salta (href EMPTY, unsa_dyzww8), x64 (x64.ar, x64_etfztb), programaConNosotros (programaconnosotros.com, programaconnosotros_nmw4qy), DESAFIA (desafia.tech, desafia_qbbx4d), SEED Latam (seedlatam.org, seedlatam_1_iyn8su).
Mobile: first 4 visible + "Ver todos los colaboradores" toggle.

### Community (#community) — "Sumate a la charla"
Intro: "Nuestra comunidad vive en diferentes plataformas. Elige tu favorita y comienza a interactuar."
| Card | Description | href |
|---|---|---|
| Discord | Chat en vivo, canales de voz y ayuda técnica. | /discord/ |
| WhatsApp | Grupos por temática y anuncios rápidos. | /whatsapp/ |
| LinkedIn | Networking profesional y oportunidades. | /linkedin/ |
| GitHub | Proyectos open source de la comunidad. | /github/ |
| X | Noticias y novedades de la comunidad. | /x/ |
| Instagram | Fotos, eventos y momentos de la comunidad. | /instagram/ |

### Events (#events on home shows 1-3; /eventos/ shows all 5)
Home heading "Próximos Eventos" + "Ver calendario completo" -> `/eventos/`. Card CTA on home: "Registrarme"; on /eventos/: "Ver más".
| Event | Date | Time | Location | Link |
|---|---|---|---|---|
| PunaTech 2026 - 28, 29 y 30 de Mayo | 28, 29 y 30 de Mayo | 9:00 a 19:00 | Av. Independencia 910 | punatech.ar/#entradas |
| Aleph Hackathon 2026 | 20, 21 y 22 de Marzo | 09:00 hs | IRL + Virtual | instagram.com/p/DUWdLR0kjsZ/ |
| Blockchain Salta | 19 de Septiembre | 16:00 hs | Salón Forum | luma.com/0nlhacs9?locale=es&tk=YPpJNo |
| Cultura C3 en Salta | 31 de Mayo | 10:00 hs | Universidad Nacional de Salta | lu.ma/y7t0op6j |
| Bitcoin Pizza Day 2025 | 22 de Mayo | 20:00 hs | Temple Craft Bar | luma.com/jq3877ml |
Images: Cloudinary `saltadev/events/event_*.{jpg,avif}` with `w_1200,h_630,c_fill,g_auto,q_auto,f_auto`. Full verbatim descriptions in scratchpad HTML snapshots and live DB.
/eventos/ extras: countdown hero (target `2026-05-28T09:00:00-03:00`, already past), hidden empty state, featured PunaTech block ("Inscribirse" / "Ver más eventos"), bottom CTA band ("¿Querés proponer un evento?" -> mailto + WhatsApp).

### Staff (#staff) — "Quiénes Somos" / "El equipo detrás de la organización de SaltaDev."
Cloudinary base `.../v1/media/staff/`:
1. Facundo Padilla — Fundador — "Software Engineer en Santader Tecnología" (typo "Santader" is live) — facundo-padilla_blgp7f — LinkedIn/GitHub/X/website facundopadilla.com.
2. Juan Patricio Gutierrez Guzman — Administrador — "Co-founder de Coplero | Consultor operacional de IA" — juan-guzman_wv1maz — LinkedIn.
3. Verónica Torres — Administradora — "Docente, project manager y tester QA" — vero_dmmbif — LinkedIn.

### Contact (#contact)
"Contáctanos" / "¿Tienes alguna duda o propuesta? Escríbenos." Form per preservation contract above.

### Footer
Brand: logo + "Comunidad de tecnología y desarrollo en Salta. Impulsando el futuro digital del norte."
Columns: Comunidad (WhatsApp, Discord, LinkedIn, X, Instagram, GitHub -> internal redirects) | Recursos (Eventos, Colaboradores, Comunidad) | Legal (Código de Conducta -> /reglamento/).
Copyright: "© 2026 SaltaDev. Todos los derechos reservados." Social icons: LinkedIn + mail (comusaltadev@gmail.com).

### Metrics with source (the ONLY numbers allowed)
- "+1000 miembros" / "+1000 Miembros activos" (hero + stat strip).
- "Más de 20 organizaciones" (partners intro; 19 cards render — flagged).
- Contact emails: comusaltadev@gmail.com (form/footer/eventos), info@salta.dev (reglamento #contacto).

### SEO baseline
- JSON-LD Organization on home only (name, url, logo, address Salta AR, sameAs socials).
- Sitemap: home, events, code_of_conduct, benefits_list (name mismatch flag). robots.txt allows all, disallows admin/dashboard/auth routes.
- og:locale es_AR, twitter summary_large_image, `meta color-scheme: dark`, `meta robots: index, follow`.

---

## 4. Section 11.B audit of salta.dev (current site)

### Brand tokens in use
- `--color-primary: #94413d` (terracotta), `--color-primary-hover: #b04e49`, bg `#1d1515`, surface `#241f1e`, sidebar `#181414`, border `#342d2d`, muted `#c4b5b3`, light `#f7f6f6`, alert `#ef4444`. Extra hardcoded: `#181013`, `#7a3431`, `#23181b`, `#3a2a2d`, `#4d4242`.
- Type: Space Grotesk (display AND sans), Material Symbols Outlined icons. Google Fonts link tags.
- Radii: 0.5 / 1 / 1.5 / 2rem + full pills. Shadows: terracotta glow `0 0 20px rgba(148,65,61,.4)`, deep black card shadows.
- Identity motif: "poncho" pattern (inline SVG plus-grid, primary at 5% opacity) + poncho stripe bars. This is the existing norte-argentino visual hook.

### Information architecture
One-page home (hero -> stats -> partners -> community -> events -> staff -> contact) + /eventos/ + /reglamento/ + auth. Conversion paths: WhatsApp join (primary), event registration (external links), mailto contact. IA is sound; preserved as-is.

### Patterns to preserve
- Terracotta-on-warm-dark palette and the poncho motif (evolved, not copied literally).
- Real photography in hero + avatar stack social proof.
- Space Grotesk as brand type starting point (extend, not replace, unless approved).
- GSAP + reduced-motion discipline already present in index.js.
- All URLs, anchors, nav labels, form fields, meta (contract).

### Patterns to retire (tasteskill tells present today)
1. Pulsing green status dot in hero badge (decorative status dot: banned).
2. `#cursorGlow` mouse-follow glow (custom-cursor family, perf cost, tell).
3. Floating scroll stepper buttons / scroll cues (banned).
4. Hand-drawn SVG squiggle underline in H1 (hand-rolled decorative SVG).
5. Six sections all using the same layout family: centered heading + centered sub + uniform card grid (layout-repetition ban; the "cards sin ritmo" problem).
6. Per-platform accent colors on community cards (indigo/green/blue/slate/pink) breaking the Color Consistency Lock.
7. `red-700` hover classes instead of brand hover token.
8. `text-white` everywhere; muted token barely used (flat hierarchy).
9. `animated-bg` fixed 18s gradient drift behind everything (unmotivated motion).
10. Material Symbols icon font (FOUT/flash of unstyled icon text, generic look): candidate for replacement with a single SVG icon family.

### Dial reading (current site)
- DESIGN_VARIANCE: **3** (only the hero is split; everything else symmetric centered grids).
- MOTION_INTENSITY: **4** (GSAP entrance reveals, countdown, hovers; reduced-motion respected).
- VISUAL_DENSITY: **4** (py-20 sections, airy cards).

---

## 5. Structural reading of bnbchain.org home (captured 2026-07-14, 1440px)

Ordered sections and layout families (structure only; zero assets/copy/colors taken):

1. **Nav** (64px): logo left, 5 dropdown items, 2 CTAs right (accent pill + ghost). Family: slim utility nav.
2. **Stacked-claims hero**: centered multi-line claim headline, one line accent-colored, single primary CTA + prompt-style input below; subtle geometric pixel-grid background. Family: centered claims/manifesto hero. Hero + stat bar fit ~1 viewport.
3. **Stat bar**: 5 metrics in one row with thin vertical dividers (big value, small label). Family: horizontal stat strip.
4. **Solution cards**: small centered heading, then 3 equal cards (title, body, one badge), tinted surfaces, 1px borders. Family: 3-card grid.
5. **Logo strip** ("Trusted by..." one-line label): single static row of ~7 monochrome logos. Family: logo wall.
6. **Proof bento**: centered heading, 3-column asymmetric bento mixing photo tiles with big-number stat tiles (numbers as visual anchors). Family: stats+photo bento.
7. **Programs list**: left-aligned small heading + "View All" top-right; 3 compact horizontal card-rows with small tag pills. Family: compact list-cards.
8. **Project cards with tags**: large left-aligned heading + actions top-right; 4-column media cards (image, title, short desc, tech tag pills). Family: media cards with tags.
9. **Tools split**: left column heading + sub + CTA; right column grid of icon tool tiles. Family: split heading + tool grid.
10. **Mega footer**: logo + social icon row + 5 link columns + locale selector + copyright.

Rhythm notes: single continuous dark theme (no section inversions); alternates centered and left-aligned section headers; photography concentrated in ONE section (proof bento); one accent used sparingly; small-radius cards (~12-16px) with 1px borders; big numerals carry hierarchy; medium density.

Inferred reference dials: VARIANCE ~6, MOTION ~6 (rotating claims, hovers, reveals), DENSITY ~5-6.

---

## 6. Flags requiring user decision (none will be changed silently)

1. "Más de 20 organizaciones" vs 19 partner cards rendered.
2. UNSA partner card has empty `href=""`.
3. Staff bio typo "Santader Tecnología".
4. Events labeled "Próximos" are mostly past dates (countdown target 2026-05-28 already elapsed; data-driven, ordered by -event_start_date).
5. Meta descriptions missing accents ("diseniadores", "Codigo") — preserved verbatim unless approved.
6. Sitemap URL-name mismatch (`events_list` vs `events`).
7. og:image relative path; reglamento canonical empty.
8. CSP script-src may not include jsDelivr (GSAP source) in production settings.

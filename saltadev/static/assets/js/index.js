const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Smooth scroll for same-page anchor links
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const targetId = link.getAttribute('href');
    if (!targetId || targetId === '#') return;
    const target = document.querySelector(targetId);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth' });
  });
});

// Hero 3D background (cerros): desktop only, motion-safe, loaded after the
// page is done so it never competes with LCP. Static poncho backdrop remains
// the fallback when WebGL, viewport or motion preferences rule it out.
const hero3dHost = document.getElementById('hero3d');
if (
  hero3dHost &&
  !prefersReducedMotion &&
  window.matchMedia('(min-width: 1024px)').matches &&
  window.WebGLRenderingContext
) {
  const bootHero3d = () => {
    import('./hero3d.js').then((m) => m.mountHero3D(hero3dHost)).catch(() => {});
  };
  if (document.readyState === 'complete') setTimeout(bootHero3d, 250);
  else window.addEventListener('load', () => setTimeout(bootHero3d, 250), { once: true });
}

// Keep anchored sections clear of the fixed header
const header = document.querySelector('header');
const headerOffset = header ? header.offsetHeight + 12 : 76;
document.querySelectorAll('main section[id]').forEach((section) => {
  section.style.scrollMarginTop = `${headerOffset}px`;
});

// Events carousel: native scroll-snap; buttons only appear when content overflows
const carousel = document.querySelector('[data-carousel]');
const carouselControls = document.querySelector('[data-carousel-controls]');
if (carousel && carouselControls) {
  const prevBtn = carouselControls.querySelector('[data-carousel-prev]');
  const nextBtn = carouselControls.querySelector('[data-carousel-next]');
  const step = () => {
    const card = carousel.querySelector('.event-card');
    return card ? card.getBoundingClientRect().width + 20 : 360;
  };
  const sync = () => {
    const overflows = carousel.scrollWidth > carousel.clientWidth + 4;
    carouselControls.hidden = !overflows;
    if (!overflows) return;
    prevBtn.disabled = carousel.scrollLeft <= 4;
    nextBtn.disabled = carousel.scrollLeft >= carousel.scrollWidth - carousel.clientWidth - 4;
  };
  const scrollByStep = (dir) => {
    carousel.scrollBy({ left: dir * step(), behavior: prefersReducedMotion ? 'auto' : 'smooth' });
  };
  prevBtn.addEventListener('click', () => scrollByStep(-1));
  nextBtn.addEventListener('click', () => scrollByStep(1));
  carousel.addEventListener('scroll', sync, { passive: true });
  window.addEventListener('resize', sync);
  sync();
}

// Partners: toggle the full directory grid under the marquee
const partnersToggle = document.getElementById('togglePartners');
const partnersGrid = document.getElementById('partnersGrid');
const partnersToggleLabel = document.getElementById('togglePartnersLabel');
if (partnersToggle && partnersGrid && partnersToggleLabel) {
  partnersToggle.addEventListener('click', () => {
    const isOpen = partnersGrid.classList.toggle('open');
    partnersToggle.setAttribute('aria-expanded', String(isOpen));
    partnersToggleLabel.textContent = isOpen ? 'Ver menos colaboradores' : 'Ver todos los colaboradores';
    const icon = partnersToggle.querySelector('.material-symbols-outlined');
    if (icon) icon.textContent = isOpen ? 'expand_less' : 'expand_more';
  });
}

if (!prefersReducedMotion && window.gsap) {
  gsap.registerPlugin(ScrollTrigger);

  // Hero entrance: staggered rise, communicates reading order
  gsap.from('[data-hero-item]', {
    y: 22,
    opacity: 0,
    duration: 0.7,
    stagger: 0.09,
    ease: 'power3.out',
  });

  // Section reveals on scroll
  document.querySelectorAll('[data-reveal]').forEach((el) => {
    gsap.from(el, {
      scrollTrigger: { trigger: el, start: 'top 85%' },
      y: 24,
      opacity: 0,
      duration: 0.7,
      ease: 'power2.out',
    });
  });

  // Stat counters roll up once when the strip enters the viewport.
  // Markup already contains the final value, so reduced-motion and no-JS
  // users see the real number without animation.
  document.querySelectorAll('[data-count-to]').forEach((el) => {
    const target = parseInt(el.dataset.countTo, 10);
    if (Number.isNaN(target)) return;
    const prefix = el.dataset.countPrefix || '';
    const state = { n: 0 };
    gsap.to(state, {
      n: target,
      duration: 1.4,
      ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      onUpdate: () => {
        el.textContent = prefix + String(Math.round(state.n));
      },
    });
  });
}

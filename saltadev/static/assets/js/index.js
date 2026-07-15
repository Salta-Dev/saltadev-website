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

// Run each motion subsystem in isolation: one failure must not kill the rest
const safeMotion = (label, fn) => {
  try {
    fn();
  } catch (err) {
    console.warn(`motion subsystem "${label}" skipped:`, err);
  }
};

if (!prefersReducedMotion && window.gsap) {
  gsap.registerPlugin(ScrollTrigger);

  // Card tilt: pointer-driven 3D lean on pillar cards, bento cells and event
  // cards. Fine pointers only (no hover on touch), smoothed with quickTo.
  // Bound first so a failure in any scroll system can never disable it.
  safeMotion('tilt', () => {
    // Input capability is decided per event (pointerType), not via media query:
    // '(hover: hover) and (pointer: fine)' reports false on some real desktop
    // setups (device emulation, hybrid inputs) and silently disabled the effect.
    document.querySelectorAll('[data-tilt], .bento-cell, .event-card').forEach((card) => {
      gsap.set(card, { transformPerspective: 650 });
      const toRotX = gsap.quickTo(card, 'rotationX', { duration: 0.4, ease: 'power2.out' });
      const toRotY = gsap.quickTo(card, 'rotationY', { duration: 0.4, ease: 'power2.out' });
      const toScale = gsap.quickTo(card, 'scale', { duration: 0.4, ease: 'power2.out' });
      card.addEventListener('pointermove', (e) => {
        if (e.pointerType === 'touch') return; // taps must not tilt
        const rect = card.getBoundingClientRect();
        const px = (e.clientX - rect.left) / rect.width - 0.5;
        const py = (e.clientY - rect.top) / rect.height - 0.5;
        toRotX(py * -7);
        toRotY(px * 9);
        toScale(1.015);
      });
      card.addEventListener('pointerleave', () => {
        toRotX(0);
        toRotY(0);
        toScale(1);
      });
    });
  });

  // Hero entrance: staggered rise, communicates reading order
  gsap.from('[data-hero-item]', {
    y: 22,
    opacity: 0,
    duration: 0.7,
    stagger: 0.09,
    ease: 'power3.out',
  });

  // Section reveals on scroll (base rhythm for headers and single blocks)
  document.querySelectorAll('[data-reveal]').forEach((el) => {
    gsap.from(el, {
      scrollTrigger: { trigger: el, start: 'top 85%' },
      y: 24,
      opacity: 0,
      duration: 0.7,
      ease: 'power2.out',
    });
  });

  // Cascading grids (pillars, bento): children rise in reading order
  document.querySelectorAll('[data-stagger]').forEach((group) => {
    gsap.from(group.children, {
      scrollTrigger: { trigger: group, start: 'top 82%' },
      y: 30,
      opacity: 0,
      duration: 0.65,
      stagger: 0.12,
      ease: 'power2.out',
    });
  });

  // Staff rows: enter from the left, one by one, like reading down a list
  document.querySelectorAll('[data-stagger-rows]').forEach((group) => {
    gsap.from(group.children, {
      scrollTrigger: { trigger: group, start: 'top 82%' },
      x: -36,
      opacity: 0,
      duration: 0.6,
      stagger: 0.15,
      ease: 'power2.out',
    });
  });

  // Event cards: slide in from the right, pointing at the carousel direction
  const eventTrack = document.querySelector('.event-track');
  if (eventTrack) {
    gsap.from(eventTrack.children, {
      scrollTrigger: { trigger: eventTrack, start: 'top 82%' },
      x: 64,
      opacity: 0,
      duration: 0.7,
      stagger: 0.1,
      ease: 'power3.out',
    });
  }

  // Norte band: the weave and the franja drift at different speeds (parallax)
  safeMotion('norte-parallax', () => {
    const norteBand = document.querySelector('.norte-band');
    if (!norteBand) return;
    gsap.fromTo(
      norteBand,
      { '--weave-y': '-46px', '--franja-y': '36px' },
      {
        '--weave-y': '46px',
        '--franja-y': '-36px',
        ease: 'none',
        scrollTrigger: { trigger: norteBand, start: 'top bottom', end: 'bottom top', scrub: true },
      }
    );
  });

  // Desktop-only depth: hero photo scrolls slower than the page; the contact
  // heading column drifts slightly against the form. Skipped on stacked
  // mobile layouts where differential motion reads as misalignment.
  const mm = gsap.matchMedia();
  mm.add('(min-width: 1024px)', () => {
    const heroPhoto = document.querySelector('[data-hero-photo]');
    if (heroPhoto) {
      gsap.fromTo(
        heroPhoto,
        { yPercent: -3 },
        {
          yPercent: 7,
          ease: 'none',
          scrollTrigger: { trigger: heroPhoto, start: 'top bottom', end: 'bottom top', scrub: true },
        }
      );
    }
    const contactSlow = document.querySelector('[data-parallax-slow]');
    if (contactSlow) {
      gsap.fromTo(
        contactSlow,
        { y: 44 },
        {
          y: -28,
          ease: 'none',
          scrollTrigger: { trigger: '#contact', start: 'top bottom', end: 'bottom top', scrub: true },
        }
      );
    }
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

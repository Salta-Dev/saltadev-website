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

// Keep anchored sections clear of the fixed header
const header = document.querySelector('header');
const headerOffset = header ? header.offsetHeight + 12 : 76;
document.querySelectorAll('main section[id]').forEach((section) => {
  section.style.scrollMarginTop = `${headerOffset}px`;
});

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

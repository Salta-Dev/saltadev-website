/**
 * SaltaDev Main JavaScript
 * Global functionality for the SaltaDev website
 */

(() => {
  /* ══════════════════════════════════════════════════════════════════════════
     PROGRESS BAR
     ══════════════════════════════════════════════════════════════════════════ */

  const pb = document.getElementById('pb');

  function updateProgressBar() {
    if (!pb) return;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = (window.scrollY / scrollHeight) * 100;
    pb.style.width = `${scrolled}%`;
  }

  /* ══════════════════════════════════════════════════════════════════════════
     NAVBAR SCROLL EFFECT
     ══════════════════════════════════════════════════════════════════════════ */

  const nav = document.getElementById('nav');

  function updateNavbar() {
    if (!nav) return;
    nav.classList.toggle('on', window.scrollY > 50);
  }

  /* ══════════════════════════════════════════════════════════════════════════
     BACK TO TOP BUTTON
     ══════════════════════════════════════════════════════════════════════════ */

  const btt = document.getElementById('btt');

  function updateBackToTop() {
    if (!btt) return;
    btt.classList.toggle('show', window.scrollY > 400);
  }

  if (btt) {
    btt.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ══════════════════════════════════════════════════════════════════════════
     COMBINED SCROLL HANDLER
     ══════════════════════════════════════════════════════════════════════════ */

  window.addEventListener(
    'scroll',
    () => {
      updateProgressBar();
      updateNavbar();
      updateBackToTop();
    },
    { passive: true },
  );

  /* ══════════════════════════════════════════════════════════════════════════
     MOBILE MENU
     ══════════════════════════════════════════════════════════════════════════ */

  const mob = document.getElementById('mob');
  const ham = document.getElementById('ham');
  const mobX = document.getElementById('mobX');

  function openMob() {
    if (mob) mob.classList.add('open');
  }

  function closeMob() {
    if (mob) mob.classList.remove('open');
  }

  if (ham) {
    ham.addEventListener('click', openMob);
  }

  if (mobX) {
    mobX.addEventListener('click', closeMob);
    mobX.addEventListener('touchend', (e) => {
      e.preventDefault();
      closeMob();
    });
  }

  // Close on backdrop click
  if (mob) {
    mob.addEventListener('click', (e) => {
      if (e.target === mob) closeMob();
    });
  }

  // Close menu when clicking on links
  document.querySelectorAll('.mob a').forEach((link) => {
    link.addEventListener('click', closeMob);
  });

  /* ══════════════════════════════════════════════════════════════════════════
     REVEAL ON SCROLL
     ══════════════════════════════════════════════════════════════════════════ */

  function initReveal() {
    const els = document.querySelectorAll('.rv, .rv-l');
    if (!els.length) return;

    try {
      if (!('IntersectionObserver' in window)) {
        // Fallback: show all elements if IntersectionObserver not supported
        els.forEach((el) => {
          el.classList.add('in');
        });
        return;
      }

      // Mark elements for animation (hidden state)
      els.forEach((el) => {
        if (!el.classList.contains('in')) {
          el.classList.add('anim');
        }
      });

      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('in');
              io.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.05, rootMargin: '0px 0px -20px 0px' },
      );

      els.forEach((el) => {
        if (!el.classList.contains('in')) {
          io.observe(el);
        }
      });

      // Safety fallback: reveal all after 600ms in case observer never fires
      setTimeout(() => {
        els.forEach((el) => {
          el.classList.add('in');
        });
      }, 600);
    } catch (_e) {
      // If anything fails, just show everything
      els.forEach((el) => {
        el.classList.add('in');
      });
    }
  }

  // Initialize reveal on page load
  initReveal();

  /* ══════════════════════════════════════════════════════════════════════════
     COUNTER ANIMATION
     ══════════════════════════════════════════════════════════════════════════ */

  function initCounters() {
    var counters = document.querySelectorAll('.counter');
    if (!counters.length) return;

    if (!('IntersectionObserver' in window)) {
      // Fallback: show final values immediately
      counters.forEach((el) => {
        var target = parseInt(el.dataset.t, 10);
        el.textContent = target.toLocaleString('es-AR');
      });
      return;
    }

    var io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            countUp(e.target);
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.5 },
    );

    counters.forEach((el) => {
      io.observe(el);
    });
  }

  function countUp(el) {
    var target = parseInt(el.dataset.t, 10);
    var duration = 1800;
    var start = performance.now();

    function easeOutQuad(t) {
      return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }

    function update(now) {
      var elapsed = Math.min((now - start) / duration, 1);
      var value = Math.round(easeOutQuad(elapsed) * target);
      el.textContent = value.toLocaleString('es-AR');
      if (elapsed < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = target.toLocaleString('es-AR');
      }
    }

    requestAnimationFrame(update);
  }

  // Initialize counters on page load
  initCounters();

  /* ══════════════════════════════════════════════════════════════════════════
     PARTNERS MARQUEE & GRID
     ══════════════════════════════════════════════════════════════════════════ */

  // Partners data should be passed from Django via a script tag
  // Example: <script>const PARTNERS = {{ partners_json|safe }};</script>

  function renderMarquee() {
    var track = document.getElementById('mtrack');
    if (!track || typeof PARTNERS === 'undefined') return;

    // Duplicate array for infinite scroll effect
    var allPartners = PARTNERS.concat(PARTNERS);

    allPartners.forEach((p) => {
      var a = document.createElement('a');
      a.className = 'mpill';
      a.href = p.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.innerHTML =
        '<img src="' +
        p.img +
        '" alt="' +
        p.n +
        '" loading="lazy" onerror="this.style.display=\'none\'"/>' +
        '<span>' +
        p.n +
        '</span>';
      track.appendChild(a);
    });
  }

  function renderGrid() {
    var grid = document.getElementById('pgrid');
    if (!grid || typeof PARTNERS === 'undefined') return;

    grid.innerHTML = PARTNERS.map(
      (p) =>
        '<a class="pcard rv" href="' +
        p.url +
        '" target="_blank" rel="noopener">' +
        '<img src="' +
        p.img +
        '" alt="' +
        p.n +
        '" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'"/>' +
        '<div class="pcard-fb" style="display:none">' +
        p.n.slice(0, 2).toUpperCase() +
        '</div>' +
        '<span>' +
        p.n +
        '</span>' +
        '</a>',
    ).join('');

    // Re-initialize reveal for new elements
    initReveal();
  }

  // Initialize marquee on page load
  renderMarquee();

  // Toggle between marquee and grid
  var expanded = false;
  var showMoreBtn = document.getElementById('showMoreBtn');

  if (showMoreBtn) {
    showMoreBtn.addEventListener('click', () => {
      expanded = !expanded;
      var mw = document.getElementById('marqueeWrap');
      var g = document.getElementById('pgrid');

      if (expanded) {
        if (mw) mw.style.display = 'none';
        if (g) g.style.display = 'grid';
        renderGrid();
        showMoreBtn.innerHTML = '<span class="material-symbols-outlined ms">expand_less</span>Ver carrusel';
      } else {
        if (g) g.style.display = 'none';
        if (mw) mw.style.display = '';
        showMoreBtn.innerHTML =
          '<span class="material-symbols-outlined ms">expand_more</span>Ver todos los colaboradores';
      }
    });
  }

  /* ══════════════════════════════════════════════════════════════════════════
     EVENT FILTER BUTTONS
     ══════════════════════════════════════════════════════════════════════════ */

  document.querySelectorAll('.filt').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filt').forEach((b) => {
        b.classList.remove('on');
      });
      btn.classList.add('on');
      // TODO: Implement actual filtering logic
    });
  });

  /* ══════════════════════════════════════════════════════════════════════════
     TABLE OF CONTENTS SPY (Code of Conduct)
     ══════════════════════════════════════════════════════════════════════════ */

  function initTocSpy() {
    var sections = document.querySelectorAll('.rgsec');
    if (!sections.length || !('IntersectionObserver' in window)) return;

    sections.forEach((sec) => {
      new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              document.querySelectorAll('.tl').forEach((l) => {
                l.classList.remove('on');
              });
              const link = document.querySelector(`.tl[href="#${e.target.id}"]`);
              if (link) link.classList.add('on');
            }
          });
        },
        { rootMargin: '-25% 0px -60% 0px' },
      ).observe(sec);
    });
  }

  // Smooth scroll for TOC links
  document.querySelectorAll('.tl').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      var target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  initTocSpy();

  /* ══════════════════════════════════════════════════════════════════════════
     CONTACT FORM (Progressive enhancement)
     ══════════════════════════════════════════════════════════════════════════ */

  var contactForm = document.getElementById('cform');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      // Only handle via AJAX if the form has an action URL
      var action = contactForm.getAttribute('action');
      if (!action || action === '#') {
        e.preventDefault();
        // Demo mode: show toast
        showToast('Mensaje enviado correctamente');
        contactForm.reset();
        return;
      }

      // If using AJAX submission
      if (contactForm.dataset.ajax === 'true') {
        e.preventDefault();
        const btn = contactForm.querySelector('.fsub');
        if (!btn) return;

        btn.innerHTML = '<span class="material-symbols-outlined ms ms-f">hourglass_empty</span>Enviando...';
        btn.disabled = true;

        fetch(action, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrf(),
          },
          body: new FormData(contactForm),
        })
          .then((res) => {
            if (res.ok) {
              btn.innerHTML = '<span class="material-symbols-outlined ms ms-f">check_circle</span>Enviado';
              showToast('Mensaje enviado correctamente');
              setTimeout(() => {
                btn.innerHTML = '<span class="material-symbols-outlined ms ms-f">send</span>Enviar Mensaje';
                btn.disabled = false;
                contactForm.reset();
              }, 3500);
            } else {
              throw new Error('Error');
            }
          })
          .catch(() => {
            btn.innerHTML = '<span class="material-symbols-outlined ms ms-f">send</span>Enviar Mensaje';
            btn.disabled = false;
            showToast('Error al enviar. Intenta de nuevo.', 'error');
          });
      }
    });
  }

  function getCsrf() {
    var input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;

    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith('csrftoken=')) {
        return cookie.substring(10);
      }
    }
    return '';
  }

  /* ══════════════════════════════════════════════════════════════════════════
     TOAST NOTIFICATIONS
     ══════════════════════════════════════════════════════════════════════════ */

  function showToast(message, type) {
    var toast = document.getElementById('toast');
    var toastTxt = document.getElementById('toastTxt');
    if (!toast || !toastTxt) return;

    toastTxt.textContent = message;

    // Update icon based on type
    var icon = toast.querySelector('.ms');
    if (icon) {
      if (type === 'error') {
        icon.textContent = 'error';
        icon.style.color = '#ef4444';
      } else {
        icon.textContent = 'check_circle';
        icon.style.color = '#4ade80';
      }
    }

    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 5000);
  }

  // Expose showToast globally for use in templates
  window.showToast = showToast;

  /* ══════════════════════════════════════════════════════════════════════════
     MAGNETIC BUTTONS (optional enhancement)
     ══════════════════════════════════════════════════════════════════════════ */

  function initMagneticButtons() {
    var buttons = document.querySelectorAll('.btn-p, .btn-g, .ev-reg');
    buttons.forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        var rect = btn.getBoundingClientRect();
        var x = (e.clientX - rect.left - rect.width / 2) * 0.12;
        var y = (e.clientY - rect.top - rect.height / 2) * 0.12;
        btn.style.transform = `translateY(-2px) translate(${x}px, ${y}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
      });
    });
  }

  // Only enable magnetic buttons on desktop
  if (window.innerWidth > 768) {
    initMagneticButtons();
  }

  /* ══════════════════════════════════════════════════════════════════════════
     NAV SECTION SPY (Active link highlighting)
     ══════════════════════════════════════════════════════════════════════════ */

  function initNavSpy() {
    var sections = ['inicio', 'partners', 'community', 'eventos-preview', 'staff', 'contacto'];

    sections.forEach((id) => {
      var el = document.getElementById(id);
      if (!el || !('IntersectionObserver' in window)) return;

      new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              document.querySelectorAll('.nl').forEach((a) => {
                a.classList.remove('act');
              });
              const match = document.querySelector(`.nl[data-sec="${id}"]`);
              if (match) match.classList.add('act');
            }
          });
        },
        { rootMargin: '-35% 0px -55% 0px' },
      ).observe(el);
    });
  }

  initNavSpy();

  /* ══════════════════════════════════════════════════════════════════════════
     HERO PARALLAX (optional enhancement)
     ══════════════════════════════════════════════════════════════════════════ */

  var hero = document.querySelector('.hero');
  if (hero) {
    window.addEventListener(
      'scroll',
      () => {
        hero.style.backgroundPositionY = `${window.scrollY * 0.25}px`;
      },
      { passive: true },
    );
  }
})();

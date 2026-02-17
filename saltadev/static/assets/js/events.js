// Countdown functionality
function initCountdown() {
  const dateElement = document.getElementById('currentEventDate');
  if (!dateElement || !dateElement.textContent.trim()) return;

  const eventDate = new Date(dateElement.textContent.trim());
  if (isNaN(eventDate.getTime())) return;

  function updateCountdown() {
    const now = new Date();
    const diff = eventDate - now;

    if (diff <= 0) {
      document.getElementById('countdown-container').style.display = 'none';
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    updateElement('js-days', days);
    updateElement('js-hours', hours);
    updateElement('js-minutes', minutes);
    updateElement('js-seconds', seconds);
  }

  function updateElement(id, value) {
    const el = document.getElementById(id);
    if (!el) return;

    let span = el.querySelector('span');
    if (!span) {
      span = document.createElement('span');
      el.appendChild(span);
    }
    span.textContent = value.toString().padStart(2, '0');
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);
}

// Events toggle functionality
const eventsToggle = document.getElementById('toggleEvents');
const eventsList = document.getElementById('eventsList');
const eventsToggleLabel = document.getElementById('toggleEventsLabel');

if (eventsToggle && eventsList && eventsToggleLabel) {
  eventsToggle.addEventListener('click', () => {
    const isExpanded = eventsToggle.getAttribute('aria-expanded') === 'true';
    eventsToggle.setAttribute('aria-expanded', String(!isExpanded));
    eventsList.classList.toggle('events-expanded', !isExpanded);
    eventsToggle.querySelector('span.material-symbols-outlined').textContent = !isExpanded
      ? 'expand_less'
      : 'expand_more';
    eventsToggleLabel.textContent = !isExpanded ? 'Mostrar menos eventos' : 'Cargar eventos anteriores';
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initCountdown);

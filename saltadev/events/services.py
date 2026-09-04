"""Shared event persistence helpers used by the form and the ingest API."""

from datetime import datetime

from content.models import Event
from django.core.cache import cache
from django.utils import timezone
from django.utils.text import slugify

HOME_EVENTS_CACHE_KEY = "home_latest_events"

MONTHS_ES = [
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


def invalidate_home_events_cache() -> None:
    """Drop the homepage events cache so a new card is visible immediately."""
    cache.delete(HOME_EVENTS_CACHE_KEY)


def next_upcoming_event() -> Event | None:
    """Return the approved event that starts soonest from now."""
    return (
        Event.objects.filter(
            status=Event.Status.APPROVED,
            event_start_date__gte=timezone.now(),
        )
        .select_related("creator")
        .order_by("event_start_date", "pk")
        .first()
    )


def assign_event_display_fields(event: Event) -> None:
    """Fill Spanish date/time display fields from the start datetime if missing."""
    start_datetime: datetime | None = event.event_start_date
    if not start_datetime:
        return
    if not event.event_date_display:
        event.event_date_display = (
            f"{start_datetime.day} de {MONTHS_ES[start_datetime.month]}"
        )
    if not event.event_time_display:
        event.event_time_display = start_datetime.strftime("%H:%M hs")


_KIND_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        Event.Kind.HACKATHON,
        ("hackaton", "hackathon", "hackatón", "datathon", "challenge"),
    ),
    (Event.Kind.WORKSHOP, ("taller", "workshop")),
    (Event.Kind.TALK, ("charla", "conferencia", "keynote")),
    (Event.Kind.SOCIAL, ("after", "birra", "networking", "adminbirra")),
)


def infer_event_kind(title: str, description: str = "") -> str:
    """Map free text to an Event.Kind, defaulting to meetup."""
    haystack = f"{title} {description}".casefold()
    for kind, keywords in _KIND_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return kind
    return Event.Kind.MEETUP


def assign_event_kind(event: Event) -> None:
    """Infer kind when the organizer left the default meetup value."""
    if event.kind and event.kind != Event.Kind.MEETUP:
        return
    event.kind = infer_event_kind(event.title, event.description)


def assign_event_slug(event: Event) -> None:
    """Generate a unique slug from the title when the event has none."""
    if event.slug:
        return
    base_slug = slugify(event.title) or "evento"
    slug = base_slug
    counter = 1
    while Event.objects.filter(slug=slug).exclude(pk=event.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    event.slug = slug


def prepare_event_for_save(event: Event) -> None:
    """Apply display fields, kind, and slug before persisting an event."""
    assign_event_display_fields(event)
    assign_event_kind(event)
    assign_event_slug(event)

"""Shared event persistence helpers used by the form and the ingest API."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from urllib.parse import urlparse, urlunparse

from content.models import Event
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.text import slugify

HOME_EVENTS_CACHE_KEY = "home_latest_events"
_DUPLICATE_SCAN_LIMIT = 200
_EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001faff"
    "\U00002700-\U000027bf"
    "\U0001f1e0-\U0001f1ff"
    "]+",
    flags=re.UNICODE,
)

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


def normalize_event_title(title: str) -> str:
    """Collapse whitespace and strip emoji/punctuation so near-identical titles match."""
    without_emoji = _EMOJI_RE.sub(" ", title)
    cleaned = "".join(
        char
        for char in without_emoji
        if unicodedata.category(char)[0] not in {"S", "C", "P"}
    )
    return re.sub(r"\s+", " ", cleaned).strip().casefold()


def normalize_event_link(link: str) -> str:
    """Normalize registration URLs for duplicate comparison."""
    raw = link.strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    scheme = (parsed.scheme or "https").casefold()
    netloc = parsed.netloc.casefold()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


def _same_start_day(left: datetime | None, right: datetime | None) -> bool:
    """Return True when both datetimes fall on the same calendar day."""
    if left is None or right is None:
        return False
    left_day: date = timezone.localtime(left).date()
    right_day: date = timezone.localtime(right).date()
    return left_day == right_day


def find_duplicate_event(
    *,
    title: str,
    link: str = "",
    event_start_date: datetime | None = None,
    event_date_display: str = "",
    queryset: QuerySet[Event] | None = None,
) -> Event | None:
    """Return an existing event that matches link or title+date.

    Matching rules (first hit wins):
    1. Same normalized registration link (when both are non-empty).
    2. Same normalized title and same start calendar day.
    3. Same normalized title and same date_display text.
    """
    norm_title = normalize_event_title(title)
    norm_link = normalize_event_link(link)
    norm_display = event_date_display.strip().casefold()
    if not norm_title and not norm_link:
        return None

    candidates = queryset or Event.objects.order_by("-created_at", "-pk")
    for event in candidates[:_DUPLICATE_SCAN_LIMIT]:
        if norm_link and event.link and normalize_event_link(event.link) == norm_link:
            return event
        if not norm_title:
            continue
        if normalize_event_title(event.title) != norm_title:
            continue
        if _same_start_day(event_start_date, event.event_start_date):
            return event
        existing_display = (event.event_date_display or "").strip().casefold()
        if norm_display and existing_display and norm_display == existing_display:
            return event
    return None

"""Tests for event kind inference and public semantic badges."""

from datetime import timedelta

import pytest
from content.models import Event
from django.urls import reverse
from django.utils import timezone
from events.forms import EventForm
from events.services import infer_event_kind, prepare_event_for_save


@pytest.mark.parametrize(
    ("title", "description", "expected"),
    [
        ("Charla de Python en UCASAL", "", Event.Kind.TALK),
        ("Taller de Git", "Hands-on", Event.Kind.WORKSHOP),
        ("Hackatón PunaTech", "", Event.Kind.HACKATHON),
        ("After office y birras", "", Event.Kind.SOCIAL),
        ("Devin llega a Salta", "Primer meetup", Event.Kind.MEETUP),
    ],
)
def test_infer_event_kind(title: str, description: str, expected: str) -> None:
    """Titles and copy should map to a community-facing event kind."""
    assert infer_event_kind(title, description) == expected


@pytest.mark.django_db
def test_prepare_infers_kind_when_default_meetup() -> None:
    """Ingest/save should upgrade the default meetup when copy is more specific."""
    event = Event(title="Taller de Django", description="")
    prepare_event_for_save(event)
    assert event.kind == Event.Kind.WORKSHOP


@pytest.mark.django_db
def test_prepare_keeps_explicit_kind() -> None:
    """An organizer-chosen kind must not be overwritten by keywords."""
    event = Event(title="Charla abierta", kind=Event.Kind.SOCIAL)
    prepare_event_for_save(event)
    assert event.kind == Event.Kind.SOCIAL


@pytest.mark.django_db
def test_online_location_is_virtual_modality() -> None:
    """Virtual venues should surface an Online badge."""
    event = Event(title="Meetup", location="Discord / virtual")
    assert event.is_online is True
    assert event.modality_label == "Online"


@pytest.mark.django_db
def test_physical_location_is_presencial() -> None:
    """A street address should surface Presencial."""
    event = Event(title="Meetup", location="Espacio X, Salta")
    assert event.is_online is False
    assert event.modality_label == "Presencial"


def test_form_accepts_kind_without_breaking_existing_payloads() -> None:
    """Legacy form posts without kind stay valid and default to meetup."""
    form = EventForm(
        data={"title": "Meetup de septiembre", "description": "Nos juntamos"}
    )
    assert form.is_valid()
    event = form.save(commit=False)
    assert event.kind == Event.Kind.MEETUP


@pytest.mark.django_db
def test_events_list_shows_kind_and_modality_badges(client, db) -> None:
    """Public cards should show type and modality, not only a date line."""
    Event.objects.create(
        title="Charla de arquitectura",
        description="Charla abierta",
        location="Virtual por Discord",
        slug="charla-arquitectura",
        status=Event.Status.APPROVED,
        kind=Event.Kind.TALK,
        event_start_date=timezone.now() + timedelta(days=4),
        event_date_display="10 de Septiembre",
        event_time_display="19:00 hs",
    )
    html = client.get(reverse("events")).content.decode()
    assert "Charla" in html
    assert "Online" in html


@pytest.mark.django_db
def test_events_list_filters_by_kind(client, db) -> None:
    """?tipo= should keep only matching approved events."""
    Event.objects.create(
        title="Taller de testing",
        slug="taller-testing",
        status=Event.Status.APPROVED,
        kind=Event.Kind.WORKSHOP,
        event_start_date=timezone.now() + timedelta(days=2),
    )
    Event.objects.create(
        title="Meetup mensual",
        slug="meetup-mensual",
        status=Event.Status.APPROVED,
        kind=Event.Kind.MEETUP,
        event_start_date=timezone.now() + timedelta(days=3),
    )
    html = client.get(reverse("events") + "?tipo=workshop").content.decode()
    assert "Taller de testing" in html
    assert "Meetup mensual" not in html

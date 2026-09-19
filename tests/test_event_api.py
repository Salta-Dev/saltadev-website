"""Tests for the internal event ingest API."""

import pytest
from content.models import Event
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from django.urls import reverse
from events.services import HOME_EVENTS_CACHE_KEY

INGEST_TOKEN = "test-ingest-token"
INGEST_URL = "/api/internal/events/"

VALID_PAYLOAD = {
    "title": "PunaTech 2026",
    "description": "3 días a pura IA",
    "location": "Av. Independencia 910",
    "link": "https://www.punatech.ar",
    "event_start_date": "2026-05-28T09:00:00-03:00",
    "event_end_date": "2026-05-30T19:00:00-03:00",
    "event_date_display": "28, 29 y 30 de Mayo",
    "event_time_display": "9:00 a 19:00",
}


def _auth_headers(token: str = INGEST_TOKEN) -> dict[str, str]:
    """Return Authorization header for the ingest token."""
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.django_db
class TestInternalCreateEvent:
    """Tests for POST /api/internal/events/."""

    def test_unauthorized_without_token(self, client, settings):
        """Missing bearer token should return 401."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
        )
        assert response.status_code == 401
        assert Event.objects.count() == 0

    def test_unauthorized_with_wrong_token(self, client, settings):
        """A mismatched token should return 401."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers("wrong-token-value"),
        )
        assert response.status_code == 401
        assert Event.objects.count() == 0

    def test_unauthorized_when_token_not_configured(self, client, settings):
        """An empty configured token should reject every request."""
        settings.SALTADEV_INGEST_TOKEN = ""
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers("anything"),
        )
        assert response.status_code == 401

    def test_creates_approved_event(self, client, settings):
        """A valid payload should create an approved event with slug."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 201
        body = response.json()
        event = Event.objects.get(pk=body["id"])
        assert event.title == "PunaTech 2026"
        assert event.status == Event.Status.APPROVED
        assert event.slug.startswith("punatech-2026")
        assert event.link == "https://www.punatech.ar"
        assert event.location == "Av. Independencia 910"
        assert body["slug"] == event.slug
        site_url = settings.SITE_URL.rstrip("/")
        assert body["url"] == f"{site_url}{event.get_absolute_url()}"
        assert body["url"].endswith(f"/eventos/{event.slug}/")

    def test_missing_title_returns_400(self, client, settings):
        """Title is required."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        payload = {**VALID_PAYLOAD, "title": ""}
        response = client.post(
            INGEST_URL,
            data=payload,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 400
        assert Event.objects.count() == 0

    def test_invalid_json_returns_400(self, client, settings):
        """Malformed JSON should return 400."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.post(
            INGEST_URL,
            data="{not-json",
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 400

    def test_duplicate_slug_gets_suffix(self, client, settings):
        """A colliding title without link/date match should get a unique slug suffix."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        Event.objects.create(title="PunaTech 2026", slug="punatech-2026")
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 201
        assert response.json()["slug"] == "punatech-2026-1"

    def test_duplicate_link_returns_409(self, client, settings):
        """Re-ingesting the same registration link should not create another event."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        existing = Event.objects.create(
            title="Otro título",
            slug="otro-titulo",
            link="https://www.punatech.ar/",
            status=Event.Status.APPROVED,
        )
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 409
        body = response.json()
        assert body["error"] == "duplicate"
        assert body["event"]["id"] == existing.pk
        assert Event.objects.count() == 1

    def test_duplicate_title_and_date_returns_409(self, client, settings):
        """Same title and start day should be rejected even with a different link."""
        from datetime import datetime
        from zoneinfo import ZoneInfo

        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        existing = Event.objects.create(
            title="¡PunaTech 2026! 🚀",
            slug="punatech-emoji",
            link="https://example.com/other",
            event_start_date=datetime(2026, 5, 28, 12, 0, tzinfo=ZoneInfo("America/Argentina/Buenos_Aires")),
            status=Event.Status.APPROVED,
        )
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 409
        assert response.json()["event"]["id"] == existing.pk
        assert Event.objects.count() == 1

    def test_invalidates_home_cache_and_shows_on_home(self, client, settings):
        """A newly ingested event should appear on the homepage immediately."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        cache.set(HOME_EVENTS_CACHE_KEY, [], 60)
        response = client.post(
            INGEST_URL,
            data=VALID_PAYLOAD,
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 201
        home = client.get(reverse("home"))
        assert home.status_code == 200
        titles = [event.title for event in home.context["latest_events"]]
        assert "PunaTech 2026" in titles
        assert "PunaTech 2026" in home.content.decode()

    def test_multipart_photo_is_stored_and_shown(self, client, settings, tmp_path):
        """A photo file should be saved and used instead of the community fallback."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        settings.MEDIA_ROOT = tmp_path
        settings.MEDIA_URL = "/media/"
        png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        uploaded = SimpleUploadedFile("flyer.png", png, content_type="image/png")
        response = client.post(
            INGEST_URL,
            data={**VALID_PAYLOAD, "photo": uploaded},
            headers=_auth_headers(),
        )
        assert response.status_code == 201
        event = Event.objects.get(pk=response.json()["id"])
        assert "/media/events/" in event.photo
        assert event.photo.endswith(".png")
        home = client.get(reverse("home"))
        assert event.photo in home.content.decode()


@pytest.mark.django_db
class TestInternalUpdateEvent:
    """Tests for PATCH /api/internal/events/<id>/."""

    def test_unauthorized_without_token(self, client, settings):
        """Missing bearer token should return 401."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        event = Event.objects.create(title="Patch me", slug="patch-me")
        response = client.patch(
            f"{INGEST_URL}{event.pk}/",
            data={"title": "Nuevo"},
            content_type="application/json",
        )
        assert response.status_code == 401
        event.refresh_from_db()
        assert event.title == "Patch me"

    def test_not_found(self, client, settings):
        """Unknown event id should return 404."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.patch(
            f"{INGEST_URL}99999/",
            data={"title": "Nuevo"},
            content_type="application/json",
            headers=_auth_headers(),
        )
        assert response.status_code == 404

    def test_updates_title_and_photo(self, client, settings, tmp_path):
        """A patch can replace title and photo of an ingested event."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        settings.MEDIA_ROOT = tmp_path
        settings.MEDIA_URL = "/media/"
        event = Event.objects.create(
            title="Foto mala",
            slug="foto-mala",
            photo="https://example.com/old.jpg",
            status=Event.Status.APPROVED,
        )
        png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
            b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        uploaded = SimpleUploadedFile("fixed.png", png, content_type="image/png")
        response = client.generic(
            "PATCH",
            f"{INGEST_URL}{event.pk}/",
            data=encode_multipart(
                BOUNDARY, {"title": "Foto corregida", "photo": uploaded}
            ),
            content_type=MULTIPART_CONTENT,
            headers=_auth_headers(),
        )
        assert response.status_code == 200, response.content
        event.refresh_from_db()
        assert event.title == "Foto corregida"
        assert "/media/events/" in event.photo
        assert event.photo.endswith(".png")
        body = response.json()
        assert body["id"] == event.pk
        assert body["url"].endswith(f"/eventos/{event.slug}/")

    def test_latest_returns_most_recent(self, client, settings):
        """Staff can fetch the most recently ingested event."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        Event.objects.create(title="Viejo", slug="viejo")
        recent = Event.objects.create(title="Reciente", slug="reciente")
        response = client.get(f"{INGEST_URL}latest/", headers=_auth_headers())
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == recent.pk
        assert body["title"] == "Reciente"

    def test_list_returns_recent_events(self, client, settings):
        """GET collection should list recent events for the bot picker."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        Event.objects.create(title="Uno", slug="uno")
        Event.objects.create(title="Dos", slug="dos")
        response = client.get(INGEST_URL, headers=_auth_headers())
        assert response.status_code == 200
        titles = [item["title"] for item in response.json()["events"]]
        assert titles == ["Dos", "Uno"]

    def test_list_unauthorized(self, client, settings):
        """Listing events without a token should return 401."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        response = client.get(INGEST_URL)
        assert response.status_code == 401

    def test_delete_removes_event(self, client, settings):
        """DELETE should remove the event and invalidate the home cache."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        event = Event.objects.create(title="Borrar", slug="borrar")
        response = client.delete(f"{INGEST_URL}{event.pk}/", headers=_auth_headers())
        assert response.status_code == 200
        assert not Event.objects.filter(pk=event.pk).exists()

    def test_delete_unauthorized(self, client, settings):
        """DELETE without a token should not remove the event."""
        settings.SALTADEV_INGEST_TOKEN = INGEST_TOKEN
        event = Event.objects.create(title="Seguir", slug="seguir")
        response = client.delete(f"{INGEST_URL}{event.pk}/")
        assert response.status_code == 401
        assert Event.objects.filter(pk=event.pk).exists()

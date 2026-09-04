"""Tests for the public event detail page."""

import re
from datetime import timedelta
from urllib.parse import urlparse

import pytest
from content.models import Event
from django.urls import reverse
from django.utils import timezone


def _sitemap_loc_paths(xml: str) -> list[str]:
    """Return path components of each sitemap <loc> (own URL, not a prefix)."""
    return [urlparse(loc).path for loc in re.findall(r"<loc>([^<]+)</loc>", xml)]


@pytest.fixture
def meetup_salta(db):
    """Create an approved public event with slug meetup-salta."""
    return Event.objects.create(
        title="Meetup Salta",
        description="Encuentro mensual de la comunidad.",
        location="Salta, Argentina",
        photo="https://example.com/meetup.jpg",
        link="https://example.com/register",
        slug="meetup-salta",
        status=Event.Status.APPROVED,
        event_start_date=timezone.now() + timedelta(days=7),
        event_end_date=timezone.now() + timedelta(days=7, hours=3),
        event_date_display="9 de Septiembre",
        event_time_display="18:00",
    )


@pytest.fixture
def pending_event(db):
    """Create a pending event with slug pendiente."""
    return Event.objects.create(
        title="Evento Pendiente",
        slug="pendiente",
        status=Event.Status.PENDING,
        event_start_date=timezone.now() + timedelta(days=10),
    )


@pytest.fixture
def rejected_event(db):
    """Create a rejected event with slug rechazado."""
    return Event.objects.create(
        title="Evento Rechazado",
        slug="rechazado",
        status=Event.Status.REJECTED,
        event_start_date=timezone.now() + timedelta(days=11),
    )


def _detail_url(slug: str) -> str:
    """Build the public event detail URL for a slug."""
    return reverse("event_detail", kwargs={"slug": slug})


@pytest.mark.django_db
class TestEventDetailVisibility:
    """Approved-only public detail: 200 for APPROVED, 404 otherwise."""

    def test_approved_slug_returns_200(self, client, meetup_salta):
        """Approved meetup-salta returns 200 and shows the event."""
        response = client.get(_detail_url("meetup-salta"))
        assert response.status_code == 200
        assert meetup_salta.title in response.content.decode()

    def test_missing_slug_returns_404(self, client):
        """Unknown slug returns 404."""
        response = client.get(_detail_url("no-existe"))
        assert response.status_code == 404

    def test_pending_slug_returns_404(self, client, pending_event):
        """Pending events are not publicly visible."""
        response = client.get(_detail_url("pendiente"))
        assert response.status_code == 404

    def test_rejected_slug_returns_404(self, client, rejected_event):
        """Rejected events are not publicly visible."""
        response = client.get(_detail_url("rechazado"))
        assert response.status_code == 404

    def test_pending_returns_404_for_staff(self, client, pending_event, admin_user):
        """Staff must not see pending events on the public URL."""
        client.force_login(admin_user)
        response = client.get(_detail_url("pendiente"))
        assert response.status_code == 404

    def test_rejected_returns_404_for_staff(self, client, rejected_event, admin_user):
        """Staff must not see rejected events on the public URL."""
        client.force_login(admin_user)
        response = client.get(_detail_url("rechazado"))
        assert response.status_code == 404


@pytest.mark.django_db
class TestEventGetAbsoluteUrl:
    """Event.get_absolute_url points at the public detail route."""

    def test_get_absolute_url_matches_event_detail(self, meetup_salta):
        """Absolute URL equals reverse of event_detail for meetup-salta."""
        assert meetup_salta.get_absolute_url() == reverse(
            "event_detail", kwargs={"slug": meetup_salta.slug}
        )

    def test_get_absolute_url_uses_event_slug(self, event):
        """Absolute URL includes the event's own slug."""
        assert event.get_absolute_url() == reverse(
            "event_detail", kwargs={"slug": event.slug}
        )
        assert event.slug in event.get_absolute_url()


@pytest.fixture
def blank_optional_event(db):
    """Approved event with empty optional fields."""
    return Event.objects.create(
        title="Evento Mínimo",
        description="",
        location="",
        photo="",
        link="",
        slug="evento-minimo",
        status=Event.Status.APPROVED,
        event_start_date=timezone.now() + timedelta(days=3),
    )


@pytest.fixture
def datetime_only_event(db):
    """Approved event with datetimes but blank display fields."""
    start = timezone.now() + timedelta(days=4)
    return Event.objects.create(
        title="Evento Sin Display",
        description="Descripción de fallback.",
        location="Tartagal",
        photo="assets/img/custom-event.jpg",
        link="",
        slug="evento-sin-display",
        status=Event.Status.APPROVED,
        event_start_date=start,
        event_end_date=start + timedelta(hours=2),
        event_date_display="",
        event_time_display="",
    )


@pytest.mark.django_db
class TestEventDetailTemplate:
    """Visible fields, blank optionals, and register CTA."""

    def test_populated_event_shows_required_fields(self, client, meetup_salta):
        """Title, description, dates, location, and photo are visible."""
        response = client.get(_detail_url("meetup-salta"))
        html = response.content.decode()
        assert meetup_salta.title in html
        assert meetup_salta.description in html
        assert meetup_salta.location in html
        assert meetup_salta.event_date_display in html
        assert meetup_salta.event_time_display in html
        assert meetup_salta.photo in html

    def test_photo_is_contained_not_fullscreen(self, client, meetup_salta):
        """Detail flyer stays in a capped frame instead of filling the viewport."""
        html = client.get(_detail_url("meetup-salta")).content.decode()
        assert "event-detail-card" in html
        assert "event-detail-cover" in html
        assert "Volver a eventos" in html

    def test_blank_optionals_still_200_with_title(self, client, blank_optional_event):
        """Empty optionals still render 200 with the title and no empty src."""
        response = client.get(_detail_url("evento-minimo"))
        html = response.content.decode()
        assert response.status_code == 200
        assert blank_optional_event.title in html
        srcs = re.findall(r'<img[^>]+src="([^"]*)"', html)
        assert srcs
        assert all(src.strip() for src in srcs)
        assert "seed-latam-salta-960w.webp" in html

    def test_relative_photo_uses_rooted_path(self, client, datetime_only_event):
        """Non-http photo is served from a rooted path."""
        response = client.get(_detail_url("evento-sin-display"))
        html = response.content.decode()
        assert response.status_code == 200
        assert f"/{datetime_only_event.photo}" in html
        assert str(datetime_only_event.event_start_date.day) in html

    def test_cta_when_link_set(self, client, meetup_salta):
        """Register CTA uses event.link and Spanish copy."""
        response = client.get(_detail_url("meetup-salta"))
        html = response.content.decode()
        assert meetup_salta.link in html
        assert "Inscribirse" in html
        assert 'target="_blank"' in html
        assert 'rel="noopener"' in html

    def test_no_cta_when_link_empty(self, client, blank_optional_event):
        """Empty link hides the register CTA."""
        response = client.get(_detail_url("evento-minimo"))
        html = response.content.decode()
        assert response.status_code == 200
        assert "Inscribirse" not in html


@pytest.mark.django_db
class TestEventDetailInboundLinks:
    """Home, list, and dashboard point cards at the public detail page."""

    def test_home_card_goes_to_detail(self, client, meetup_salta):
        """Home Registrarme goes to /eventos/<slug>/ without opening event.link."""
        response = client.get(reverse("home"))
        html = response.content.decode()
        assert response.status_code == 200
        assert "/eventos/meetup-salta/" in html
        assert 'href="https://example.com/register" target="_blank"' not in html

    def test_events_list_goes_to_detail(self, client, meetup_salta):
        """Hero keeps detail links; Inscribirse opens the registration URL when set."""
        response = client.get(reverse("events"))
        html = response.content.decode()
        assert response.status_code == 200
        assert reverse("events") == "/eventos/"
        assert html.count("/eventos/meetup-salta/") >= 2
        assert 'href="https://example.com/register" target="_blank"' in html
        assert "Ver detalle" in html

    def test_events_detail_urlizes_links_in_description(self, client, db):
        """URLs inside the event description become clickable anchors."""
        Event.objects.create(
            title="Meetup con link",
            description="Inscribite acá: https://luma.com/cursor-sh4i",
            location="Salta",
            link="https://luma.com/cursor-sh4i",
            slug="meetup-con-link",
            status=Event.Status.APPROVED,
            event_start_date=timezone.now() + timedelta(days=5),
            event_date_display="16 de Septiembre",
            event_time_display="18:00",
        )
        html = client.get(_detail_url("meetup-con-link")).content.decode()
        assert 'href="https://luma.com/cursor-sh4i"' in html
        assert "event-body" in html

    def test_events_hero_description_only_on_left(self, client, meetup_salta):
        """Full description stays on the left; the right card is photo + title only."""
        html = client.get(reverse("events")).content.decode()
        assert "event-hero-description" in html
        assert meetup_salta.description in html
        assert html.count("event-hero-description") == 1

    def test_dashboard_row_goes_to_detail(self, client, meetup_salta, member_user):
        """Dashboard upcoming row links to the public detail URL."""
        client.force_login(member_user)
        response = client.get(reverse("dashboard"))
        html = response.content.decode()
        assert response.status_code == 200
        assert "/eventos/meetup-salta/" in html
        assert 'href="https://example.com/register" target="_blank"' not in html


@pytest.mark.django_db
class TestDashboardUpcomingApprovedOnly:
    """Dashboard upcoming lists only approved future events."""

    def test_pending_future_event_absent(self, client, pending_event, member_user):
        """Pending future events do not appear in upcoming."""
        client.force_login(member_user)
        response = client.get(reverse("dashboard"))
        html = response.content.decode()
        assert response.status_code == 200
        assert pending_event.title not in html
        assert "/eventos/pendiente/" not in html

    def test_approved_future_event_listed_with_detail_href(
        self, client, meetup_salta, member_user
    ):
        """Approved future events appear with a public detail href."""
        client.force_login(member_user)
        response = client.get(reverse("dashboard"))
        html = response.content.decode()
        assert meetup_salta.title in html
        assert "/eventos/meetup-salta/" in html


@pytest.mark.django_db
class TestEventSitemap:
    """Sitemap lists approved detail URLs and valid static names."""

    def test_sitemap_includes_approved_detail_and_valid_names(
        self, client, meetup_salta, pending_event, rejected_event
    ):
        """Approved loc is present; pending/rejected omitted; static names resolve."""
        response = client.get("/sitemap.xml")
        xml = response.content.decode()
        loc_paths = _sitemap_loc_paths(xml)
        list_path = reverse("events")
        detail_path = reverse("event_detail", kwargs={"slug": meetup_salta.slug})
        benefits_path = reverse("benefits_list")
        assert response.status_code == 200
        assert loc_paths.count(list_path) == 1
        assert detail_path in loc_paths
        assert loc_paths.count(benefits_path) == 1
        assert reverse("event_detail", kwargs={"slug": pending_event.slug}) not in loc_paths
        assert reverse("event_detail", kwargs={"slug": rejected_event.slug}) not in loc_paths

    def test_sitemap_omits_rejected_when_only_rejected(self, client, rejected_event):
        """A rejected-only catalog does not publish that detail URL."""
        response = client.get("/sitemap.xml")
        xml = response.content.decode()
        loc_paths = _sitemap_loc_paths(xml)
        assert response.status_code == 200
        assert reverse("event_detail", kwargs={"slug": rejected_event.slug}) not in loc_paths
        assert loc_paths.count(reverse("events")) == 1
        assert loc_paths.count(reverse("benefits_list")) == 1

"""Tests for the public courses catalog and admin-managed resources."""

import pytest
from content.models import LearningResource
from django.urls import reverse
from home.resources import TRACKS, tracks_for_page
from users.models import User


@pytest.fixture
def published_resources(db):
    """Create one published resource per public track."""
    return (
        LearningResource.objects.create(
            title="Tutorial oficial de Python",
            tip="Empezá por el tutorial.",
            url="https://docs.python.org/es/3/tutorial/",
            source="docs.python.org",
            track=LearningResource.Track.DEVELOPERS,
            order=1,
        ),
        LearningResource.objects.create(
            title="Cursor: trabajo con el agente",
            tip="Reglas del repo primero.",
            url="https://cursor.com/docs",
            source="cursor.com",
            track=LearningResource.Track.VIBECODERS,
            order=1,
        ),
    )


@pytest.mark.django_db
def test_resources_page_returns_200(client) -> None:
    """The catalog should be a public page."""
    response = client.get(reverse("resources"))
    assert response.status_code == 200
    assert "home/resources.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_resources_page_empty_state_when_nothing_published(client) -> None:
    """Without published rows the catalog explains that admins load courses."""
    LearningResource.objects.all().delete()
    html = client.get(reverse("resources")).content.decode()
    assert "Todavía no hay cursos publicados" in html


@pytest.mark.django_db
def test_resources_page_shows_published_tracks(client, published_resources) -> None:
    """Developers and vibecoders sections appear when they have published items."""
    html = client.get(reverse("resources")).content.decode()
    assert "Developers" in html
    assert "Vibecoders" in html
    assert "Cursos y tips" in html
    for resource in published_resources:
        assert resource.title in html
        assert resource.url in html


@pytest.mark.django_db
def test_unpublished_resource_is_hidden(client, published_resources) -> None:
    """Drafts stay off the public page."""
    draft = LearningResource.objects.create(
        title="Borrador secreto",
        tip="No debería verse.",
        url="https://example.com/draft",
        track=LearningResource.Track.DEVELOPERS,
        is_published=False,
    )
    html = client.get(reverse("resources")).content.decode()
    assert draft.title not in html
    assert published_resources[0].title in html


def test_tracks_meta_covers_both_audiences() -> None:
    """Track slugs stay stable for anchors and admin choices."""
    assert {track.slug for track in TRACKS} == {"developers", "vibecoders"}


@pytest.mark.django_db
def test_tracks_for_page_skips_empty_tracks(published_resources) -> None:
    """A track without published items is omitted from the page."""
    LearningResource.objects.filter(track=LearningResource.Track.VIBECODERS).delete()
    tracks = tracks_for_page()
    assert [track.slug for track in tracks] == ["developers"]
    assert tracks[0].resources[0].title == published_resources[0].title


@pytest.mark.django_db
def test_home_cursos_pillar_links_to_resources(client) -> None:
    """The home Cursos card should stop being a dead sample."""
    html = client.get(reverse("home")).content.decode()
    assert reverse("resources") in html
    assert "Cursos" in html


@pytest.mark.django_db
def test_nav_includes_recursos(client) -> None:
    """Public nav should expose the catalog."""
    html = client.get(reverse("home")).content.decode()
    assert 'href="/recursos/"' in html


@pytest.mark.django_db
def test_sitemap_includes_resources(client) -> None:
    """Search engines should see the catalog."""
    xml = client.get("/sitemap.xml").content.decode()
    assert "/recursos/" in xml


@pytest.mark.django_db
def test_admin_changelist_allows_superuser(client, superuser) -> None:
    """Administrators manage courses from Django admin."""
    client.force_login(superuser)
    response = client.get(reverse("admin:content_learningresource_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_changelist_allows_administrador_staff(client, staff_user) -> None:
    """A staff administrator can load courses from Django admin."""
    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.save(update_fields=["role"])
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_learningresource_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_changelist_rejects_staff_member(client, staff_user) -> None:
    """A staff user without the administrator role cannot manage courses."""
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_learningresource_changelist"))
    assert response.status_code == 403

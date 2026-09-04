"""Tests for the public IT specialties catalog."""

import pytest
from content.models import TechSpecialty
from django.urls import reverse
from home.specialties import FAMILIES, specialties_for_page
from users.models import User

SEEDED_TITLES = (
    "Frontend web",
    "Backend",
    "Full stack",
    "Mobile iOS",
    "Mobile Android",
    "Mobile multiplataforma",
    "DevOps y cloud",
    "Ciencia de datos",
    "Machine learning e IA",
    "Ciberseguridad",
    "Videojuegos",
    "QA y testing",
    "Blockchain y Web3",
    "Diseño UI/UX",
    "Redes e infraestructura",
    "Soporte técnico",
    "Bases de datos",
    "Data engineering",
    "Product management",
    "Project management",
    "Tech lead",
    "Engineering management",
    "Arquitectura de software",
)


@pytest.fixture
def published_specialty(db):
    """Create a published specialty used by tests that ignore the seed."""
    return TechSpecialty.objects.create(
        slug="sre",
        title="Site reliability",
        summary="Mantiene sistemas en pie cuando el tráfico pega.",
        stack="Prometheus\nGrafana\nKubernetes",
        audience="Para quien prefiere guardias y métricas a features nuevas.",
        family=TechSpecialty.Family.OPERATIONS,
        icon="monitor_heart",
        order=90,
    )


@pytest.mark.django_db
def test_specialties_page_returns_200(client) -> None:
    """The specialties catalog should be a public page."""
    response = client.get(reverse("resource_specialties"))
    assert response.status_code == 200
    assert "home/specialties.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_specialties_page_lists_seeded_roles(client) -> None:
    """The first catalog should cover the main IT career paths."""
    html = client.get(reverse("resource_specialties")).content.decode()
    assert "Especialidades" in html
    assert "Construye la interfaz en el navegador" in html
    assert "Implementa la lógica del servidor" in html
    for title in SEEDED_TITLES:
        assert title in html


@pytest.mark.django_db
def test_unpublished_specialty_is_hidden(client, published_specialty) -> None:
    """Drafts stay off the public page."""
    draft = TechSpecialty.objects.create(
        slug="borrador",
        title="Rol secreto",
        summary="No debería verse.",
        family=TechSpecialty.Family.DEVELOPMENT,
        is_published=False,
    )
    html = client.get(reverse("resource_specialties")).content.decode()
    assert draft.title not in html
    assert published_specialty.title in html


@pytest.mark.django_db
def test_specialties_empty_state(client) -> None:
    """Without published rows the page tells visitors that admins load roles."""
    TechSpecialty.objects.all().delete()
    html = client.get(reverse("resource_specialties")).content.decode()
    assert "Todavía no hay especialidades publicadas" in html


@pytest.mark.django_db
def test_specialties_for_page_groups_by_family(published_specialty) -> None:
    """Empty families are omitted; published roles stay under their family."""
    TechSpecialty.objects.exclude(pk=published_specialty.pk).delete()
    families = specialties_for_page()
    assert [family.slug for family in families] == ["operations"]
    assert families[0].specialties[0].title == published_specialty.title


def test_families_cover_the_catalog() -> None:
    """Family slugs stay stable for anchors and admin choices."""
    assert {family.slug for family in FAMILIES} == {
        "development",
        "data",
        "operations",
        "design",
        "product",
        "leadership",
    }


@pytest.mark.django_db
def test_resources_hub_links_to_specialties(client) -> None:
    """Cursos and especialidades share a resources nav."""
    courses = client.get(reverse("resources")).content.decode()
    specialties = client.get(reverse("resource_specialties")).content.decode()
    assert reverse("resource_specialties") in courses
    assert reverse("resources") in specialties
    assert "Especialidades" in courses


@pytest.mark.django_db
def test_sitemap_includes_specialties(client) -> None:
    """Search engines should see the specialties catalog."""
    xml = client.get("/sitemap.xml").content.decode()
    assert "/recursos/especialidades/" in xml


@pytest.mark.django_db
def test_footer_links_to_specialties(client) -> None:
    """The footer should expose the roles catalog."""
    html = client.get(reverse("home")).content.decode()
    assert "/recursos/especialidades/" in html


@pytest.mark.django_db
def test_admin_changelist_allows_superuser(client, superuser) -> None:
    """Administrators manage specialties from Django admin."""
    client.force_login(superuser)
    response = client.get(reverse("admin:content_techspecialty_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_changelist_allows_administrador_staff(client, staff_user) -> None:
    """A staff administrator can load specialties."""
    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.save(update_fields=["role"])
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_techspecialty_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_changelist_rejects_staff_member(client, staff_user) -> None:
    """A staff user without the administrator role cannot manage specialties."""
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_techspecialty_changelist"))
    assert response.status_code == 403

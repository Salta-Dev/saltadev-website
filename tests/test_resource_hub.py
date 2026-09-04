"""Tests for the PCN-style public resources hub."""

import pytest
from content.models import CatalogEntry
from django.urls import reverse
from users.models import User

CONVERSATIONAL_LEFTOVERS = (
    "¿Para quién es ideal?",
    "Si te gusta",
    "Si te copa",
    "mesa chica",
    "frenos de mano",
    "sin misterio",
    "en mi máquina anda",
    "daily que no sea teatro",
    "Sumá una herramienta",
    "Sumá tu proyecto",
)


HUB_URLS = (
    ("resources", "/recursos/"),
    ("resource_reading", "/recursos/lectura/"),
    ("resource_specialties", "/recursos/especialidades/"),
    ("resource_tools", "/recursos/herramientas/"),
    ("resource_projects", "/recursos/proyectos/"),
)


@pytest.mark.django_db
@pytest.mark.parametrize(("name", "path"), HUB_URLS)
def test_hub_pages_return_200(client, name, path) -> None:
    """Every Recursos tab should be a public page."""
    response = client.get(reverse(name))
    assert response.status_code == 200
    html = client.get(reverse(name)).content.decode()
    assert path in client.get(reverse("resources")).content.decode()
    for leftover in CONVERSATIONAL_LEFTOVERS:
        assert leftover not in html


@pytest.mark.django_db
def test_specialties_render_structured_sections(client) -> None:
    """A specialty should read like a role sheet, not a one-liner."""
    html = client.get(reverse("resource_specialties")).content.decode()
    assert "Tecnologías principales" in html
    assert "A quién está orientado" in html
    assert "Responsabilidades" in html


@pytest.mark.django_db
def test_reading_page_lists_seeded_books(client) -> None:
    """Lectura should show curated books with author and topic."""
    html = client.get(reverse("resource_reading")).content.decode()
    assert "The Pragmatic Programmer" in html
    assert "Designing Data-Intensive Applications" in html
    assert "Arquitectura" in html
    assert "Libro sobre el oficio de programar" in html


@pytest.mark.django_db
def test_tools_page_lists_seeded_tools(client) -> None:
    """Herramientas should show category and pricing like a catalog."""
    html = client.get(reverse("resource_tools")).content.decode()
    assert "Visual Studio Code" in html
    assert "Cursor" in html
    assert "Editor de código de Microsoft" in html
    assert "Freemium" in html or "Gratis" in html
    assert "Proponer una herramienta" in html
    assert "Iniciar sesión para publicar" in html


@pytest.mark.django_db
def test_specialties_page_has_no_suggest_cta(client) -> None:
    """Specialties are curated; visitors should not be asked to propose roles."""
    html = client.get(reverse("resource_specialties")).content.decode()
    assert "Proponer una especialidad" not in html
    assert "¿Falta un rol?" not in html


@pytest.mark.django_db
def test_projects_page_starts_empty(client) -> None:
    """Seeded placeholder projects should not appear."""
    assert CatalogEntry.objects.filter(kind=CatalogEntry.Kind.PROJECT).count() == 0
    html = client.get(reverse("resource_projects")).content.decode()
    assert "Bot de Telegram" not in html
    assert "Proponer un proyecto" in html
    assert "Iniciar sesión para publicar" in html


@pytest.mark.django_db
def test_member_project_stays_pending_until_admin_approves(
    client, verified_user, staff_user
) -> None:
    """A member submission is hidden until an administrator approves it."""
    client.force_login(verified_user)
    response = client.post(
        reverse("resource_projects"),
        {
            "title": "Mi app",
            "summary": "Una app de la comunidad.",
            "url": "https://example.com/app",
            "stack": "Django\nHTMX",
        },
        follow=True,
    )
    assert response.status_code == 200
    project = CatalogEntry.objects.get(title="Mi app")
    assert project.kind == CatalogEntry.Kind.PROJECT
    assert project.status == CatalogEntry.Status.PENDING
    assert project.is_published is False
    assert "Mi app" not in client.get(reverse("resource_projects")).content.decode()

    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.save(update_fields=["role"])
    project.approve(staff_user)
    html = client.get(reverse("resource_projects")).content.decode()
    assert "Mi app" in html


@pytest.mark.django_db
def test_member_tool_stays_pending_until_admin_approves(
    client, verified_user, staff_user
) -> None:
    """A member tool submission is hidden until an administrator approves it."""
    client.force_login(verified_user)
    response = client.post(
        reverse("resource_tools"),
        {
            "title": "Helix",
            "summary": "Editor modal en la terminal.",
            "url": "https://helix-editor.com/",
            "category": "Desarrollo",
            "pricing": "Gratis",
            "tags": "Editor\nTerminal",
        },
        follow=True,
    )
    assert response.status_code == 200
    tool = CatalogEntry.objects.get(title="Helix")
    assert tool.kind == CatalogEntry.Kind.TOOL
    assert tool.status == CatalogEntry.Status.PENDING
    assert tool.is_published is False
    assert "Helix" not in client.get(reverse("resource_tools")).content.decode()

    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.save(update_fields=["role"])
    tool.approve(staff_user)
    html = client.get(reverse("resource_tools")).content.decode()
    assert "Helix" in html


@pytest.mark.django_db
def test_anonymous_tool_post_redirects_to_login(client) -> None:
    """Publishing a tool requires a session."""
    response = client.post(
        reverse("resource_tools"),
        {
            "title": "Tool anónima",
            "summary": "No debería crearse.",
            "url": "https://example.com/no",
        },
    )
    assert response.status_code == 302
    assert reverse("login") in response.url
    assert CatalogEntry.objects.filter(title="Tool anónima").exists() is False


@pytest.mark.django_db
def test_anonymous_project_post_redirects_to_login(client) -> None:
    """Publishing a project requires a session."""
    response = client.post(
        reverse("resource_projects"),
        {
            "title": "App anónima",
            "summary": "No debería crearse.",
            "url": "https://example.com/no",
        },
    )
    assert response.status_code == 302
    assert reverse("login") in response.url
    assert CatalogEntry.objects.filter(title="App anónima").exists() is False


@pytest.mark.django_db
def test_unpublished_catalog_entry_is_hidden(client) -> None:
    """Draft catalog rows stay off the public hub."""
    draft = CatalogEntry.objects.create(
        kind=CatalogEntry.Kind.READING,
        title="Libro secreto",
        summary="No debería verse.",
        is_published=False,
    )
    html = client.get(reverse("resource_reading")).content.decode()
    assert draft.title not in html


@pytest.mark.django_db
def test_sitemap_includes_hub_tabs(client) -> None:
    """Search engines should see every Recursos tab."""
    xml = client.get("/sitemap.xml").content.decode()
    for _name, path in HUB_URLS:
        assert path in xml


@pytest.mark.django_db
def test_admin_catalog_allows_administrador(client, staff_user) -> None:
    """Administrators load books, tools and projects from Django admin."""
    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.save(update_fields=["role"])
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_catalogentry_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_catalog_rejects_staff_member(client, staff_user) -> None:
    """A staff member cannot manage the catalog."""
    client.force_login(staff_user)
    response = client.get(reverse("admin:content_catalogentry_changelist"))
    assert response.status_code == 403

"""Tests for Recursos community proposals and on-site review."""

from __future__ import annotations

import pytest
from content.models import CatalogEntry, LearningResource
from django.urls import reverse
from notifications.models import Notification
from users.models import User


@pytest.mark.django_db
def test_reading_page_has_propose_form(client) -> None:
    """Lectura should accept community book proposals."""
    html = client.get(reverse("resource_reading")).content.decode()
    assert "Proponer un libro" in html
    assert "Iniciar sesión para publicar" in html


@pytest.mark.django_db
def test_courses_page_has_propose_form(client) -> None:
    """Cursos should accept community course proposals."""
    html = client.get(reverse("resources")).content.decode()
    assert "Proponer un curso" in html
    assert "Enviar a revisión" in html or "Iniciar sesión para publicar" in html
    assert "Proponer un recurso" not in html


@pytest.mark.django_db
def test_unverified_member_cannot_submit_tool(client, unverified_user) -> None:
    """Verified email is required to submit proposals."""
    client.force_login(unverified_user)
    response = client.post(
        reverse("resource_tools"),
        {
            "title": "Tool sin verificar",
            "summary": "No debería crearse.",
            "url": "https://example.com/unverified",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert CatalogEntry.objects.filter(title="Tool sin verificar").exists() is False
    assert b"Confirm" in response.content or b"email" in response.content.lower()


@pytest.mark.django_db
def test_member_book_stays_pending_until_reviewer_approves(
    client, verified_user, staff_user
) -> None:
    """A member book is hidden until a Revisor publishes it on the site."""
    client.force_login(verified_user)
    client.post(
        reverse("resource_reading"),
        {
            "title": "Libro Propuesta Unica",
            "summary": "Oficio del código limpio.",
            "url": "https://example.com/clean-code-unique",
            "authors": "Robert C. Martin",
        },
        follow=True,
    )
    book = CatalogEntry.objects.filter(
        title="Libro Propuesta Unica",
        url="https://example.com/clean-code-unique",
        creator=verified_user,
    ).latest("pk")
    assert book.kind == CatalogEntry.Kind.READING
    assert book.status == CatalogEntry.Status.PENDING
    assert book.title not in client.get(reverse("resource_reading")).content.decode()

    staff_user.role = User.Role.MODERADOR
    staff_user.is_staff = True
    staff_user.save(update_fields=["role", "is_staff"])
    client.force_login(staff_user)
    response = client.post(
        reverse("catalog_proposal_approve", kwargs={"pk": book.pk}),
        follow=True,
    )
    assert response.status_code == 200
    book.refresh_from_db()
    assert book.status == CatalogEntry.Status.APPROVED
    assert (
        "Libro Propuesta Unica"
        in client.get(reverse("resource_reading")).content.decode()
    )
    assert Notification.objects.filter(
        recipient=verified_user, verb="Propuesta publicada"
    ).exists()


@pytest.mark.django_db
def test_member_course_pending_and_reject_with_reason(
    client, verified_user, staff_user
) -> None:
    """Courses use the same proposal lifecycle with optional reject reason."""
    client.force_login(verified_user)
    client.post(
        reverse("resources"),
        {
            "title": "Curso de HTMX",
            "tip": "Interactividad sin SPA.",
            "url": "https://example.com/htmx-course",
            "track": LearningResource.Track.DEVELOPERS,
        },
        follow=True,
    )
    course = LearningResource.objects.get(title="Curso de HTMX")
    assert course.status == LearningResource.Status.PENDING
    assert course.is_published is False

    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.is_staff = True
    staff_user.save(update_fields=["role", "is_staff"])
    client.force_login(staff_user)
    client.post(
        reverse("course_proposal_reject", kwargs={"pk": course.pk}),
        {"rejection_reason": "Falta nivel"},
        follow=True,
    )
    course.refresh_from_db()
    assert course.status == LearningResource.Status.REJECTED
    assert course.rejection_reason == "Falta nivel"
    assert Notification.objects.filter(
        recipient=verified_user, verb="Propuesta rechazada"
    ).exists()

    client.force_login(verified_user)
    mine = client.get(reverse("my_resource_proposals")).content.decode()
    assert "Curso de HTMX" in mine
    assert "Falta nivel" in mine


@pytest.mark.django_db
def test_duplicate_url_blocked_across_kinds(client, verified_user) -> None:
    """The same canonical URL cannot be proposed twice while pending/approved."""
    CatalogEntry.objects.create(
        kind=CatalogEntry.Kind.TOOL,
        title="Existente",
        summary="Ya está.",
        url="https://example.com/tool/",
        status=CatalogEntry.Status.APPROVED,
        is_published=True,
    )
    client.force_login(verified_user)
    response = client.post(
        reverse("resource_projects"),
        {
            "title": "Copia",
            "summary": "Mismo link.",
            "url": "https://example.com/tool",
        },
    )
    assert response.status_code == 200
    assert CatalogEntry.objects.filter(title="Copia").exists() is False
    assert "Ya hay un recurso con ese enlace" in response.content.decode()


@pytest.mark.django_db
def test_reviewer_submission_publishes_immediately(client, staff_user) -> None:
    """Revisores skip the queue when they submit."""
    staff_user.role = User.Role.ADMINISTRADOR
    staff_user.is_staff = True
    staff_user.email_confirmed = True
    staff_user.save(update_fields=["role", "is_staff", "email_confirmed"])
    client.force_login(staff_user)
    client.post(
        reverse("resource_tools"),
        {
            "title": "Admin Tool",
            "summary": "Publicada al toque.",
            "url": "https://example.com/admin-tool",
        },
        follow=True,
    )
    tool = CatalogEntry.objects.get(title="Admin Tool")
    assert tool.status == CatalogEntry.Status.APPROVED
    assert tool.is_published is True
    assert "Admin Tool" in client.get(reverse("resource_tools")).content.decode()


@pytest.mark.django_db
def test_pending_queue_requires_reviewer(client, verified_user) -> None:
    """Members cannot open the review queue."""
    client.force_login(verified_user)
    response = client.get(reverse("pending_resource_proposals"))
    assert response.status_code == 302

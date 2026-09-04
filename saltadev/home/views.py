"""Public home and Recursos hub views."""

from __future__ import annotations

from content.models import (
    CatalogEntry,
    Collaborator,
    Event,
    LearningResource,
    StaffProfile,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from users.models import User

from home.catalog import (
    approve_catalog_entry,
    approve_course,
    can_review_recursos,
    can_submit_propuestas,
    entries_for_kind,
    hub_url_is_taken,
    pending_proposals,
    proposals_for_member,
    reject_catalog_entry,
    reject_course,
    submit_catalog_entry,
    submit_course,
)
from home.forms import CourseForm, ProjectForm, ReadingForm, ToolForm
from home.resources import tracks_for_page
from home.specialties import specialties_for_page


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    """Render the homepage with latest events, staff members, and collaborators."""
    latest_events = cache.get("home_latest_events")
    if latest_events is None:
        latest_events = list(
            Event.objects.filter(status=Event.Status.APPROVED)
            .select_related("creator")
            .order_by("-event_start_date")[:3]
        )
        cache.set("home_latest_events", latest_events, 60)

    staff_members = cache.get("home_staff_members")
    if staff_members is None:
        staff_members = list(
            StaffProfile.objects.select_related("user").order_by("order", "created_at")[
                :6
            ]
        )
        cache.set("home_staff_members", staff_members, 60)

    collaborators = cache.get("home_collaborators")
    if collaborators is None:
        collaborators = list(Collaborator.objects.order_by("created_at"))
        cache.set("home_collaborators", collaborators, 60)

    collaborators_count = len(collaborators)
    return render(
        request,
        "home/index.html",
        {
            "latest_events": latest_events,
            "staff_members": staff_members,
            "collaborators": collaborators,
            "collaborators_count": collaborators_count,
        },
    )


def _get_user(request: HttpRequest) -> User:
    """Return the authenticated User for typed view helpers."""
    user_id = request.user.pk
    assert user_id is not None
    return User.objects.get(pk=user_id)


def _submit_catalog(
    request: HttpRequest,
    form_class: type[ModelForm],
    kind: str,
    redirect_name: str,
    pending_message: str,
    published_message: str,
) -> HttpResponse | ModelForm:
    """Handle POST for a community catalog submission, or return an unbound form."""
    if request.method != "POST":
        return form_class()
    if not request.user.is_authenticated:
        login_url = reverse("login")
        next_url = reverse(redirect_name)
        return redirect(f"{login_url}?next={next_url}")
    user = _get_user(request)
    if not can_submit_propuestas(user) and not can_review_recursos(user):
        messages.error(
            request,
            "Confirmá tu email antes de proponer recursos.",
        )
        return redirect(redirect_name)
    form = form_class(request.POST)
    if form.is_valid():
        url = str(form.cleaned_data.get("url") or "")
        if hub_url_is_taken(url):
            form.add_error(
                "url",
                "Ya hay un recurso con ese enlace (publicado o en revisión).",
            )
            return form
        entry = submit_catalog_entry(form, user, kind)
        if entry.is_pending:
            messages.success(request, pending_message)
        else:
            messages.success(request, published_message)
        return redirect(redirect_name)
    return form


def _submit_course(
    request: HttpRequest,
) -> HttpResponse | ModelForm:
    """Handle POST for a community course submission, or return an unbound form."""
    if request.method != "POST":
        return CourseForm()
    if not request.user.is_authenticated:
        login_url = reverse("login")
        next_url = reverse("resources")
        return redirect(f"{login_url}?next={next_url}")
    user = _get_user(request)
    if not can_submit_propuestas(user) and not can_review_recursos(user):
        messages.error(
            request,
            "Confirmá tu email antes de proponer recursos.",
        )
        return redirect("resources")
    form = CourseForm(request.POST)
    if form.is_valid():
        url = str(form.cleaned_data.get("url") or "")
        if hub_url_is_taken(url):
            form.add_error(
                "url",
                "Ya hay un recurso con ese enlace (publicado o en revisión).",
            )
            return form
        course = submit_course(form, user)
        if course.is_pending:
            messages.success(
                request,
                "Curso enviado. Un revisor lo publica antes de mostrarlo.",
            )
        else:
            messages.success(request, "Curso publicado.")
        return redirect("resources")
    return form


@require_http_methods(["GET", "POST"])
def resources(request: HttpRequest) -> HttpResponse:
    """Render curated courses and accept community course proposals."""
    result = _submit_course(request)
    if isinstance(result, HttpResponse):
        return result
    return render(
        request,
        "home/resources.html",
        {
            "tracks": tracks_for_page(),
            "resources_section": "cursos",
            "submit_form": result,
            "submit_heading": "Proponer un curso",
            "submit_blurb": "Un revisor publica el envío antes de mostrarlo en Cursos.",
            "submit_login_name": "resources",
        },
    )


@require_GET
def resource_specialties(request: HttpRequest) -> HttpResponse:
    """Render the public catalog of IT roles and specialties."""
    return render(
        request,
        "home/specialties.html",
        {
            "families": specialties_for_page(),
            "resources_section": "especialidades",
        },
    )


@require_http_methods(["GET", "POST"])
def resource_reading(request: HttpRequest) -> HttpResponse:
    """Render the reading list and accept book proposals."""
    result = _submit_catalog(
        request,
        ReadingForm,
        CatalogEntry.Kind.READING,
        "resource_reading",
        "Libro enviado. Un revisor lo publica antes de mostrarlo.",
        "Libro publicado.",
    )
    if isinstance(result, HttpResponse):
        return result
    return render(
        request,
        "home/catalog.html",
        {
            "resources_section": "lectura",
            "catalog_title": "Lectura",
            "catalog_kicker": "Bibliografía",
            "catalog_blurb": "Libros de programación, arquitectura, gestión y producto.",
            "catalog_cta": "Ver libro",
            "catalog_meta": "Libros de programación, arquitectura, gestión y producto seleccionados por SaltaDev.",
            "entries": entries_for_kind(CatalogEntry.Kind.READING),
            "submit_form": result,
            "submit_heading": "Proponer un libro",
            "submit_blurb": "Un revisor publica el envío antes de mostrarlo en Lectura.",
            "submit_login_name": "resource_reading",
        },
    )


@require_http_methods(["GET", "POST"])
def resource_tools(request: HttpRequest) -> HttpResponse:
    """Render the tools catalog and accept submissions for review."""
    result = _submit_catalog(
        request,
        ToolForm,
        CatalogEntry.Kind.TOOL,
        "resource_tools",
        "Herramienta enviada. Un revisor la publica antes de mostrarla.",
        "Herramienta publicada.",
    )
    if isinstance(result, HttpResponse):
        return result
    return render(
        request,
        "home/catalog.html",
        {
            "resources_section": "herramientas",
            "catalog_title": "Herramientas",
            "catalog_kicker": "Catálogo",
            "catalog_blurb": "Editores, infraestructura, diseño e IA. La comunidad puede proponer; un revisor publica.",
            "catalog_cta": "Abrir herramienta",
            "catalog_meta": "Herramientas de SaltaDev: editores, infraestructura, diseño e IA.",
            "entries": entries_for_kind(CatalogEntry.Kind.TOOL),
            "submit_form": result,
            "submit_heading": "Proponer una herramienta",
            "submit_blurb": "Un revisor publica el envío antes de mostrarlo.",
            "submit_login_name": "resource_tools",
        },
    )


@require_http_methods(["GET", "POST"])
def resource_projects(request: HttpRequest) -> HttpResponse:
    """Render community projects and accept submissions for review."""
    result = _submit_catalog(
        request,
        ProjectForm,
        CatalogEntry.Kind.PROJECT,
        "resource_projects",
        "Proyecto enviado. Un revisor lo publica antes de mostrarlo.",
        "Proyecto publicado.",
    )
    if isinstance(result, HttpResponse):
        return result
    return render(
        request,
        "home/catalog.html",
        {
            "resources_section": "proyectos",
            "catalog_title": "Proyectos",
            "catalog_kicker": "Comunidad",
            "catalog_blurb": "Proyectos construidos por integrantes de SaltaDev. Se pueden proponer; un revisor publica.",
            "catalog_cta": "Visitar proyecto",
            "catalog_meta": "Proyectos construidos por la comunidad SaltaDev.",
            "entries": entries_for_kind(CatalogEntry.Kind.PROJECT),
            "submit_form": result,
            "submit_heading": "Proponer un proyecto",
            "submit_blurb": "Un revisor publica el envío antes de mostrarlo.",
            "submit_login_name": "resource_projects",
        },
    )


@login_required
@require_GET
def my_resource_proposals(request: HttpRequest) -> HttpResponse:
    """List the member's own Recursos proposals with status."""
    user = _get_user(request)
    return render(
        request,
        "home/my_proposals.html",
        {
            "proposals": proposals_for_member(user),
            "can_review": can_review_recursos(user),
        },
    )


@login_required
@require_GET
def pending_resource_proposals(request: HttpRequest) -> HttpResponse:
    """Review queue for pending Recursos proposals."""
    user = _get_user(request)
    if not can_review_recursos(user):
        messages.error(request, "No tenés permisos para revisar propuestas.")
        return redirect("resources")
    return render(
        request,
        "home/pending_proposals.html",
        {"proposals": pending_proposals()},
    )


@login_required
@require_http_methods(["GET", "POST"])
def catalog_proposal_approve(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve a pending catalog proposal."""
    user = _get_user(request)
    if not can_review_recursos(user):
        messages.error(request, "No tenés permisos para aprobar propuestas.")
        return redirect("resources")
    entry = get_object_or_404(CatalogEntry, pk=pk, status=CatalogEntry.Status.PENDING)
    if request.method == "POST":
        approve_catalog_entry(entry, user)
        messages.success(request, f"«{entry.title}» publicado.")
        return redirect("pending_resource_proposals")
    return render(
        request,
        "home/proposal_approve_confirm.html",
        {"proposal_title": entry.title, "action_url": request.path},
    )


@login_required
@require_http_methods(["GET", "POST"])
def catalog_proposal_reject(request: HttpRequest, pk: int) -> HttpResponse:
    """Reject a pending catalog proposal with an optional reason."""
    user = _get_user(request)
    if not can_review_recursos(user):
        messages.error(request, "No tenés permisos para rechazar propuestas.")
        return redirect("resources")
    entry = get_object_or_404(CatalogEntry, pk=pk, status=CatalogEntry.Status.PENDING)
    if request.method == "POST":
        reason = (request.POST.get("rejection_reason") or "").strip()
        reject_catalog_entry(entry, user, reason=reason)
        messages.success(request, f"«{entry.title}» rechazado.")
        return redirect("pending_resource_proposals")
    return render(
        request,
        "home/proposal_reject_confirm.html",
        {"proposal_title": entry.title, "action_url": request.path},
    )


@login_required
@require_http_methods(["GET", "POST"])
def course_proposal_approve(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve a pending course proposal."""
    user = _get_user(request)
    if not can_review_recursos(user):
        messages.error(request, "No tenés permisos para aprobar propuestas.")
        return redirect("resources")
    course = get_object_or_404(
        LearningResource, pk=pk, status=LearningResource.Status.PENDING
    )
    if request.method == "POST":
        approve_course(course, user)
        messages.success(request, f"«{course.title}» publicado.")
        return redirect("pending_resource_proposals")
    return render(
        request,
        "home/proposal_approve_confirm.html",
        {"proposal_title": course.title, "action_url": request.path},
    )


@login_required
@require_http_methods(["GET", "POST"])
def course_proposal_reject(request: HttpRequest, pk: int) -> HttpResponse:
    """Reject a pending course proposal with an optional reason."""
    user = _get_user(request)
    if not can_review_recursos(user):
        messages.error(request, "No tenés permisos para rechazar propuestas.")
        return redirect("resources")
    course = get_object_or_404(
        LearningResource, pk=pk, status=LearningResource.Status.PENDING
    )
    if request.method == "POST":
        reason = (request.POST.get("rejection_reason") or "").strip()
        reject_course(course, user, reason=reason)
        messages.success(request, f"«{course.title}» rechazado.")
        return redirect("pending_resource_proposals")
    return render(
        request,
        "home/proposal_reject_confirm.html",
        {"proposal_title": course.title, "action_url": request.path},
    )

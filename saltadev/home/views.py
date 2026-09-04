from content.models import CatalogEntry, Collaborator, Event, StaffProfile
from django.contrib import messages
from django.core.cache import cache
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from users.models import User

from home.catalog import entries_for_kind, submit_catalog_entry
from home.forms import ProjectForm, ToolForm
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


@require_GET
def resources(request: HttpRequest) -> HttpResponse:
    """Render curated courses and tips for developers and vibecoders."""
    return render(
        request,
        "home/resources.html",
        {
            "tracks": tracks_for_page(),
            "resources_section": "cursos",
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


@require_GET
def resource_reading(request: HttpRequest) -> HttpResponse:
    """Render the curated reading list."""
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
        },
    )


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
    form = form_class(request.POST)
    if form.is_valid():
        submitter = User.objects.get(pk=request.user.pk)
        entry = submit_catalog_entry(form, submitter, kind)
        if entry.is_pending:
            messages.success(request, pending_message)
        else:
            messages.success(request, published_message)
        return redirect(redirect_name)
    return form


@require_http_methods(["GET", "POST"])
def resource_tools(request: HttpRequest) -> HttpResponse:
    """Render the tools catalog and accept submissions for admin review."""
    result = _submit_catalog(
        request,
        ToolForm,
        CatalogEntry.Kind.TOOL,
        "resource_tools",
        "Herramienta enviada. Un administrador la revisa antes de publicarla.",
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
            "catalog_blurb": "Editores, infraestructura, diseño e IA. La comunidad puede proponer; un administrador publica.",
            "catalog_cta": "Abrir herramienta",
            "catalog_meta": "Herramientas de SaltaDev: editores, infraestructura, diseño e IA.",
            "entries": entries_for_kind(CatalogEntry.Kind.TOOL),
            "submit_form": result,
            "submit_heading": "Proponer una herramienta",
            "submit_blurb": "Un administrador revisa el envío antes de publicarlo.",
            "submit_login_name": "resource_tools",
        },
    )


@require_http_methods(["GET", "POST"])
def resource_projects(request: HttpRequest) -> HttpResponse:
    """Render community projects and accept submissions for admin review."""
    result = _submit_catalog(
        request,
        ProjectForm,
        CatalogEntry.Kind.PROJECT,
        "resource_projects",
        "Proyecto enviado. Un administrador lo revisa antes de publicarlo.",
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
            "catalog_blurb": "Proyectos construidos por integrantes de SaltaDev. Se pueden proponer; un administrador publica.",
            "catalog_cta": "Visitar proyecto",
            "catalog_meta": "Proyectos construidos por la comunidad SaltaDev.",
            "entries": entries_for_kind(CatalogEntry.Kind.PROJECT),
            "submit_form": result,
            "submit_heading": "Proponer un proyecto",
            "submit_blurb": "Un administrador revisa el envío antes de publicarlo.",
            "submit_login_name": "resource_projects",
        },
    )

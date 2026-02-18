from typing import TYPE_CHECKING

from content.models import Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from users.image_service import upload_event_image

from .forms import EventForm, ImageSourceChoices

if TYPE_CHECKING:
    from users.models import User


def _get_user(request: HttpRequest) -> "User":
    """Get the authenticated user from request with proper typing."""
    from users.models import User

    pk: int = request.user.pk  # type: ignore[assignment]
    return User.objects.get(pk=pk)


def can_manage_events(user: "User") -> bool:
    """Check if user can create/manage events."""
    if user.is_superuser:
        return True
    return user.role in ["administrador", "moderador", "colaborador"]


def can_approve_events(user: "User") -> bool:
    """Check if user can approve/reject events."""
    if user.is_superuser:
        return True
    return user.role in ["administrador", "moderador"]


def events_list(request: HttpRequest) -> HttpResponse:
    """Render the events page with all approved events sorted by date."""
    events = (
        Event.objects.filter(status=Event.Status.APPROVED)
        .select_related("creator")
        .order_by("-event_start_date")
    )
    latest_event = events.first()
    return render(
        request, "events/index.html", {"events": events, "latest_event": latest_event}
    )


@login_required
def my_events(request: HttpRequest) -> HttpResponse:
    """Display events created by the current user."""
    user = _get_user(request)
    if not can_manage_events(user):
        messages.error(request, "No tenés permisos para acceder a esta sección.")
        return redirect("events")

    events = Event.objects.filter(creator=user).order_by("-created_at")

    return render(
        request,
        "events/my_events.html",
        {
            "events": events,
            "can_approve": can_approve_events(user),
        },
    )


@login_required
def pending_events(request: HttpRequest) -> HttpResponse:
    """Display events pending approval (admin/moderator only)."""
    user = _get_user(request)
    if not can_approve_events(user):
        messages.error(request, "No tenés permisos para acceder a esta sección.")
        return redirect("events")

    events = Event.objects.filter(status=Event.Status.PENDING).order_by("-created_at")

    return render(
        request,
        "events/pending.html",
        {"events": events},
    )


@login_required
def event_create(request: HttpRequest) -> HttpResponse:
    """Create a new event."""
    user = _get_user(request)
    if not can_manage_events(user):
        messages.error(request, "No tenés permisos para crear eventos.")
        return redirect("events")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = user

            # Determine status based on user role
            if can_approve_events(user):
                event.status = Event.Status.APPROVED
                event.approved_by = user
                event.approved_at = timezone.now()
            else:
                event.status = Event.Status.PENDING

            # Handle image upload if file was provided
            image_source = form.cleaned_data.get("image_source")
            image_file = form.cleaned_data.get("image_file")

            if image_source == ImageSourceChoices.FILE and image_file:
                result = upload_event_image(image_file)
                if result.success and result.url:
                    event.photo = result.url
                else:
                    messages.warning(
                        request,
                        f"No se pudo subir la imagen: {result.error}. "
                        "El evento se creó sin imagen.",
                    )

            event.save()

            if event.status == Event.Status.PENDING:
                messages.success(
                    request,
                    "Evento creado. Está pendiente de aprobación por un moderador.",
                )
            else:
                messages.success(request, "Evento creado exitosamente.")

            return redirect("my_events")
    else:
        form = EventForm()

    return render(
        request,
        "events/form.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def event_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit an existing event."""
    event = get_object_or_404(Event, pk=pk)
    user = _get_user(request)

    if not event.can_edit(user):
        messages.error(request, "No tenés permisos para editar este evento.")
        return redirect("my_events")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated_event = form.save(commit=False)

            # Handle image upload if file was provided
            image_source = form.cleaned_data.get("image_source")
            image_file = form.cleaned_data.get("image_file")

            if image_source == ImageSourceChoices.FILE and image_file:
                result = upload_event_image(image_file)
                if result.success and result.url:
                    updated_event.photo = result.url
                else:
                    messages.warning(
                        request,
                        f"No se pudo subir la imagen: {result.error}. "
                        "Se mantuvo la imagen anterior.",
                    )

            updated_event.save()
            messages.success(request, "Evento actualizado exitosamente.")
            return redirect("my_events")
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "events/form.html",
        {
            "form": form,
            "event": event,
            "is_edit": True,
        },
    )


@login_required
def event_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete an event."""
    event = get_object_or_404(Event, pk=pk)
    user = _get_user(request)

    if not event.can_edit(user):
        messages.error(request, "No tenés permisos para eliminar este evento.")
        return redirect("my_events")

    if request.method == "POST":
        event.delete()
        messages.success(request, "Evento eliminado exitosamente.")
        return redirect("my_events")

    return render(
        request,
        "events/delete_confirm.html",
        {"event": event},
    )


@login_required
def event_approve(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve a pending event."""
    event = get_object_or_404(Event, pk=pk)
    user = _get_user(request)

    if not event.can_approve(user):
        messages.error(request, "No tenés permisos para aprobar eventos.")
        return redirect("events")

    if request.method == "POST":
        event.status = Event.Status.APPROVED
        event.approved_by = user
        event.approved_at = timezone.now()
        event.save()
        messages.success(request, f"Evento '{event.title}' aprobado exitosamente.")
        return redirect("pending_events")

    return render(
        request,
        "events/approve_confirm.html",
        {"event": event},
    )


@login_required
def event_reject(request: HttpRequest, pk: int) -> HttpResponse:
    """Reject a pending event."""
    event = get_object_or_404(Event, pk=pk)
    user = _get_user(request)

    if not event.can_approve(user):
        messages.error(request, "No tenés permisos para rechazar eventos.")
        return redirect("events")

    if request.method == "POST":
        event.status = Event.Status.REJECTED
        event.save()
        messages.success(request, f"Evento '{event.title}' rechazado.")
        return redirect("pending_events")

    return render(
        request,
        "events/reject_confirm.html",
        {"event": event},
    )

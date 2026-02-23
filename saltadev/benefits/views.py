"""Views for the benefits app."""

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from users.image_service import upload_benefit_image

from .forms import BenefitForm, ImageSourceChoices
from .models import Benefit

if TYPE_CHECKING:
    from users.models import User


def can_manage_benefits(user: "User") -> bool:
    """Check if user can create/manage benefits."""
    if user.is_superuser:
        return True
    return user.role in ["administrador", "moderador", "colaborador"]


def _get_user(request: HttpRequest) -> "User":
    """Get the authenticated user from request with proper typing."""
    from users.models import User

    # request.user.pk is guaranteed to be int after @login_required
    pk: int = request.user.pk  # type: ignore[assignment]
    return User.objects.get(pk=pk)


@login_required
@require_GET
def benefits_list(request: HttpRequest) -> HttpResponse:
    """Display list of all active benefits."""
    user = _get_user(request)
    benefits = Benefit.objects.filter(is_active=True).select_related(
        "creator", "creator__profile"
    )

    # Filter by type if specified
    benefit_type = request.GET.get("type")
    if benefit_type in ["redeemable", "discount"]:
        benefits = benefits.filter(benefit_type=benefit_type)

    # Filter by modality if specified
    modality = request.GET.get("modality")
    if modality in ["virtual", "in_person", "both"]:
        benefits = benefits.filter(modality=modality)

    # Search by title or description
    search = request.GET.get("search", "").strip()
    if search:
        benefits = benefits.filter(title__icontains=search) | benefits.filter(
            description__icontains=search
        )

    # Pagination
    paginator = Paginator(benefits, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "benefits": page_obj,
        "can_create": can_manage_benefits(user),
        "current_type": benefit_type,
        "current_modality": modality,
        "search_query": search,
    }
    return render(request, "benefits/list.html", context)


@login_required
@require_GET
def benefits_my_list(request: HttpRequest) -> HttpResponse:
    """Display list of benefits created by the current user."""
    user = _get_user(request)
    if not can_manage_benefits(user):
        messages.error(request, "No tenés permisos para acceder a esta sección.")
        return redirect("benefits_list")

    benefits = Benefit.objects.filter(creator=user).select_related("creator")

    # Pagination
    paginator = Paginator(benefits, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "benefits": page_obj,
        "is_my_benefits": True,
    }
    return render(request, "benefits/my_list.html", context)


@login_required
@require_GET
def benefit_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Display detail of a single benefit."""
    benefit = get_object_or_404(
        Benefit.objects.select_related("creator", "creator__profile"),
        pk=pk,
    )

    user = _get_user(request)
    context = {
        "benefit": benefit,
        "can_edit": benefit.can_edit(user),
        "can_delete": benefit.can_delete(user),
    }
    return render(request, "benefits/detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def benefit_create(request: HttpRequest) -> HttpResponse:
    """Create a new benefit."""
    user = _get_user(request)
    if not can_manage_benefits(user):
        messages.error(request, "No tenés permisos para crear beneficios.")
        return redirect("benefits_list")

    if request.method == "POST":
        form = BenefitForm(request.POST, request.FILES)
        if form.is_valid():
            benefit = form.save(commit=False)
            benefit.creator = user

            # Handle image upload if file was provided
            image_source = form.cleaned_data.get("image_source")
            image_file = form.cleaned_data.get("image_file")

            if image_source == ImageSourceChoices.FILE and image_file:
                result = upload_benefit_image(image_file)
                if result.success and result.url:
                    benefit.image = result.url
                else:
                    messages.warning(
                        request,
                        f"No se pudo subir la imagen: {result.error}. "
                        "El beneficio se creó sin imagen.",
                    )

            benefit.save()
            messages.success(request, "Beneficio creado exitosamente.")
            return redirect("benefit_detail", pk=benefit.pk)
    else:
        form = BenefitForm()

    context = {
        "form": form,
        "is_edit": False,
    }
    return render(request, "benefits/form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def benefit_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit an existing benefit."""
    benefit = get_object_or_404(Benefit, pk=pk)
    user = _get_user(request)

    if not benefit.can_edit(user):
        messages.error(request, "No tenés permisos para editar este beneficio.")
        return redirect("benefit_detail", pk=pk)

    if request.method == "POST":
        form = BenefitForm(request.POST, request.FILES, instance=benefit)
        if form.is_valid():
            updated_benefit = form.save(commit=False)

            # Handle image upload if file was provided
            image_source = form.cleaned_data.get("image_source")
            image_file = form.cleaned_data.get("image_file")

            if image_source == ImageSourceChoices.FILE and image_file:
                result = upload_benefit_image(image_file)
                if result.success and result.url:
                    updated_benefit.image = result.url
                else:
                    messages.warning(
                        request,
                        f"No se pudo subir la imagen: {result.error}. "
                        "Se mantuvo la imagen anterior.",
                    )

            updated_benefit.save()
            messages.success(request, "Beneficio actualizado exitosamente.")
            return redirect("benefit_detail", pk=benefit.pk)
    else:
        form = BenefitForm(instance=benefit)

    context = {
        "form": form,
        "benefit": benefit,
        "is_edit": True,
    }
    return render(request, "benefits/form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def benefit_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a benefit."""
    benefit = get_object_or_404(Benefit, pk=pk)
    user = _get_user(request)

    if not benefit.can_delete(user):
        messages.error(request, "No tenés permisos para eliminar este beneficio.")
        return redirect("benefit_detail", pk=pk)

    if request.method == "POST":
        benefit.delete()
        messages.success(request, "Beneficio eliminado exitosamente.")
        return redirect("benefits_list")

    context = {
        "benefit": benefit,
    }
    return render(request, "benefits/delete_confirm.html", context)


@login_required
@require_POST
def benefit_toggle_active(request: HttpRequest, pk: int) -> HttpResponse:
    """Toggle the active status of a benefit."""
    benefit = get_object_or_404(Benefit, pk=pk)
    user = _get_user(request)

    if not benefit.can_edit(user):
        return HttpResponseForbidden("No tenés permisos para modificar este beneficio.")

    if request.method == "POST":
        benefit.is_active = not benefit.is_active
        benefit.save(update_fields=["is_active"])
        status = "activado" if benefit.is_active else "desactivado"
        messages.success(request, f"Beneficio {status} exitosamente.")

    return redirect("benefit_detail", pk=pk)

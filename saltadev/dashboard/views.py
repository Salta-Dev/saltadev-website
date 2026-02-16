"""Dashboard views for authenticated users."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from content.models import Event
from users.image_service import delete_local_image, upload_avatar
from users.models import Profile, User

from .forms import ProfileForm


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render the user dashboard with profile, membership and upcoming events."""
    user = request.user

    # Get or create user profile
    profile, _ = Profile.objects.get_or_create(user=user)

    # Get upcoming events (next 5 events from today)
    upcoming_events = Event.objects.filter(
        event_start_date__gte=timezone.now()
    ).order_by("event_start_date")[:5]

    # Build credential URL for QR code
    credential_url = f"{settings.SITE_URL}/credencial/{user.public_id}/"

    context = {
        "user": user,
        "profile": profile,
        "upcoming_events": upcoming_events,
        "credential_url": credential_url,
    }
    return render(request, "dashboard/index.html", context)


@login_required
def profile_edit_view(request: HttpRequest) -> HttpResponse:
    """Handle profile editing including avatar upload."""
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle avatar upload
            avatar_file = form.cleaned_data.get("avatar_file")
            if avatar_file:
                # Delete old avatar if it exists (local only)
                if profile.avatar_url and settings.DEBUG:
                    delete_local_image(profile.avatar_url)

                # Upload new avatar
                result = upload_avatar(avatar_file)
                if result.success:
                    profile.avatar_url = result.url or ""
                    profile.avatar_delete_url = result.delete_url or ""
                else:
                    messages.error(request, f"Error al subir imagen: {result.error}")

            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "user": user,
        "profile": profile,
        "form": form,
    }
    return render(request, "dashboard/profile_edit.html", context)


def public_credential_view(request: HttpRequest, public_id: str) -> HttpResponse:
    """Display a public credential page for a user."""
    user = get_object_or_404(User, public_id=public_id)
    profile, _ = Profile.objects.get_or_create(user=user)

    # Build credential URL for sharing
    credential_url = f"{settings.SITE_URL}/credencial/{user.public_id}/"

    context = {
        "credential_user": user,
        "credential_profile": profile,
        "credential_url": credential_url,
    }
    return render(request, "dashboard/public_credential.html", context)

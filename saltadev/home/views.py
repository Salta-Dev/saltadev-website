from content.models import Collaborator, Event, StaffProfile
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


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

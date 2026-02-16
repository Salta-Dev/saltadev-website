from content.models import Collaborator, Event, StaffProfile
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Render the homepage with latest events, staff members, and collaborators."""
    latest_events = Event.objects.order_by("-event_start_date")[:3]
    staff_members = StaffProfile.objects.select_related("user").order_by(
        "order", "created_at"
    )[:6]
    collaborators = Collaborator.objects.order_by("created_at")
    collaborators_count = Collaborator.objects.count()
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

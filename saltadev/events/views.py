from content.models import Event
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def events_list(request: HttpRequest) -> HttpResponse:
    """Render the events page with all events sorted by date."""
    events = Event.objects.order_by("-event_start_date")
    latest_event = events.first()
    return render(
        request, "events/index.html", {"events": events, "latest_event": latest_event}
    )

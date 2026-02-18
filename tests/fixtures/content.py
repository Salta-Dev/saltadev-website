"""Content model fixtures for testing."""

import uuid
from datetime import timedelta

import pytest
from content.models import Collaborator, Event, StaffProfile
from django.utils import timezone


def _unique_slug(prefix: str = "test") -> str:
    """Generate a unique slug."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def event(db):
    """Create and return a test event."""
    return Event.objects.create(
        title="Test Event",
        description="A test event description",
        event_start_date=timezone.now() + timedelta(days=7),
        event_end_date=timezone.now() + timedelta(days=7, hours=2),
        location="Test Location",
        slug=_unique_slug("event"),
        status=Event.Status.APPROVED,
    )


@pytest.fixture
def past_event(db):
    """Create and return a past event."""
    return Event.objects.create(
        title="Past Event",
        description="A past event description",
        event_start_date=timezone.now() - timedelta(days=7),
        event_end_date=timezone.now() - timedelta(days=7, hours=2),
        location="Past Location",
        slug=_unique_slug("past-event"),
        status=Event.Status.APPROVED,
    )


@pytest.fixture
def multiple_events(db):
    """Create multiple events for testing."""
    now = timezone.now()
    events = []
    for i in range(5):
        events.append(
            Event.objects.create(
                title=f"Event {i + 1}",
                description=f"Description {i + 1}",
                event_start_date=now + timedelta(days=i),
                event_end_date=now + timedelta(days=i, hours=2),
                location=f"Location {i + 1}",
                slug=_unique_slug(f"event-{i}"),
                status=Event.Status.APPROVED,
            )
        )
    return events


@pytest.fixture
def staff_profile(verified_user):
    """Create and return a staff profile."""
    return StaffProfile.objects.create(
        user=verified_user,
        role="Developer",
        bio="Test bio",
        order=1,
    )


@pytest.fixture
def collaborator(db):
    """Create and return a collaborator."""
    return Collaborator.objects.create(
        name="Test Collaborator",
        image_url="https://example.com/logo.png",
        link="https://example.com",
        slug=_unique_slug("collab"),
    )

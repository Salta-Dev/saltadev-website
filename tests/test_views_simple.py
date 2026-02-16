"""Tests for simple views (home, events, code_of_conduct)."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


class TestHomeView:
    """Tests for home view."""

    @pytest.mark.django_db
    def test_home_returns_200(self, client):
        """Home page should return 200 status."""
        response = client.get(reverse("home"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_home_uses_correct_template(self, client):
        """Home page should use home/index.html template."""
        response = client.get(reverse("home"))
        assert "home/index.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_home_contains_latest_events(self, client, multiple_events):
        """Home page should contain latest events."""
        response = client.get(reverse("home"))
        assert "latest_events" in response.context
        # Should show max 3 events
        assert len(response.context["latest_events"]) <= 3

    @pytest.mark.django_db
    def test_home_contains_staff_members(self, client, staff_profile):
        """Home page should contain staff members."""
        response = client.get(reverse("home"))
        assert "staff_members" in response.context

    @pytest.mark.django_db
    def test_home_contains_collaborators(self, client, collaborator):
        """Home page should contain collaborators."""
        response = client.get(reverse("home"))
        assert "collaborators" in response.context
        assert "collaborators_count" in response.context


class TestEventsView:
    """Tests for events list view."""

    @pytest.mark.django_db
    def test_events_returns_200(self, client):
        """Events page should return 200 status."""
        response = client.get(reverse("events"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_events_uses_correct_template(self, client):
        """Events page should use events/index.html template."""
        response = client.get(reverse("events"))
        assert "events/index.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_events_contains_all_events(self, client, multiple_events):
        """Events page should contain all events."""
        response = client.get(reverse("events"))
        assert "events" in response.context
        assert len(response.context["events"]) == len(multiple_events)

    @pytest.mark.django_db
    def test_events_contains_latest_event(self, client, event):
        """Events page should contain latest event."""
        response = client.get(reverse("events"))
        assert "latest_event" in response.context

    @pytest.mark.django_db
    def test_events_ordered_by_date_descending(self, client, multiple_events):
        """Events should be ordered by date descending."""
        response = client.get(reverse("events"))
        events = list(response.context["events"])
        for i in range(len(events) - 1):
            assert events[i].event_start_date >= events[i + 1].event_start_date


class TestCodeOfConductView:
    """Tests for code of conduct view."""

    @pytest.mark.django_db
    def test_code_of_conduct_returns_200(self, client):
        """Code of conduct page should return 200 status."""
        response = client.get(reverse("code_of_conduct"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_code_of_conduct_uses_correct_template(self, client):
        """Code of conduct page should use correct template."""
        response = client.get(reverse("code_of_conduct"))
        assert "code_of_conduct/index.html" in [t.name for t in response.templates]

"""Tests for the dashboard views."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardView:
    """Tests for the user dashboard."""

    def test_dashboard_requires_login(self):
        """Dashboard should redirect unauthenticated users to login."""
        client = Client()
        response = client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_dashboard_authenticated_returns_200(self, verified_user):
        """Dashboard should return 200 for authenticated users."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("dashboard"))
        assert response.status_code == 200

    def test_dashboard_context_includes_user(self, verified_user):
        """Dashboard context should include user and profile."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("dashboard"))
        assert "user" in response.context
        assert "profile" in response.context
        assert response.context["user"] == verified_user

    def test_dashboard_context_includes_events(self, verified_user):
        """Dashboard context should include upcoming events."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("dashboard"))
        assert "upcoming_events" in response.context

    def test_dashboard_context_includes_benefits(self, verified_user):
        """Dashboard context should include active benefits."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("dashboard"))
        assert "benefits" in response.context

    def test_dashboard_context_includes_credential_url(self, verified_user):
        """Dashboard context should include credential URL."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("dashboard"))
        assert "credential_url" in response.context
        assert verified_user.public_id in response.context["credential_url"]


@pytest.mark.django_db
class TestProfileEditView:
    """Tests for profile editing."""

    def test_profile_edit_requires_login(self):
        """Profile edit should redirect unauthenticated users."""
        client = Client()
        response = client.get(reverse("profile_edit"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_profile_edit_authenticated_returns_200(self, verified_user):
        """Profile edit should return 200 for authenticated users."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("profile_edit"))
        assert response.status_code == 200

    def test_profile_edit_includes_form(self, verified_user):
        """Profile edit should include the profile form."""
        client = Client()
        client.force_login(verified_user)
        response = client.get(reverse("profile_edit"))
        assert "form" in response.context

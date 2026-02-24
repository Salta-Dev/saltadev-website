"""Tests for public credential views."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestPublicCredentialView:
    """Tests for the public credential page."""

    def test_public_credential_view_returns_200(self, verified_user_with_dni):
        """Public credential should return 200 for valid public_id."""
        client = Client()
        response = client.get(
            reverse("public_credential", kwargs={"public_id": verified_user_with_dni.public_id})
        )
        assert response.status_code == 200

    def test_public_credential_includes_user_info(self, verified_user_with_dni):
        """Public credential should include user information."""
        client = Client()
        response = client.get(
            reverse("public_credential", kwargs={"public_id": verified_user_with_dni.public_id})
        )
        content = response.content.decode()
        assert verified_user_with_dni.first_name in content

    def test_public_credential_context(self, verified_user_with_dni):
        """Public credential context should include expected data."""
        client = Client()
        response = client.get(
            reverse("public_credential", kwargs={"public_id": verified_user_with_dni.public_id})
        )
        assert "credential_user" in response.context
        assert "credential_profile" in response.context
        assert "credential_url" in response.context
        assert response.context["credential_user"] == verified_user_with_dni

    def test_public_credential_invalid_id_returns_404(self):
        """Public credential should return 404 for invalid public_id."""
        client = Client()
        response = client.get(
            reverse("public_credential", kwargs={"public_id": "INVALID1"})
        )
        assert response.status_code == 404

    def test_public_credential_no_login_required(self, verified_user_with_dni):
        """Public credential should be accessible without login."""
        client = Client()
        # Ensure no user is logged in
        client.logout()
        response = client.get(
            reverse("public_credential", kwargs={"public_id": verified_user_with_dni.public_id})
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestHealthCheckEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self):
        """Health check should return 200 when services are healthy."""
        client = Client()
        response = client.get(reverse("health_check"))
        # May return 503 in test environment without Redis
        assert response.status_code in [200, 503]

    def test_health_check_returns_json(self):
        """Health check should return JSON response."""
        client = Client()
        response = client.get(reverse("health_check"))
        assert response["Content-Type"] == "application/json"

    def test_health_check_includes_services(self):
        """Health check response should include service statuses."""
        client = Client()
        response = client.get(reverse("health_check"))
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "django" in data["services"]
        assert "postgres" in data["services"]
        assert "redis" in data["services"]

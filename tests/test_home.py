"""Tests for the home view."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestHomeView:
    """Tests for the home page."""

    def test_home_view_returns_200(self):
        """Home view should return 200 status code."""
        client = Client()
        response = client.get(reverse("home"))
        assert response.status_code == 200

    def test_home_view_contains_expected_content(self):
        """Home view should contain expected HTML elements."""
        client = Client()
        response = client.get(reverse("home"))
        content = response.content.decode()
        # Check that page renders (contains basic HTML)
        assert "<html" in content or "<!DOCTYPE" in content

    def test_home_view_includes_events(self, multiple_events):
        """Home view should include events in context."""
        client = Client()
        response = client.get(reverse("home"))
        # Should have latest_events in context
        assert "latest_events" in response.context

    def test_home_view_includes_staff_members(self, staff_profile):
        """Home view should include staff members in context."""
        client = Client()
        response = client.get(reverse("home"))
        assert "staff_members" in response.context

    def test_home_view_includes_collaborators(self, collaborator):
        """Home view should include collaborators in context."""
        client = Client()
        response = client.get(reverse("home"))
        assert "collaborators" in response.context
        assert "collaborators_count" in response.context


@pytest.mark.django_db
class TestHomeViewQueryOptimization:
    """Tests for query optimization in home view."""

    def test_home_view_query_count(self, django_assert_max_num_queries, multiple_events):
        """Home view should use a reasonable number of queries (no N+1)."""
        client = Client()
        # The view uses 3 queries: collaborators, events, staff
        # This test ensures we don't have N+1 problems
        with django_assert_max_num_queries(5):
            client.get(reverse("home"))

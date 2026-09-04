"""Tests for public navigation and dashboard escape hatch."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestPublicNavAnonymous:
    """Anonymous visitors must reach login on every viewport."""

    def test_home_hides_header_login_on_mobile(self):
        """Header login is desktop-only; mobile keeps it inside the hamburger."""
        response = Client().get(reverse("home"))
        html = response.content.decode()
        assert 'id="nav-session-cta"' in html
        session_cta = html.split('id="nav-session-cta"', 1)[1].split("</a>", 1)[0]
        assert "hidden lg:inline-flex" in session_cta
        assert 'href="/login/"' in session_cta
        mobile_menu = html.split('id="mobileMenu"', 1)[1]
        assert "Iniciar sesión" in mobile_menu
        assert 'href="/login/"' in mobile_menu


@pytest.mark.django_db
class TestPublicNavAuthenticated:
    """Logged-in members keep the public site and get a personal greeting."""

    def test_home_greets_user_by_first_name(self, verified_user):
        client = Client()
        client.force_login(verified_user)
        html = client.get(reverse("home")).content.decode()
        assert "Hola, Test" in html
        assert "Iniciar sesión" not in html
        greeting = html.split('id="hero-user-greeting"', 1)[1]
        assert "Hola, Test" in greeting.split("Comunidad salteña", 1)[0]

    def test_home_session_cta_points_to_dashboard(self, verified_user):
        client = Client()
        client.force_login(verified_user)
        html = client.get(reverse("home")).content.decode()
        session_cta = html.split('id="nav-session-cta"', 1)[1].split("</a>", 1)[0]
        assert 'href="/dashboard/"' in session_cta

    def test_home_still_links_to_public_pages(self, verified_user):
        client = Client()
        client.force_login(verified_user)
        html = client.get(reverse("home")).content.decode()
        assert "/eventos/" in html
        assert "/reglamento/" in html
        assert 'href="/"' in html


@pytest.mark.django_db
class TestDashboardSiteEscape:
    """Dashboard must offer a labeled path back to the public website."""

    def test_dashboard_has_labeled_home_link(self, verified_user):
        client = Client()
        client.force_login(verified_user)
        html = client.get(reverse("dashboard")).content.decode()
        assert "Ir al sitio" in html
        assert html.count('href="/"') >= 1
        assert html.count("Ir al sitio") >= 2

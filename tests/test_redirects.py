"""Tests for content/redirects.py module."""

import pytest
from django.test import Client, override_settings
from django.urls import reverse


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


class TestRedirectViews:
    """Tests for redirect views."""

    @pytest.mark.django_db
    @override_settings(SITE_DISCORD="https://discord.gg/test")
    def test_discord_redirect(self, client):
        """Should redirect to Discord URL."""
        response = client.get(reverse("redirect_discord"))
        assert response.status_code == 302
        assert response.url == "https://discord.gg/test"

    @pytest.mark.django_db
    @override_settings(SITE_WHATSAPP="https://chat.whatsapp.com/test")
    def test_whatsapp_redirect(self, client):
        """Should redirect to WhatsApp URL."""
        response = client.get(reverse("redirect_whatsapp"))
        assert response.status_code == 302
        assert response.url == "https://chat.whatsapp.com/test"

    @pytest.mark.django_db
    @override_settings(SITE_LINKEDIN="https://linkedin.com/company/test")
    def test_linkedin_redirect(self, client):
        """Should redirect to LinkedIn URL."""
        response = client.get(reverse("redirect_linkedin"))
        assert response.status_code == 302
        assert response.url == "https://linkedin.com/company/test"

    @pytest.mark.django_db
    @override_settings(SITE_GITHUB="https://github.com/test")
    def test_github_redirect(self, client):
        """Should redirect to GitHub URL."""
        response = client.get(reverse("redirect_github"))
        assert response.status_code == 302
        assert response.url == "https://github.com/test"

    @pytest.mark.django_db
    @override_settings(SITE_TWITTER="https://twitter.com/test")
    def test_twitter_redirect(self, client):
        """Should redirect to Twitter URL."""
        response = client.get(reverse("redirect_twitter"))
        assert response.status_code == 302
        assert response.url == "https://twitter.com/test"

    @pytest.mark.django_db
    @override_settings(SITE_INSTAGRAM="https://instagram.com/test")
    def test_instagram_redirect(self, client):
        """Should redirect to Instagram URL."""
        response = client.get(reverse("redirect_instagram"))
        assert response.status_code == 302
        assert response.url == "https://instagram.com/test"

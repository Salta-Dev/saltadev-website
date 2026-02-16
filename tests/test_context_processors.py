"""Tests for content/context_processors.py module."""

import pytest
from django.test import RequestFactory, override_settings

from content.context_processors import site_links


@pytest.fixture
def request_factory():
    """Return a Django RequestFactory."""
    return RequestFactory()


class TestSiteLinks:
    """Tests for site_links context processor."""

    def test_returns_dict(self, request_factory):
        """Should return a dictionary."""
        request = request_factory.get("/")
        result = site_links(request)
        assert isinstance(result, dict)

    def test_contains_all_social_links(self, request_factory):
        """Should contain all social link keys."""
        request = request_factory.get("/")
        result = site_links(request)

        expected_keys = [
            "site_whatsapp",
            "site_discord",
            "site_github",
            "site_linkedin",
            "site_twitter",
            "site_instagram",
        ]
        for key in expected_keys:
            assert key in result

    @override_settings(SITE_WHATSAPP="https://whatsapp.example.com")
    def test_returns_whatsapp_from_settings(self, request_factory):
        """Should return WhatsApp URL from settings."""
        request = request_factory.get("/")
        result = site_links(request)
        assert result["site_whatsapp"] == "https://whatsapp.example.com"

    @override_settings(SITE_DISCORD="https://discord.example.com")
    def test_returns_discord_from_settings(self, request_factory):
        """Should return Discord URL from settings."""
        request = request_factory.get("/")
        result = site_links(request)
        assert result["site_discord"] == "https://discord.example.com"

    @override_settings(SITE_GITHUB="https://github.example.com")
    def test_returns_github_from_settings(self, request_factory):
        """Should return GitHub URL from settings."""
        request = request_factory.get("/")
        result = site_links(request)
        assert result["site_github"] == "https://github.example.com"

    def test_returns_empty_string_for_missing_settings(self, request_factory, settings):
        """Should return empty string if setting is not defined."""
        # Remove the setting if it exists
        if hasattr(settings, "SITE_WHATSAPP"):
            delattr(settings, "SITE_WHATSAPP")

        request = request_factory.get("/")
        result = site_links(request)
        # Should not raise an error
        assert isinstance(result["site_whatsapp"], str)

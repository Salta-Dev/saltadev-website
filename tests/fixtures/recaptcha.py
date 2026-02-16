"""reCAPTCHA fixtures for testing."""

import pytest
from django_recaptcha import client


@pytest.fixture(autouse=True)
def recaptcha_always_valid(monkeypatch):
    """Mock reCAPTCHA to always return valid response."""

    def _submit(*args, **kwargs):
        return client.RecaptchaResponse(True)

    monkeypatch.setattr(client, "submit", _submit)


@pytest.fixture
def recaptcha_settings(settings):
    """Configure reCAPTCHA test keys."""
    settings.RECAPTCHA_PUBLIC_KEY = "test"
    settings.RECAPTCHA_PRIVATE_KEY = "test"
    return settings

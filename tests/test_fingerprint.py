"""Tests for users/fingerprint.py module."""

import pytest
from django.http import HttpResponse

from users.fingerprint import attach_fingerprint_cookie
from users.ratelimit import FINGERPRINT_COOKIE, FINGERPRINT_MAX_AGE


class TestAttachFingerprintCookie:
    """Tests for attach_fingerprint_cookie function."""

    def test_sets_cookie_when_should_set_is_true(self):
        """Should set fingerprint cookie when should_set_cookie is True."""
        response = HttpResponse()
        fingerprint = "test-fp-123"

        result = attach_fingerprint_cookie(response, fingerprint, should_set_cookie=True)

        assert FINGERPRINT_COOKIE in result.cookies
        cookie = result.cookies[FINGERPRINT_COOKIE]
        assert cookie.value == fingerprint
        assert cookie["max-age"] == FINGERPRINT_MAX_AGE
        assert cookie["httponly"] is True
        assert cookie["samesite"] == "Lax"

    def test_does_not_set_cookie_when_should_set_is_false(self):
        """Should not set cookie when should_set_cookie is False."""
        response = HttpResponse()
        fingerprint = "test-fp-123"

        result = attach_fingerprint_cookie(response, fingerprint, should_set_cookie=False)

        assert FINGERPRINT_COOKIE not in result.cookies

    def test_returns_same_response_object(self):
        """Should return the same response object."""
        response = HttpResponse("test content")
        result = attach_fingerprint_cookie(response, "fp", should_set_cookie=True)
        assert result is response

    def test_preserves_response_content(self):
        """Should preserve response content."""
        response = HttpResponse("original content")
        result = attach_fingerprint_cookie(response, "fp", should_set_cookie=True)
        assert result.content == b"original content"

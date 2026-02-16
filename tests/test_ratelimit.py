"""Tests for users/ratelimit.py module."""

import pytest
from django.core.cache import cache

from users.ratelimit import (
    COOLDOWN_SECONDS,
    FINGERPRINT_COOKIE,
    FINGERPRINT_HEADER,
    LOGIN_LIMIT,
    REGISTER_LIMIT,
    SCOPES,
    VERIFY_LIMIT,
    build_keys,
    clear_limits,
    get_client_ip,
    get_fingerprint,
    increment,
    is_blocked,
    reset,
)


class TestGetClientIp:
    """Tests for get_client_ip function."""

    def test_returns_remote_addr(self, get_request):
        """Should return REMOTE_ADDR when no forwarded header."""
        request = get_request()
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        assert get_client_ip(request) == "192.168.1.1"

    def test_returns_forwarded_for_first_ip(self, request_with_forwarded_ip):
        """Should return first IP from X-Forwarded-For header."""
        request = request_with_forwarded_ip("203.0.113.1, 70.41.3.18, 150.172.238.178")
        assert get_client_ip(request) == "203.0.113.1"

    def test_returns_forwarded_for_single_ip(self, request_with_forwarded_ip):
        """Should return single IP from X-Forwarded-For header."""
        request = request_with_forwarded_ip("203.0.113.1")
        assert get_client_ip(request) == "203.0.113.1"

    def test_strips_whitespace(self, request_with_forwarded_ip):
        """Should strip whitespace from IP addresses."""
        request = request_with_forwarded_ip("  203.0.113.1  ")
        assert get_client_ip(request) == "203.0.113.1"

    def test_empty_remote_addr(self, get_request):
        """Should return empty string when REMOTE_ADDR is missing."""
        request = get_request()
        request.META.pop("REMOTE_ADDR", None)
        assert get_client_ip(request) == ""


class TestGetFingerprint:
    """Tests for get_fingerprint function."""

    def test_returns_fingerprint_from_header(self, get_request):
        """Should return fingerprint from header if present."""
        request = get_request()
        request.META[FINGERPRINT_HEADER] = "header-fp-123"
        fp, should_set = get_fingerprint(request)
        assert fp == "header-fp-123"
        assert should_set is False

    def test_returns_fingerprint_from_cookie(self, request_with_fingerprint):
        """Should return fingerprint from cookie if present."""
        request = request_with_fingerprint("cookie-fp-456")
        fp, should_set = get_fingerprint(request)
        assert fp == "cookie-fp-456"
        assert should_set is False

    def test_header_takes_precedence_over_cookie(self, request_with_fingerprint):
        """Header fingerprint should take precedence over cookie."""
        request = request_with_fingerprint("cookie-fp")
        request.META[FINGERPRINT_HEADER] = "header-fp"
        fp, should_set = get_fingerprint(request)
        assert fp == "header-fp"
        assert should_set is False

    def test_generates_new_fingerprint_if_missing(self, get_request):
        """Should generate a new UUID fingerprint if none present."""
        request = get_request()
        fp, should_set = get_fingerprint(request)
        assert len(fp) == 36  # UUID format
        assert "-" in fp
        assert should_set is True


class TestBuildKeys:
    """Tests for build_keys function."""

    def test_builds_ip_and_fp_keys(self):
        """Should build keys for IP and fingerprint."""
        keys = build_keys("login", "192.168.1.1", None, "fp123")
        assert "rl:login:ip:192.168.1.1" in keys
        assert "rl:login:fp:fp123" in keys
        assert len(keys) == 2

    def test_builds_email_key_when_provided(self):
        """Should include email key when email is provided."""
        keys = build_keys("login", "192.168.1.1", "user@example.com", "fp123")
        assert "rl:login:ip:192.168.1.1" in keys
        assert "rl:login:fp:fp123" in keys
        assert "rl:login:ip_email:192.168.1.1:user@example.com" in keys
        assert len(keys) == 3

    def test_email_is_lowercased(self):
        """Should lowercase email in keys."""
        keys = build_keys("login", "192.168.1.1", "USER@EXAMPLE.COM", "fp123")
        assert "rl:login:ip_email:192.168.1.1:user@example.com" in keys

    def test_handles_email_list(self):
        """Should handle email as a list (from form data)."""
        keys = build_keys("login", "192.168.1.1", ["user@example.com"], "fp123")
        assert "rl:login:ip_email:192.168.1.1:user@example.com" in keys

    def test_handles_empty_email_list(self):
        """Should handle empty email list."""
        keys = build_keys("login", "192.168.1.1", [], "fp123")
        assert len(keys) == 2  # No email key

    def test_handles_empty_email_string(self):
        """Should not include email key for empty string."""
        keys = build_keys("login", "192.168.1.1", "", "fp123")
        assert len(keys) == 2


class TestIsBlocked:
    """Tests for is_blocked function."""

    def test_not_blocked_when_under_limit(self):
        """Should return False when under the limit."""
        keys = ["rl:login:ip:127.0.0.1"]
        cache.set(keys[0], 2, 60)
        assert is_blocked(keys, 5) is False

    def test_blocked_when_at_limit(self):
        """Should return True when at the limit."""
        keys = ["rl:login:ip:127.0.0.1"]
        cache.set(keys[0], 5, 60)
        assert is_blocked(keys, 5) is True

    def test_blocked_when_over_limit(self):
        """Should return True when over the limit."""
        keys = ["rl:login:ip:127.0.0.1"]
        cache.set(keys[0], 10, 60)
        assert is_blocked(keys, 5) is True

    def test_not_blocked_when_no_cache(self):
        """Should return False when no cache entries exist."""
        keys = ["rl:login:ip:127.0.0.1"]
        assert is_blocked(keys, 5) is False

    def test_blocked_if_any_key_at_limit(self):
        """Should return True if any key is at the limit."""
        keys = ["rl:login:ip:127.0.0.1", "rl:login:fp:abc"]
        cache.set(keys[0], 1, 60)
        cache.set(keys[1], 5, 60)
        assert is_blocked(keys, 5) is True


class TestIncrement:
    """Tests for increment function."""

    def test_increments_new_key(self):
        """Should create new key with value 1."""
        keys = ["rl:test:ip:127.0.0.1"]
        increment(keys)
        assert cache.get(keys[0]) == 1

    def test_increments_existing_key(self):
        """Should increment existing key."""
        keys = ["rl:test:ip:127.0.0.1"]
        cache.set(keys[0], 3, 60)
        increment(keys)
        assert cache.get(keys[0]) == 4

    def test_increments_all_keys(self):
        """Should increment all keys."""
        keys = ["rl:test:ip:127.0.0.1", "rl:test:fp:abc"]
        increment(keys)
        assert cache.get(keys[0]) == 1
        assert cache.get(keys[1]) == 1


class TestReset:
    """Tests for reset function."""

    def test_deletes_all_keys(self):
        """Should delete all cache keys."""
        keys = ["rl:test:ip:127.0.0.1", "rl:test:fp:abc"]
        for key in keys:
            cache.set(key, 5, 60)
        reset(keys)
        assert cache.get(keys[0]) is None
        assert cache.get(keys[1]) is None


class TestClearLimits:
    """Tests for clear_limits function."""

    def test_clears_ip_limits(self):
        """Should clear limits for IP across all scopes."""
        ip = "192.168.1.1"
        for scope in SCOPES:
            cache.set(f"rl:{scope}:ip:{ip}", 5, 60)

        cleared = clear_limits(SCOPES, ip_address=ip)

        assert len(cleared) == len(SCOPES)
        for scope in SCOPES:
            assert cache.get(f"rl:{scope}:ip:{ip}") is None

    def test_clears_fingerprint_limits(self):
        """Should clear limits for fingerprint across all scopes."""
        fp = "test-fingerprint"
        for scope in SCOPES:
            cache.set(f"rl:{scope}:fp:{fp}", 5, 60)

        cleared = clear_limits(SCOPES, fingerprint=fp)

        assert len(cleared) == len(SCOPES)
        for scope in SCOPES:
            assert cache.get(f"rl:{scope}:fp:{fp}") is None

    def test_clears_ip_email_combo(self):
        """Should clear IP+email combo limits."""
        ip = "192.168.1.1"
        email = "test@example.com"
        for scope in SCOPES:
            cache.set(f"rl:{scope}:ip_email:{ip}:{email}", 5, 60)

        cleared = clear_limits(SCOPES, ip_address=ip, email=email)

        # Should clear IP, and IP+email for each scope
        for scope in SCOPES:
            assert cache.get(f"rl:{scope}:ip_email:{ip}:{email}") is None

    def test_returns_empty_list_when_no_identifiers(self):
        """Should return empty list when no identifiers provided."""
        cleared = clear_limits(SCOPES)
        assert cleared == []


class TestConstants:
    """Tests for module constants."""

    def test_limits_are_positive(self):
        """All limits should be positive integers."""
        assert VERIFY_LIMIT > 0
        assert LOGIN_LIMIT > 0
        assert REGISTER_LIMIT > 0

    def test_cooldown_is_one_hour(self):
        """Cooldown should be one hour in seconds."""
        assert COOLDOWN_SECONDS == 3600

    def test_fingerprint_cookie_name(self):
        """Fingerprint cookie should have expected name."""
        assert FINGERPRINT_COOKIE == "sd_fp"

    def test_fingerprint_header_name(self):
        """Fingerprint header should have expected name."""
        assert FINGERPRINT_HEADER == "HTTP_X_CLIENT_FP"

    def test_scopes_defined(self):
        """All expected scopes should be defined."""
        assert "verify" in SCOPES
        assert "login" in SCOPES
        assert "register" in SCOPES

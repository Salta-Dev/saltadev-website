"""Rate limiting utilities for authentication views."""

import uuid
from collections.abc import Iterable
from datetime import timedelta

from django.core.cache import cache
from django.http import HttpRequest

VERIFY_LIMIT = 5
LOGIN_LIMIT = 5
REGISTER_LIMIT = 3
PASSWORD_RESET_REQUEST_LIMIT = 5
PASSWORD_RESET_CONFIRM_LIMIT = 5
SCOPES = (
    "verify",
    "login",
    "register",
    "password_reset_request",
    "password_reset_confirm",
)
COOLDOWN_SECONDS = 60 * 60
FINGERPRINT_COOKIE = "sd_fp"
FINGERPRINT_HEADER = "HTTP_X_CLIENT_FP"
FINGERPRINT_MAX_AGE = int(timedelta(days=30).total_seconds())


def get_client_ip(request: HttpRequest) -> str:
    """Extract the client IP address from the request, respecting X-Forwarded-For."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "").strip()


def get_fingerprint(request: HttpRequest) -> tuple[str, bool]:
    """Return (fingerprint, should_set_cookie) from header, cookie, or a new UUID."""
    fingerprint = request.META.get(FINGERPRINT_HEADER) or request.COOKIES.get(
        FINGERPRINT_COOKIE
    )
    if fingerprint:
        return fingerprint, False
    return str(uuid.uuid4()), True


def build_keys(
    scope: str,
    ip_address: str,
    email: str | list[str] | None,
    fingerprint: str,
) -> list[str]:
    """Build cache keys for rate limiting based on IP, fingerprint, and email."""
    keys = [f"rl:{scope}:ip:{ip_address}", f"rl:{scope}:fp:{fingerprint}"]
    if isinstance(email, list):
        email_value: str = email[0] if email else ""
    else:
        email_value = email or ""
    email_key = email_value.strip().lower()
    if email_key:
        keys.append(f"rl:{scope}:ip_email:{ip_address}:{email_key}")
    return keys


def is_blocked(keys: Iterable[str], limit: int) -> bool:
    """Return True if any cache key has reached or exceeded the limit."""
    return any(cache.get(key, 0) >= limit for key in keys)


def increment(keys: Iterable[str]) -> None:
    """Increment the attempt counter for each cache key."""
    for key in keys:
        if cache.add(key, 1, COOLDOWN_SECONDS):
            continue
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, COOLDOWN_SECONDS)


def reset(keys: Iterable[str]) -> None:
    """Delete all cache keys, resetting their rate limit counters."""
    for key in keys:
        cache.delete(key)


def clear_limits(
    scopes: Iterable[str],
    ip_address: str | None = None,
    email: str | None = None,
    fingerprint: str | None = None,
) -> list[str]:
    """Clear rate limit counters across all given scopes for the specified identifiers."""
    cleared = []
    email_key = (email or "").strip().lower()
    ip_key = (ip_address or "").strip()
    fp_key = (fingerprint or "").strip()

    for scope in scopes:
        if ip_key:
            cleared.append(f"rl:{scope}:ip:{ip_key}")
        if fp_key:
            cleared.append(f"rl:{scope}:fp:{fp_key}")
        if ip_key and email_key:
            cleared.append(f"rl:{scope}:ip_email:{ip_key}:{email_key}")

    if cleared:
        cache.delete_many(cleared)
    return cleared

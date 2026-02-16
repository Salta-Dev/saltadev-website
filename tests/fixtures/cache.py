"""Cache fixtures for testing rate limiting."""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def rate_limit_keys():
    """Return a factory for creating rate limit cache keys."""

    def _make_keys(scope, ip="127.0.0.1", email=None, fingerprint="test-fp"):
        keys = [f"rl:{scope}:ip:{ip}", f"rl:{scope}:fp:{fingerprint}"]
        if email:
            keys.append(f"rl:{scope}:ip_email:{ip}:{email.lower()}")
        return keys

    return _make_keys


@pytest.fixture
def block_rate_limit(rate_limit_keys):
    """Return a helper to block a rate limit scope."""

    def _block(scope, limit=5, ip="127.0.0.1", email=None, fingerprint="test-fp"):
        keys = rate_limit_keys(scope, ip, email, fingerprint)
        for key in keys:
            cache.set(key, limit, 3600)

    return _block

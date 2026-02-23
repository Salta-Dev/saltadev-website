"""Password reset fixtures for testing."""

from datetime import timedelta

import pytest
from django.utils import timezone
from password_reset.models import PasswordResetToken
from users.utils import hash_token


@pytest.fixture
def password_reset_token(db, verified_user):
    """Create and return a valid password reset token."""
    raw_token = "valid_token_123456"
    return PasswordResetToken.objects.create(
        user=verified_user,
        token_hash=hash_token(raw_token),
        expires_at=timezone.now() + timedelta(minutes=10),
        used=False,
    ), raw_token


@pytest.fixture
def expired_reset_token(db, verified_user):
    """Create and return an expired password reset token."""
    raw_token = "expired_token_123456"
    return PasswordResetToken.objects.create(
        user=verified_user,
        token_hash=hash_token(raw_token),
        expires_at=timezone.now() - timedelta(minutes=5),
        used=False,
    ), raw_token


@pytest.fixture
def used_reset_token(db, verified_user):
    """Create and return a used password reset token."""
    raw_token = "used_token_123456"
    return PasswordResetToken.objects.create(
        user=verified_user,
        token_hash=hash_token(raw_token),
        expires_at=timezone.now() + timedelta(minutes=10),
        used=True,
    ), raw_token

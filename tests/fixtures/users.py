"""User-related fixtures for testing."""

from datetime import date

import pytest
from users.models import EmailVerificationCode, Profile, User


@pytest.fixture
def user_data():
    """Return default user data for registration."""
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "birth_date": date(2000, 1, 15),
        "password": "SecurePass123$",
    }


@pytest.fixture
def user(db, user_data):
    """Create and return a test user."""
    return User.objects.create_user(**user_data)


@pytest.fixture
def verified_user(user):
    """Return a user with confirmed email."""
    user.email_confirmed = True
    user.save()
    return user


@pytest.fixture
def verified_user_with_dni(verified_user):
    """Return a verified user with DNI set (required for credential views)."""
    profile, _ = Profile.objects.get_or_create(user=verified_user)
    profile.dni = "12345678"
    profile.save()
    return verified_user


@pytest.fixture
def unverified_user(user):
    """Return a user with unconfirmed email."""
    user.email_confirmed = False
    user.save()
    return user


@pytest.fixture
def staff_user(db, user_data):
    """Create and return a staff user."""
    data = user_data.copy()
    data["email"] = "staff@example.com"
    data["is_staff"] = True
    return User.objects.create_user(**data)


@pytest.fixture
def superuser(db, user_data):
    """Create and return a superuser."""
    data = user_data.copy()
    data["email"] = "admin@example.com"
    return User.objects.create_superuser(**data)


@pytest.fixture
def verification_code(user):
    """Create a verification code for the user."""
    return EmailVerificationCode.objects.create(user=user, code="123456")


@pytest.fixture
def expired_verification_code(user):
    """Create an expired verification code."""
    from datetime import timedelta

    from django.utils import timezone

    code = EmailVerificationCode.objects.create(user=user, code="654321")
    # Manually set created_at to 25 hours ago
    EmailVerificationCode.objects.filter(pk=code.pk).update(
        created_at=timezone.now() - timedelta(hours=25)
    )
    code.refresh_from_db()
    return code

"""Tests for user models."""

from datetime import date

import pytest
from users.models import EmailVerificationCode, Profile, User


class TestUserManager:
    """Tests for UserManager."""

    @pytest.mark.django_db
    def test_create_user(self):
        """Should create a regular user."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            birth_date=date(2000, 1, 15),
            password="SecurePass123$",
        )
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.role == "miembro"
        assert user.check_password("SecurePass123$")

    @pytest.mark.django_db
    def test_create_user_normalizes_email(self):
        """Should normalize email address."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.com",
            first_name="Test",
            last_name="User",
            birth_date=date(2000, 1, 15),
            password="SecurePass123$",
        )
        assert user.email == "Test@example.com"

    @pytest.mark.django_db
    def test_create_user_requires_email(self):
        """Should raise error when email is empty."""
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(
                email="",
                first_name="Test",
                last_name="User",
                birth_date=date(2000, 1, 15),
                password="SecurePass123$",
            )

    @pytest.mark.django_db
    def test_create_superuser(self):
        """Should create a superuser."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            birth_date=date(1990, 1, 15),
            password="AdminPass123$",
        )
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == "administrador"

    @pytest.mark.django_db
    def test_create_superuser_requires_is_staff(self):
        """Should raise error when is_staff is False."""
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                birth_date=date(1990, 1, 15),
                password="AdminPass123$",
                is_staff=False,
            )

    @pytest.mark.django_db
    def test_create_superuser_requires_is_superuser(self):
        """Should raise error when is_superuser is False."""
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                birth_date=date(1990, 1, 15),
                password="AdminPass123$",
                is_superuser=False,
            )


class TestUserModel:
    """Tests for User model."""

    @pytest.mark.django_db
    def test_str_representation(self, user):
        """Should return name and email."""
        expected = f"{user.first_name} {user.last_name} ({user.email})"
        assert str(user) == expected

    @pytest.mark.django_db
    def test_username_field_is_email(self):
        """USERNAME_FIELD should be email."""
        assert User.USERNAME_FIELD == "email"

    @pytest.mark.django_db
    def test_required_fields(self):
        """Should have correct required fields."""
        assert "first_name" in User.REQUIRED_FIELDS
        assert "last_name" in User.REQUIRED_FIELDS
        assert "birth_date" in User.REQUIRED_FIELDS

    @pytest.mark.django_db
    def test_default_role_is_miembro(self, user):
        """Default role should be miembro."""
        assert user.role == "miembro"

    @pytest.mark.django_db
    def test_email_confirmed_default_false(self, user):
        """email_confirmed should default to False."""
        assert user.email_confirmed is False


class TestProfileModel:
    """Tests for Profile model."""

    @pytest.mark.django_db
    def test_create_profile(self, user):
        """Should create a profile for user."""
        profile = Profile.objects.create(
            user=user,
            phone="123456789",
            technical_role="backend",
            bio="Test bio",
        )
        assert profile.user == user
        assert profile.phone == "123456789"
        assert profile.technical_role == "backend"

    @pytest.mark.django_db
    def test_str_representation(self, user):
        """Should return profile for email."""
        profile = Profile.objects.create(user=user)
        assert str(profile) == f"Profile for {user.email}"

    @pytest.mark.django_db
    def test_default_available_true(self, user):
        """available should default to True."""
        profile = Profile.objects.create(user=user)
        assert profile.available is True

    @pytest.mark.django_db
    def test_technologies_default_empty_list(self, user):
        """technologies should default to empty list."""
        profile = Profile.objects.create(user=user)
        assert profile.technologies == []


class TestEmailVerificationCodeModel:
    """Tests for EmailVerificationCode model."""

    @pytest.mark.django_db
    def test_create_verification_code(self, user):
        """Should create verification code."""
        code = EmailVerificationCode.objects.create(user=user, code="123456")
        assert code.user == user
        assert code.code == "123456"
        assert code.used is False

    @pytest.mark.django_db
    def test_str_representation(self, user):
        """Should return verification code for email."""
        code = EmailVerificationCode.objects.create(user=user, code="123456")
        assert str(code) == f"Verification code for {user.email}"

    @pytest.mark.django_db
    def test_created_at_auto_set(self, user):
        """created_at should be set automatically."""
        code = EmailVerificationCode.objects.create(user=user, code="123456")
        assert code.created_at is not None

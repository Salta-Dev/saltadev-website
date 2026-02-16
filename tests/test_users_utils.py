"""Tests for users/utils.py module."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from users.models import EmailVerificationCode
from users.utils import (
    generate_reset_token,
    generate_verification_code,
    hash_token,
    verify_code,
)


class TestGenerateVerificationCode:
    """Tests for generate_verification_code function."""

    def test_generates_6_digit_code(self):
        """Should generate a 6-digit numeric code."""
        code = generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generates_unique_codes(self):
        """Should generate different codes on each call."""
        codes = {generate_verification_code() for _ in range(100)}
        # With 6 digits, should have high uniqueness
        assert len(codes) > 90


class TestGenerateResetToken:
    """Tests for generate_reset_token function."""

    def test_generates_url_safe_token(self):
        """Should generate a URL-safe token."""
        token = generate_reset_token()
        assert len(token) > 20
        # URL-safe characters only
        assert all(c.isalnum() or c in "-_" for c in token)

    def test_generates_unique_tokens(self):
        """Should generate different tokens on each call."""
        tokens = {generate_reset_token() for _ in range(100)}
        assert len(tokens) == 100


class TestHashToken:
    """Tests for hash_token function."""

    def test_returns_sha256_hex(self):
        """Should return SHA-256 hex digest."""
        hashed = hash_token("test-token")
        assert len(hashed) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in hashed)

    def test_same_input_same_hash(self):
        """Same input should produce same hash."""
        assert hash_token("test") == hash_token("test")

    def test_different_input_different_hash(self):
        """Different input should produce different hash."""
        assert hash_token("test1") != hash_token("test2")


class TestVerifyCode:
    """Tests for verify_code function."""

    @pytest.mark.django_db
    def test_valid_code_verifies_user(self, user, verification_code):
        """Should verify user with valid code."""
        assert user.email_confirmed is False
        result = verify_code(user, verification_code.code)
        assert result is True
        user.refresh_from_db()
        assert user.email_confirmed is True

    @pytest.mark.django_db
    def test_marks_code_as_used(self, user, verification_code):
        """Should mark verification code as used."""
        verify_code(user, verification_code.code)
        verification_code.refresh_from_db()
        assert verification_code.used is True

    @pytest.mark.django_db
    def test_invalid_code_returns_false(self, user, verification_code):
        """Should return False for invalid code."""
        result = verify_code(user, "000000")
        assert result is False
        user.refresh_from_db()
        assert user.email_confirmed is False

    @pytest.mark.django_db
    def test_used_code_returns_false(self, user, verification_code):
        """Should return False for already used code."""
        verification_code.used = True
        verification_code.save()
        result = verify_code(user, verification_code.code)
        assert result is False

    @pytest.mark.django_db
    def test_expired_code_returns_false(self, user, expired_verification_code):
        """Should return False for expired code (>24 hours)."""
        result = verify_code(user, expired_verification_code.code)
        assert result is False
        user.refresh_from_db()
        assert user.email_confirmed is False

    @pytest.mark.django_db
    def test_only_newest_code_is_valid(self, user):
        """Should only accept the newest unused code."""
        # Create first code
        old_code = EmailVerificationCode.objects.create(user=user, code="111111")
        # Create second code (newer)
        new_code = EmailVerificationCode.objects.create(user=user, code="222222")

        # Old code should not work
        result = verify_code(user, old_code.code)
        assert result is False

        # New code should work
        result = verify_code(user, new_code.code)
        assert result is True

    @pytest.mark.django_db
    def test_no_codes_returns_false(self, user):
        """Should return False when user has no verification codes."""
        result = verify_code(user, "123456")
        assert result is False


class TestSendVerificationCode:
    """Tests for send_verification_code function."""

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_creates_verification_code(self, mock_send_mail, user):
        """Should create a new verification code."""
        from users.utils import send_verification_code

        initial_count = EmailVerificationCode.objects.filter(user=user).count()
        send_verification_code(user)
        assert (
            EmailVerificationCode.objects.filter(user=user, used=False).count()
            == initial_count + 1
        )

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_invalidates_existing_codes(self, mock_send_mail, user):
        """Should mark existing codes as used."""
        from users.utils import send_verification_code

        # Create existing code
        old_code = EmailVerificationCode.objects.create(user=user, code="111111")
        send_verification_code(user)

        old_code.refresh_from_db()
        assert old_code.used is True

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_sends_email(self, mock_send_mail, user):
        """Should send email with verification code."""
        from users.utils import send_verification_code

        send_verification_code(user)

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        assert user.email in call_kwargs["recipient_list"]
        assert "Verifica tu email" in call_kwargs["subject"]


class TestCreatePasswordResetToken:
    """Tests for create_password_reset_token function."""

    @pytest.mark.django_db
    def test_creates_token(self, user):
        """Should create a password reset token."""
        from password_reset.models import PasswordResetToken
        from users.utils import create_password_reset_token

        token = create_password_reset_token(user)

        assert len(token) > 20
        assert PasswordResetToken.objects.filter(user=user, used=False).exists()

    @pytest.mark.django_db
    def test_invalidates_existing_tokens(self, user):
        """Should mark existing tokens as used."""
        from password_reset.models import PasswordResetToken
        from users.utils import create_password_reset_token

        # Create first token
        first_token = create_password_reset_token(user)
        first_db_token = PasswordResetToken.objects.filter(user=user, used=False).first()

        # Create second token
        create_password_reset_token(user)

        first_db_token.refresh_from_db()
        assert first_db_token.used is True

    @pytest.mark.django_db
    def test_token_has_correct_hash(self, user):
        """Should store the correct hash of the token."""
        from password_reset.models import PasswordResetToken
        from users.utils import create_password_reset_token, hash_token

        token = create_password_reset_token(user)
        db_token = PasswordResetToken.objects.filter(user=user, used=False).first()

        assert db_token.token_hash == hash_token(token)


class TestSendPasswordReset:
    """Tests for send_password_reset function."""

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_sends_email(self, mock_send_mail, user):
        """Should send password reset email."""
        from users.utils import send_password_reset

        reset_link = "https://example.com/reset/abc123"
        send_password_reset(user, reset_link)

        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args[1]
        assert user.email in call_kwargs["recipient_list"]
        assert "Recuperación de contraseña" in call_kwargs["subject"]

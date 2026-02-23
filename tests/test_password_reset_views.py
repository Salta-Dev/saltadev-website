"""Tests for password reset views."""

from unittest.mock import patch

import pytest
from django.urls import reverse
from password_reset.models import PasswordResetToken


@pytest.mark.django_db
class TestPasswordResetRequestView:
    """Tests for password reset request view."""

    def test_request_get_returns_form(self, client):
        """Test GET request returns the form."""
        response = client.get(reverse("password_reset_request"))
        assert response.status_code == 200
        assert "form" in response.context

    @patch("password_reset.views.send_password_reset")
    def test_request_valid_email_sends_email(self, mock_send, client, verified_user):
        """Test valid email triggers password reset email."""
        response = client.post(
            reverse("password_reset_request"),
            {
                "email": verified_user.email,
                "g-recaptcha-response": "test",
            },
        )
        assert response.status_code == 302
        assert mock_send.called

    @patch("password_reset.views.send_password_reset")
    def test_request_unknown_email_no_enumeration(self, mock_send, client):
        """Test unknown email doesn't reveal user existence."""
        response = client.post(
            reverse("password_reset_request"),
            {
                "email": "unknown@example.com",
                "g-recaptcha-response": "test",
            },
        )
        # Should still redirect with success message (no enumeration)
        assert response.status_code == 302
        # Email should NOT be sent for unknown users
        assert not mock_send.called

    @patch("password_reset.views.send_password_reset")
    def test_request_creates_token(self, mock_send, client, verified_user):
        """Test request creates a password reset token."""
        initial_count = PasswordResetToken.objects.filter(user=verified_user).count()
        client.post(
            reverse("password_reset_request"),
            {
                "email": verified_user.email,
                "g-recaptcha-response": "test",
            },
        )
        new_count = PasswordResetToken.objects.filter(user=verified_user).count()
        assert new_count == initial_count + 1

    def test_request_invalid_email_format(self, client):
        """Test invalid email format shows form errors."""
        response = client.post(
            reverse("password_reset_request"),
            {"email": "not-an-email"},
        )
        assert response.status_code == 200
        assert "form" in response.context
        assert not response.context["form"].is_valid()


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Tests for password reset confirm view."""

    def test_confirm_invalid_token(self, client):
        """Test invalid token shows error page."""
        response = client.get(
            reverse("password_reset_confirm") + "?token=invalid_token"
        )
        assert response.status_code == 200
        assert "invalid" in response.templates[0].name

    def test_confirm_empty_token(self, client):
        """Test empty token shows error page."""
        response = client.get(reverse("password_reset_confirm"))
        assert response.status_code == 200
        assert "invalid" in response.templates[0].name

    def test_confirm_expired_token(self, client, expired_reset_token):
        """Test expired token shows error page."""
        _, raw_token = expired_reset_token
        response = client.get(
            reverse("password_reset_confirm") + f"?token={raw_token}"
        )
        assert response.status_code == 200
        assert "invalid" in response.templates[0].name

    def test_confirm_used_token(self, client, used_reset_token):
        """Test used token shows error page."""
        _, raw_token = used_reset_token
        response = client.get(
            reverse("password_reset_confirm") + f"?token={raw_token}"
        )
        assert response.status_code == 200
        assert "invalid" in response.templates[0].name

    def test_confirm_valid_token_shows_form(self, client, password_reset_token):
        """Test valid token shows password form."""
        _, raw_token = password_reset_token
        response = client.get(
            reverse("password_reset_confirm") + f"?token={raw_token}"
        )
        assert response.status_code == 200
        assert "form" in response.context

    def test_confirm_sets_new_password(self, client, password_reset_token):
        """Test confirming sets new password."""
        token_record, raw_token = password_reset_token
        user = token_record.user
        new_password = "NewSecurePass456$"

        response = client.post(
            reverse("password_reset_confirm"),
            {
                "token": raw_token,
                "new_password": new_password,
                "confirm_password": new_password,
                "g-recaptcha-response": "test",
            },
        )

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password(new_password)

    def test_confirm_marks_token_used(self, client, password_reset_token):
        """Test confirming marks token as used."""
        token_record, raw_token = password_reset_token
        new_password = "NewSecurePass456$"

        client.post(
            reverse("password_reset_confirm"),
            {
                "token": raw_token,
                "new_password": new_password,
                "confirm_password": new_password,
                "g-recaptcha-response": "test",
            },
        )

        token_record.refresh_from_db()
        assert token_record.used is True

    def test_confirm_password_mismatch(self, client, password_reset_token):
        """Test password mismatch shows error."""
        token_record, raw_token = password_reset_token

        response = client.post(
            reverse("password_reset_confirm"),
            {
                "token": raw_token,
                "new_password": "NewSecurePass456$",
                "confirm_password": "DifferentPass789$",
                "g-recaptcha-response": "test",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context
        token_record.refresh_from_db()
        assert token_record.used is False

    def test_confirm_weak_password(self, client, password_reset_token):
        """Test weak password shows validation error."""
        _, raw_token = password_reset_token

        response = client.post(
            reverse("password_reset_confirm"),
            {
                "token": raw_token,
                "new_password": "weak",
                "confirm_password": "weak",
                "g-recaptcha-response": "test",
            },
        )

        assert response.status_code == 200
        assert "form" in response.context


@pytest.mark.django_db
class TestPasswordResetTokenModel:
    """Tests for PasswordResetToken model."""

    def test_is_active_valid_token(self, password_reset_token):
        """Test is_active returns True for valid token."""
        token_record, _ = password_reset_token
        assert token_record.is_active() is True

    def test_is_active_expired_token(self, expired_reset_token):
        """Test is_active returns False for expired token."""
        token_record, _ = expired_reset_token
        assert token_record.is_active() is False

    def test_is_active_used_token(self, used_reset_token):
        """Test is_active returns False for used token."""
        token_record, _ = used_reset_token
        assert token_record.is_active() is False

    def test_str_representation(self, password_reset_token):
        """Test string representation of token."""
        token_record, _ = password_reset_token
        assert token_record.user.email in str(token_record)

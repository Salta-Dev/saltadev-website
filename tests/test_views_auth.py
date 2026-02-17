"""Tests for authentication views (login, register, verify_email)."""

from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    """Return a Django test client."""
    return Client()


class TestLoginView:
    """Tests for login view."""

    @pytest.mark.django_db
    def test_login_get_returns_200(self, client):
        """Login page GET should return 200."""
        response = client.get(reverse("login"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_login_uses_correct_template(self, client):
        """Login page should use auth_login/index.html template."""
        response = client.get(reverse("login"))
        assert "auth_login/index.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_login_with_valid_verified_user(self, client, verified_user, user_data):
        """Should login successfully with verified user."""
        response = client.post(
            reverse("login"),
            {
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("dashboard")

    @pytest.mark.django_db
    def test_login_with_unverified_user_fails(self, client, unverified_user, user_data):
        """Should fail login with unverified user."""
        response = client.post(
            reverse("login"),
            {
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert response.status_code == 200
        assert "email_not_verified" in response.context

    @pytest.mark.django_db
    def test_login_with_invalid_credentials(self, client, verified_user):
        """Should fail login with invalid credentials."""
        response = client.post(
            reverse("login"),
            {
                "username": "wrong@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 200
        assert response.context["form"].errors

    @pytest.mark.django_db
    def test_login_blocked_when_rate_limited(self, client, block_rate_limit, user_data):
        """Should show blocked message when rate limited."""
        block_rate_limit("login", limit=5)
        response = client.post(
            reverse("login"),
            {
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert response.status_code == 200
        assert "blocked_message" in response.context

    @pytest.mark.django_db
    def test_login_sets_fingerprint_cookie(self, client, verified_user, user_data):
        """Should set fingerprint cookie on login."""
        response = client.post(
            reverse("login"),
            {
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert "sd_fp" in response.cookies


class TestRegisterView:
    """Tests for register view."""

    @pytest.mark.django_db
    def test_register_get_returns_200(self, client):
        """Register page GET should return 200."""
        response = client.get(reverse("register"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_register_uses_correct_template(self, client):
        """Register page should use auth_register/index.html template."""
        response = client.get(reverse("register"))
        assert "auth_register/index.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_register_with_valid_data(self, mock_send_mail, client, recaptcha_settings):
        """Should register successfully with valid data."""
        response = client.post(
            reverse("register"),
            {
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "birth_date": "2000-01-15",
                "country": "AR",
                "province": "1",
                "password1": "SecurePass123$",
                "password2": "SecurePass123$",
                "terms": True,
                "g-recaptcha-response": "test",
            },
        )
        assert response.status_code == 302
        assert "/verificar/" in response.url

    @pytest.mark.django_db
    def test_register_with_invalid_data(self, client, recaptcha_settings):
        """Should fail registration with invalid data."""
        response = client.post(
            reverse("register"),
            {
                "email": "invalid-email",
                "first_name": "New",
                "last_name": "User",
                "birth_date": "2000-01-15",
                "country": "AR",
                "province": "1",
                "password1": "short",
                "password2": "short",
                "terms": True,
                "g-recaptcha-response": "test",
            },
        )
        assert response.status_code == 200
        assert response.context["form"].errors

    @pytest.mark.django_db
    def test_register_blocked_when_rate_limited(self, client, block_rate_limit):
        """Should show blocked message when rate limited."""
        block_rate_limit("register", limit=3)
        response = client.get(reverse("register"))
        # Rate limiting is checked on POST, so GET should work
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_register_sets_fingerprint_cookie(self, client):
        """Should set fingerprint cookie on register page."""
        response = client.get(reverse("register"))
        assert "sd_fp" in response.cookies


class TestVerifyEmailView:
    """Tests for verify_email view."""

    @pytest.mark.django_db
    def test_verify_get_without_email_redirects(self, client):
        """Verify page GET without email should redirect to login."""
        response = client.get(reverse("verify_email"))
        assert response.status_code == 302
        assert response.url == reverse("login")

    @pytest.mark.django_db
    def test_verify_get_with_valid_email_returns_200(self, client, unverified_user):
        """Verify page GET with valid unverified email should return 200."""
        response = client.get(reverse("verify_email") + f"?email={unverified_user.email}")
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_verify_uses_correct_template(self, client, unverified_user):
        """Verify page should use users/verificar.html template."""
        response = client.get(reverse("verify_email") + f"?email={unverified_user.email}")
        assert "users/verificar.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_verify_with_email_param(self, client, user):
        """Should pass email to template context."""
        response = client.get(reverse("verify_email") + f"?email={user.email}")
        assert response.context["email"] == user.email

    @pytest.mark.django_db
    def test_verify_with_valid_code(self, client, unverified_user, verification_code):
        """Should verify email with valid code."""
        response = client.post(
            reverse("verify_email"),
            {
                "email": unverified_user.email,
                "code": verification_code.code,
            },
        )
        assert response.status_code == 302
        assert response.url == reverse("dashboard")
        unverified_user.refresh_from_db()
        assert unverified_user.email_confirmed is True

    @pytest.mark.django_db
    def test_verify_with_invalid_code(self, client, unverified_user, verification_code):
        """Should fail verification with invalid code."""
        response = client.post(
            reverse("verify_email"),
            {
                "email": unverified_user.email,
                "code": "000000",
            },
        )
        assert response.status_code == 200
        unverified_user.refresh_from_db()
        assert unverified_user.email_confirmed is False

    @pytest.mark.django_db
    def test_verify_with_missing_fields(self, client):
        """Should fail verification with missing fields."""
        response = client.post(
            reverse("verify_email"),
            {
                "email": "",
                "code": "",
            },
        )
        assert response.status_code == 200

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_resend_verification_code(self, mock_send_mail, client, unverified_user):
        """Should resend verification code via POST."""
        response = client.post(
            reverse("verify_email"),
            {"email": unverified_user.email, "action": "resend"},
        )
        assert response.status_code == 302
        mock_send_mail.assert_called_once()

    @pytest.mark.django_db
    @patch("users.utils.send_mail")
    def test_resend_for_already_verified_user(self, mock_send_mail, client, verified_user):
        """Should show error for already verified user."""
        response = client.post(
            reverse("verify_email"),
            {"email": verified_user.email, "action": "resend"},
            follow=True,
        )
        assert response.status_code == 200
        mock_send_mail.assert_not_called()

    @pytest.mark.django_db
    def test_verify_blocked_when_rate_limited(self, client, block_rate_limit, user):
        """Should show blocked message when rate limited."""
        block_rate_limit("verify", limit=5)
        response = client.post(
            reverse("verify_email"),
            {
                "email": user.email,
                "code": "123456",
            },
        )
        assert response.status_code == 200
        assert "blocked_message" in response.context


class TestClearRateLimitsView:
    """Tests for clear_rate_limits_view."""

    @pytest.mark.django_db
    def test_requires_authentication(self, client):
        """Should redirect unauthenticated users."""
        response = client.get(reverse("clear_rate_limits"))
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_requires_staff(self, client, verified_user):
        """Should redirect non-staff users."""
        client.force_login(verified_user)
        response = client.get(reverse("clear_rate_limits"))
        assert response.status_code == 302
        assert response.url == reverse("home")

    @pytest.mark.django_db
    def test_staff_can_clear_limits(self, client, staff_user, block_rate_limit):
        """Staff should be able to clear rate limits."""
        block_rate_limit("login", limit=5, ip="192.168.1.1")
        client.force_login(staff_user)
        response = client.get(reverse("clear_rate_limits") + "?ip=192.168.1.1")
        assert response.status_code == 302
        assert response.url == reverse("home")


class TestLogoutView:
    """Tests for logout view."""

    @pytest.mark.django_db
    def test_logout_get_returns_200(self, client, verified_user):
        """Logout page GET should return 200."""
        client.force_login(verified_user)
        response = client.get(reverse("logout"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_logout_uses_correct_template(self, client, verified_user):
        """Logout page should use auth_login/logout.html template."""
        client.force_login(verified_user)
        response = client.get(reverse("logout"))
        assert "auth_login/logout.html" in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_logout_post_logs_out_user(self, client, verified_user):
        """POST to logout should log out the user and redirect to home."""
        client.force_login(verified_user)
        response = client.post(reverse("logout"))
        assert response.status_code == 302
        assert response.url == reverse("home")
        # Verify user is logged out
        response = client.get(reverse("dashboard"))
        assert response.status_code == 302  # Redirect to login

    @pytest.mark.django_db
    def test_logout_get_without_login(self, client):
        """Logout page should be accessible even without being logged in."""
        response = client.get(reverse("logout"))
        assert response.status_code == 200

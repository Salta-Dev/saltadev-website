"""Tests for Celery tasks."""

from unittest.mock import patch

import pytest
from django.core import mail

from users.tasks import send_password_reset_email_task, send_verification_email_task


@pytest.mark.django_db
class TestSendVerificationEmailTask:
    """Tests for send_verification_email_task."""

    def test_sends_email_successfully(self):
        """Task should send verification email with correct content."""
        send_verification_email_task(
            user_id=1,
            user_email="test@example.com",
            user_first_name="Test",
            code="123456",
            verify_url="http://localhost:8000/verificar/?email=test@example.com",
        )

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["test@example.com"]
        assert "Verifica tu email" in email.subject
        assert "123456" in email.body

    def test_email_contains_verification_url(self):
        """Task should include verification URL in email."""
        verify_url = "http://localhost:8000/verificar/?email=test@example.com"
        send_verification_email_task(
            user_id=1,
            user_email="test@example.com",
            user_first_name="Test",
            code="654321",
            verify_url=verify_url,
        )

        assert len(mail.outbox) == 1
        # URL should be in the HTML message
        assert verify_url in mail.outbox[0].alternatives[0][0]


@pytest.mark.django_db
class TestSendPasswordResetEmailTask:
    """Tests for send_password_reset_email_task."""

    def test_sends_email_successfully(self):
        """Task should send password reset email with correct content."""
        send_password_reset_email_task(
            user_id=1,
            user_email="test@example.com",
            user_first_name="Test",
            reset_link="http://localhost:8000/reset/abc123",
        )

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == ["test@example.com"]
        assert "Recuperación de contraseña" in email.subject

    def test_email_contains_reset_link(self):
        """Task should include reset link in email."""
        reset_link = "http://localhost:8000/reset/unique-token-123"
        send_password_reset_email_task(
            user_id=1,
            user_email="test@example.com",
            user_first_name="Test",
            reset_link=reset_link,
        )

        assert len(mail.outbox) == 1
        # Link should be in the HTML message
        assert reset_link in mail.outbox[0].alternatives[0][0]


@pytest.mark.django_db
class TestTaskConfiguration:
    """Tests for task configuration."""

    def test_verification_task_has_retry_config(self):
        """Verification task should be configured with retries."""
        assert send_verification_email_task.autoretry_for == (Exception,)
        assert send_verification_email_task.max_retries == 3
        assert send_verification_email_task.retry_backoff == 60

    def test_password_reset_task_has_retry_config(self):
        """Password reset task should be configured with retries."""
        assert send_password_reset_email_task.autoretry_for == (Exception,)
        assert send_password_reset_email_task.max_retries == 3
        assert send_password_reset_email_task.retry_backoff == 60

    def test_tasks_use_json_serialization(self, settings):
        """Tasks should use JSON serialization."""
        assert settings.CELERY_TASK_SERIALIZER == "json"
        assert settings.CELERY_RESULT_SERIALIZER == "json"

"""Tests for disposable email validation."""

import pytest
from django.core.exceptions import ValidationError

from users.validators import validate_not_disposable_email


class TestDisposableEmailValidator:
    """Tests for the validate_not_disposable_email function."""

    def test_rejects_temp_mail_org_domain(self):
        """Should reject emails from temp-mail.org."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("test@temp-mail.org")
        assert exc_info.value.code == "disposable_email"
        assert "temporales o desechables" in str(exc_info.value.message)

    def test_rejects_guerrillamail_domain(self):
        """Should reject emails from guerrillamail.com."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("user@guerrillamail.com")
        assert exc_info.value.code == "disposable_email"

    def test_rejects_mailinator_domain(self):
        """Should reject emails from mailinator.com."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("user@mailinator.com")
        assert exc_info.value.code == "disposable_email"

    def test_rejects_10minutemail_domain(self):
        """Should reject emails from 10minutemail.com."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("user@10minutemail.com")
        assert exc_info.value.code == "disposable_email"

    def test_accepts_gmail(self):
        """Should accept emails from gmail.com."""
        # Should not raise
        validate_not_disposable_email("user@gmail.com")

    def test_accepts_outlook(self):
        """Should accept emails from outlook.com."""
        validate_not_disposable_email("user@outlook.com")

    def test_accepts_hotmail(self):
        """Should accept emails from hotmail.com."""
        validate_not_disposable_email("user@hotmail.com")

    def test_accepts_yahoo(self):
        """Should accept emails from yahoo.com."""
        validate_not_disposable_email("user@yahoo.com")

    def test_accepts_corporate_domain(self):
        """Should accept emails from corporate domains."""
        validate_not_disposable_email("user@company.com")

    def test_case_insensitive_domain(self):
        """Should reject disposable emails regardless of case."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("user@MAILINATOR.COM")
        assert exc_info.value.code == "disposable_email"

    def test_mixed_case_domain(self):
        """Should handle mixed case domains."""
        with pytest.raises(ValidationError) as exc_info:
            validate_not_disposable_email("user@Guerrillamail.Com")
        assert exc_info.value.code == "disposable_email"

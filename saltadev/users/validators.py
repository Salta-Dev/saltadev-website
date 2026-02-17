"""Custom email validators."""

from disposable_email_domains import blocklist
from django.core.exceptions import ValidationError


def validate_not_disposable_email(email: str) -> None:
    """
    Validate that email is not from a disposable email provider.

    Args:
        email: The email address to validate.

    Raises:
        ValidationError: If the email domain is in the disposable domains blocklist.
    """
    domain = email.split("@")[-1].lower()
    if domain in blocklist:
        raise ValidationError(
            "No se permiten emails temporales o desechables.",
            code="disposable_email",
        )

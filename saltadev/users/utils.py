import hashlib
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from saltadev.logging import get_logger

from .models import EmailVerificationCode, User

logger = get_logger()

DEFAULT_LOCKOUT_MESSAGE = "Demasiados intentos fallidos. Intentá nuevamente más tarde."


def get_lockout_message() -> str:
    """Get the lockout message from settings or use default."""
    return getattr(settings, "AXES_LOCKOUT_MESSAGE", DEFAULT_LOCKOUT_MESSAGE)


def generate_verification_code() -> str:
    """Generate a random 6-digit numeric verification code."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def send_verification_code(user: User) -> None:
    """Invalidate existing codes and send a new verification email to the user."""
    EmailVerificationCode.objects.filter(user=user, used=False).update(used=True)
    code = generate_verification_code()
    EmailVerificationCode.objects.create(user=user, code=code)

    verify_url = f"{settings.SITE_URL}/verificar/?{urlencode({'email': user.email})}"
    html_message = render_to_string(
        "emails/verification.html",
        {
            "user": user,
            "code": code,
            "verify_url": verify_url,
            "site_url": settings.SITE_URL,
            "site_whatsapp": settings.SITE_WHATSAPP,
            "site_discord": settings.SITE_DISCORD,
            "site_github": settings.SITE_GITHUB,
            "site_linkedin": settings.SITE_LINKEDIN,
            "site_twitter": settings.SITE_TWITTER,
            "site_instagram": settings.SITE_INSTAGRAM,
        },
    )
    message = strip_tags(html_message)

    send_mail(
        subject="Verifica tu email - SaltaDev",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_message,
    )
    logger.info("Verification email sent", extra={"user_id": user.pk})


def verify_code(user: User, code: str) -> bool:
    """Validate a verification code and mark the user's email as confirmed.

    The code must:
    1. Exist and not be used
    2. Be the newest code for this user (prevents using old codes)
    3. Not be expired (24 hour limit)
    """
    # Find the code that matches
    code_record = (
        EmailVerificationCode.objects.filter(user=user, code=code, used=False)
        .order_by("-created_at")
        .first()
    )

    if code_record is None:
        return False

    # Check if expired (24 hours)
    if timezone.now() - code_record.created_at > timedelta(hours=24):
        return False

    # Check if this is the newest code for this user
    newest_code = (
        EmailVerificationCode.objects.filter(user=user, used=False)
        .order_by("-created_at")
        .first()
    )

    if newest_code is None or newest_code.pk != code_record.pk:
        return False

    # All checks passed - mark ALL codes as used and confirm email
    EmailVerificationCode.objects.filter(user=user, used=False).update(used=True)

    user.email_confirmed = True
    user.save()
    logger.info("Email verified in utils", extra={"user_id": user.pk})

    return True


def generate_reset_token() -> str:
    """Generate a cryptographically secure URL-safe password reset token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of a token for secure storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_password_reset_token(user: User, expires_minutes: int = 10) -> str:
    """Create a new password reset token, invalidating any existing ones."""
    from password_reset.models import PasswordResetToken

    PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

    token = generate_reset_token()
    PasswordResetToken.objects.create(
        user=user,
        token_hash=hash_token(token),
        expires_at=timezone.now() + timedelta(minutes=expires_minutes),
    )
    logger.info("Password reset token created", extra={"user_id": user.pk})
    return token


def send_password_reset(user: User, reset_link: str) -> None:
    """Send a password reset email containing the given reset link."""
    html_message = render_to_string(
        "emails/password_reset.html",
        {
            "user": user,
            "reset_link": reset_link,
            "site_url": settings.SITE_URL,
            "site_whatsapp": settings.SITE_WHATSAPP,
            "site_discord": settings.SITE_DISCORD,
            "site_github": settings.SITE_GITHUB,
            "site_linkedin": settings.SITE_LINKEDIN,
            "site_twitter": settings.SITE_TWITTER,
            "site_instagram": settings.SITE_INSTAGRAM,
        },
    )
    message = strip_tags(html_message)

    send_mail(
        subject="Recuperación de contraseña - SaltaDev",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_message,
    )
    logger.info("Password reset email sent", extra={"user_id": user.pk})

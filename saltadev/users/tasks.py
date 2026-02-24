"""
Celery tasks for user-related async operations.

Tasks for sending emails asynchronously (verification codes, password resets).
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from saltadev.logging import get_logger

logger = get_logger()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    max_retries=3,
)
def send_verification_email_task(
    self,
    user_id: int,
    user_email: str,
    user_first_name: str,
    code: str,
    verify_url: str,
) -> None:
    """Send verification email asynchronously.

    Args:
        self: Task instance (for retries).
        user_id: User's primary key for logging.
        user_email: Recipient email address.
        user_first_name: User's first name for personalization.
        code: 6-digit verification code.
        verify_url: URL for email verification page.
    """
    html_message = render_to_string(
        "emails/verification.html",
        {
            "user": {"first_name": user_first_name, "email": user_email},
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
        recipient_list=[user_email],
        fail_silently=False,
        html_message=html_message,
    )
    logger.info("Verification email sent (async)", extra={"user_id": user_id})


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    max_retries=3,
)
def send_password_reset_email_task(
    self,
    user_id: int,
    user_email: str,
    user_first_name: str,
    reset_link: str,
) -> None:
    """Send password reset email asynchronously.

    Args:
        self: Task instance (for retries).
        user_id: User's primary key for logging.
        user_email: Recipient email address.
        user_first_name: User's first name for personalization.
        reset_link: URL for password reset page.
    """
    html_message = render_to_string(
        "emails/password_reset.html",
        {
            "user": {"first_name": user_first_name, "email": user_email},
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
        recipient_list=[user_email],
        fail_silently=False,
        html_message=html_message,
    )
    logger.info("Password reset email sent (async)", extra={"user_id": user_id})

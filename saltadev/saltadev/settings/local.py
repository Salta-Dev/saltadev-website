"""
Local development settings.

Uses SQLite, DEBUG=True, relaxed security.
"""

from pathlib import Path

from dotenv import load_dotenv

# Load environment variables BEFORE importing base settings
env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
load_dotenv(env_path)

from .base import *  # noqa: F403, E402

DEBUG = True

SECRET_KEY = "django-insecure-local-development-key-do-not-use-in-production"  # pragma: allowlist secret

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".ngrok-free.app", ".ngrok.io"]

# Allow ngrok for CSRF (needed for form submissions)
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Uncomment above to print emails to console instead of sending them

# reCAPTCHA test keys for local development (Google's official test keys)
# https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do
RECAPTCHA_PUBLIC_KEY = (
    "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"  # pragma: allowlist secret
)
RECAPTCHA_PRIVATE_KEY = (
    "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"  # pragma: allowlist secret
)

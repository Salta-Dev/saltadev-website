"""
Local development settings.

Uses DATABASE_URL (PostgreSQL via Docker), DEBUG=True, relaxed security.
Falls back to SQLite if DATABASE_URL is not set.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Load environment variables BEFORE importing base settings
env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
load_dotenv(env_path)

from .base import *  # noqa: F403, E402

DEBUG = True

SECRET_KEY = "django-insecure-local-development-key-do-not-use-in-production"  # pragma: allowlist secret

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", ".ngrok-free.app", ".ngrok.io"]  # nosec B104

# Allow ngrok for CSRF (needed for form submissions)
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]

# Database: use DATABASE_URL if set, otherwise SQLite for quick runs without Docker
if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default="postgresql://saltadev:saltadev@localhost:5432/saltadev_local",  # pragma: allowlist secret
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),  # noqa: F405
        }
    }

# Cache: use Redis if REDIS_URL is available, otherwise LocMem
if os.getenv("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
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

"""
Development environment settings.

Uses PostgreSQL, DEBUG=True, WhiteNoise for static files.
Configured for deployment on Render.com.
"""

import os

import dj_database_url  # type: ignore[import-not-found]

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",  # Render domains
]

# Database: use DATABASE_URL if available, fallback to individual env vars
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default="postgresql://localhost:5432/saltadev_dev",
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "saltadev_dev"),
            "USER": os.getenv("POSTGRES_USER", "saltadev_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

# CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

# WhiteNoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

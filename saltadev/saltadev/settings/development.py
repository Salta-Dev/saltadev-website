"""
Development environment settings.

Uses DATABASE_URL (PostgreSQL), Redis, Cloudinary, DEBUG=True.
Deployed on Render.com.
"""

import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",  # Docker  # nosec B104
    ".onrender.com",  # Render domains
]

# Database: PostgreSQL via DATABASE_URL (required)
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
    )
}

# CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

# WhiteNoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# Cloudinary for media storage
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Redis cache (required)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
    }
}

# Celery: use Redis as broker
CELERY_BROKER_URL = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND = os.environ["REDIS_URL"]

"""
Base Django settings for saltadev project.

Common settings shared across all environments.
Environment-specific settings are in local.py, development.py, staging.py, production.py.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "")

ALLOWED_HOSTS: list[str] = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "cloudinary",
    "cloudinary_storage",
    "home",
    "events",
    "code_of_conduct",
    "auth_login",
    "auth_register",
    "users",
    "content",
    "locations",
    "password_reset",
    "dashboard",
    "benefits",
    "django_recaptcha",
    "axes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "saltadev.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "content.context_processors.site_links",
            ],
        },
    },
]

WSGI_APPLICATION = "saltadev.wsgi.application"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [
    "username",
    "ip_address",
]
AXES_USERNAME_FORM_FIELD = "username"
AXES_LOCKOUT_MESSAGE = "Demasiados intentos fallidos. Fuiste bloqueado por 1 hora después de 5 intentos. Intentá nuevamente más tarde."
AXES_LOCKOUT_TEMPLATE = "registration/axes_lockout.html"


# Internationalization

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Salta"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

# Email configuration (Gmail SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")

SITE_WHATSAPP = os.getenv(
    "SITE_WHATSAPP", "https://chat.whatsapp.com/Jv02aqrmzXK6wwuRELp9zs"
)
SITE_DISCORD = os.getenv("SITE_DISCORD", "https://discord.gg/kqzWbStGQ6")
SITE_GITHUB = os.getenv("SITE_GITHUB", "https://github.com/Salta-Dev")
SITE_LINKEDIN = os.getenv("SITE_LINKEDIN", "https://www.linkedin.com/company/saltadev/")
SITE_TWITTER = os.getenv("SITE_TWITTER", "https://x.com/SaltaDevAr")
SITE_INSTAGRAM = os.getenv("SITE_INSTAGRAM", "https://www.instagram.com/salta.dev.ar/")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# reCAPTCHA configuration
RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_V2_SECRET", "tu-secret-key")
RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_V2_SITE_KEY", "tu-site-key")

# Cloudinary configuration for image uploads
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET", ""),
}

SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

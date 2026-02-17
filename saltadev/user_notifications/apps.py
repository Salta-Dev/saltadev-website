"""User notifications app configuration."""

from django.apps import AppConfig


class UserNotificationsConfig(AppConfig):
    """Configuration for the user_notifications app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "user_notifications"
    verbose_name = "Notificaciones de Usuario"

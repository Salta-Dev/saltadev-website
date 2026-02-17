"""Django app configuration for content app."""

from django.apps import AppConfig


class ContentConfig(AppConfig):
    """Configuration for the content app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "content"

    def ready(self) -> None:
        """Import signals when the app is ready."""
        import content.signals  # noqa: F401

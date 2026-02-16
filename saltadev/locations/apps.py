"""Locations app configuration."""

from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """Configuration for the locations app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "locations"
    verbose_name = "Ubicaciones"

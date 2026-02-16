"""Admin configuration for locations app."""

from django.contrib import admin

from .models import Country, Province


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin for Country model."""

    list_display = ["code", "name"]  # noqa: RUF012
    search_fields = ["code", "name"]  # noqa: RUF012
    ordering = ["name"]  # noqa: RUF012


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """Admin for Province model."""

    list_display = ["name", "code", "country"]  # noqa: RUF012
    list_filter = ["country"]  # noqa: RUF012
    search_fields = ["name", "code"]  # noqa: RUF012
    ordering = ["country", "name"]  # noqa: RUF012

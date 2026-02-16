"""Admin configuration for benefits."""

from django.contrib import admin

from .models import Benefit


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    """Admin configuration for Benefit model."""

    list_display = (
        "title",
        "creator",
        "benefit_type",
        "modality",
        "is_active",
        "is_expired",
        "created_at",
    )
    list_filter = (
        "benefit_type",
        "modality",
        "is_active",
        "contact_source",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "creator__first_name",
        "creator__last_name",
        "creator__email",
    )
    readonly_fields = ("created_at", "updated_at", "redemption_count")
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("title", "description", "image", "is_active"),
            },
        ),
        (
            "Tipo y detalles",
            {
                "fields": (
                    "benefit_type",
                    "discount_percentage",
                    "redemption_limit",
                    "redemption_count",
                    "discount_codes",
                ),
            },
        ),
        (
            "Validez",
            {
                "fields": ("expiration_date",),
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "contact_source",
                    "contact_phone",
                    "contact_email",
                    "contact_website",
                ),
            },
        ),
        (
            "Modalidad y ubicación",
            {
                "fields": ("modality", "location"),
            },
        ),
        (
            "Metadatos",
            {
                "fields": ("creator", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

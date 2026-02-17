"""Django admin configuration for User and Profile models."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "email_confirmed",
        "is_active",
    )
    list_filter = ("role", "is_active", "email_confirmed")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-registered_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Información personal",
            {"fields": ("first_name", "last_name", "birth_date")},
        ),
        (
            "Rol y permisos",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Estado",
            {"fields": ("email_confirmed", "registered_at", "last_login")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "technical_role", "location", "company", "available")
    search_fields = ("user__email", "user__first_name", "location", "company")
    list_filter = ("technical_role", "available")


admin.site.register(User, UserAdmin)

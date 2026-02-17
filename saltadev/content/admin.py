from django.contrib import admin

from .models import Collaborator, Event, StaffProfile


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date_display", "event_time_display", "location")
    search_fields = ("title", "location")
    list_filter = ("event_date_display",)


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("name", "link")
    search_fields = ("name",)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin configuration for StaffProfile with dual photo upload options."""

    list_display = ("user", "role", "order", "has_photo")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_editable = ("order",)
    fieldsets = (
        (None, {"fields": ("user", "role", "bio", "order")}),
        (
            "Foto de perfil",
            {
                "description": "Podés subir una foto desde tu PC o pegar una URL. "
                "Si usás ambas, la foto subida tiene prioridad.",
                "fields": ("photo_file", "photo_url"),
            },
        ),
        (
            "Redes sociales y sitio web",
            {"fields": ("linkedin", "github", "twitter", "instagram", "website")},
        ),
    )

    @admin.display(boolean=True, description="Foto")
    def has_photo(self, obj: StaffProfile) -> bool:
        """Return True if the staff member has a photo."""
        return bool(obj.photo_file or obj.photo_url)

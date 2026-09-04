from collections.abc import Sequence
from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from django.http import HttpRequest
from users.models import User

from .models import (
    CatalogEntry,
    Collaborator,
    Event,
    LearningResource,
    StaffProfile,
    TechSpecialty,
)


def _can_manage_learning_resources(user: User | AnonymousUser) -> bool:
    """Return True for Django superusers or SaltaDev administrators."""
    if not user.is_authenticated:
        return False
    return bool(
        user.is_superuser or (user.is_staff and user.role == User.Role.ADMINISTRADOR)
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "kind",
        "status",
        "creator",
        "event_date_display",
        "event_time_display",
        "location",
    )
    search_fields = ("title", "location")
    list_filter = ("status", "kind", "event_date_display")
    raw_id_fields = ("creator", "approved_by")


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    """Admin configuration for Collaborator with dual image upload options."""

    list_display = ("name", "link", "has_image")
    search_fields = ("name",)
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "link")}),
        (
            "Imagen",
            {
                "description": "Podés subir una imagen desde tu PC o pegar una URL. "
                "Si usás ambas, la imagen subida tiene prioridad.",
                "fields": ("image_file", "image_url"),
            },
        ),
    )

    @admin.display(boolean=True, description="Imagen")
    def has_image(self, obj: Collaborator) -> bool:
        """Return True if the collaborator has an image."""
        return bool(obj.image_file or obj.image_url)


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


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    """Admin for courses and tips shown on /recursos/."""

    list_display = (
        "title",
        "track",
        "duration",
        "instructor",
        "source",
        "order",
        "is_published",
    )
    list_filter = ("track", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "tip", "source")
    ordering = ("track", "order", "created_at")

    def has_module_permission(self, request: HttpRequest) -> bool:
        """Hide the module from staff who are not administrators."""
        return _can_manage_learning_resources(request.user)

    def has_view_permission(
        self, request: HttpRequest, obj: LearningResource | None = None
    ) -> bool:
        """Only administrators can see the catalog in admin."""
        return _can_manage_learning_resources(request.user)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Only administrators can add courses."""
        return _can_manage_learning_resources(request.user)

    def has_change_permission(
        self, request: HttpRequest, obj: LearningResource | None = None
    ) -> bool:
        """Only administrators can edit courses."""
        return _can_manage_learning_resources(request.user)

    def has_delete_permission(
        self, request: HttpRequest, obj: LearningResource | None = None
    ) -> bool:
        """Only administrators can delete courses."""
        return _can_manage_learning_resources(request.user)


@admin.register(TechSpecialty)
class TechSpecialtyAdmin(admin.ModelAdmin):
    """Admin for IT roles shown on /recursos/especialidades/."""

    list_display = ("title", "family", "order", "is_published")
    list_filter = ("family", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "summary", "stack")
    fields = (
        "title",
        "slug",
        "family",
        "icon",
        "summary",
        "stack",
        "audience",
        "sections",
        "order",
        "is_published",
    )
    prepopulated_fields: ClassVar[dict[str, Sequence[str]]] = {"slug": ("title",)}
    ordering = ("family", "order", "title")

    def has_module_permission(self, request: HttpRequest) -> bool:
        """Hide the module from staff who are not administrators."""
        return _can_manage_learning_resources(request.user)

    def has_view_permission(
        self, request: HttpRequest, obj: TechSpecialty | None = None
    ) -> bool:
        """Only administrators can see specialties in admin."""
        return _can_manage_learning_resources(request.user)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Only administrators can add specialties."""
        return _can_manage_learning_resources(request.user)

    def has_change_permission(
        self, request: HttpRequest, obj: TechSpecialty | None = None
    ) -> bool:
        """Only administrators can edit specialties."""
        return _can_manage_learning_resources(request.user)

    def has_delete_permission(
        self, request: HttpRequest, obj: TechSpecialty | None = None
    ) -> bool:
        """Only administrators can delete specialties."""
        return _can_manage_learning_resources(request.user)


@admin.register(CatalogEntry)
class CatalogEntryAdmin(admin.ModelAdmin):
    """Admin for books, tools and projects on the Recursos hub."""

    list_display = ("title", "kind", "status", "creator", "order", "is_published")
    list_filter = ("kind", "status", "is_published", "category")
    list_editable = ("order", "is_published")
    search_fields = ("title", "summary", "authors", "tags")
    raw_id_fields = ("creator", "approved_by")
    actions = ("approve_entries",)
    ordering = ("kind", "order", "title")

    @admin.action(description="Aprobar ítems seleccionados")
    def approve_entries(
        self, request: HttpRequest, queryset: QuerySet[CatalogEntry]
    ) -> None:
        """Publish pending community catalog submissions."""
        if not request.user.is_authenticated or request.user.pk is None:
            return

        approver = User.objects.get(pk=request.user.pk)
        pending = queryset.filter(status=CatalogEntry.Status.PENDING)
        for entry in pending:
            entry.approve(approver)

    def has_module_permission(self, request: HttpRequest) -> bool:
        """Hide the module from staff who are not administrators."""
        return _can_manage_learning_resources(request.user)

    def has_view_permission(
        self, request: HttpRequest, obj: CatalogEntry | None = None
    ) -> bool:
        """Only administrators can see catalog entries."""
        return _can_manage_learning_resources(request.user)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Only administrators can add catalog entries."""
        return _can_manage_learning_resources(request.user)

    def has_change_permission(
        self, request: HttpRequest, obj: CatalogEntry | None = None
    ) -> bool:
        """Only administrators can edit catalog entries."""
        return _can_manage_learning_resources(request.user)

    def has_delete_permission(
        self, request: HttpRequest, obj: CatalogEntry | None = None
    ) -> bool:
        """Only administrators can delete catalog entries."""
        return _can_manage_learning_resources(request.user)

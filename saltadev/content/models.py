from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from users.models import User


class Event(models.Model):
    """Community event with date, location, and registration link."""

    class Status(models.TextChoices):
        """Event approval status."""

        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        REJECTED = "rejected", "Rechazado"

    title = models.CharField(max_length=200, verbose_name="título")
    description = models.TextField(blank=True, verbose_name="descripción")
    location = models.CharField(max_length=200, blank=True, verbose_name="ubicación")
    photo = models.URLField(max_length=500, blank=True, verbose_name="imagen")
    link = models.URLField(blank=True, verbose_name="link de registro")
    event_start_date = models.DateTimeField(
        null=True, blank=True, verbose_name="fecha de inicio"
    )
    event_end_date = models.DateTimeField(
        null=True, blank=True, verbose_name="fecha de fin"
    )
    event_date_display = models.CharField(
        max_length=30, blank=True, verbose_name="fecha a mostrar"
    )
    event_time_display = models.CharField(
        max_length=30, blank=True, verbose_name="hora a mostrar"
    )
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="creado")

    # New fields for user-created events
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        verbose_name="creador",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPROVED,
        verbose_name="estado",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_events",
        verbose_name="aprobado por",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="fecha de aprobación"
    )

    class Meta:
        verbose_name = "evento"
        verbose_name_plural = "eventos"
        ordering = ("-event_start_date",)

    def __str__(self) -> str:
        return self.title

    @property
    def is_pending(self) -> bool:
        """Check if event is pending approval."""
        return self.status == self.Status.PENDING

    @property
    def is_approved(self) -> bool:
        """Check if event is approved."""
        return self.status == self.Status.APPROVED

    def can_edit(self, user: "User") -> bool:
        """Check if user can edit this event."""
        if user.is_superuser or user.role in ["administrador", "moderador"]:
            return True
        return self.creator == user

    def can_approve(self, user: "User") -> bool:
        """Check if user can approve/reject this event."""
        return user.is_superuser or user.role in ["administrador", "moderador"]


class Collaborator(models.Model):
    """Organization or company that collaborates with the SaltaDev community."""

    name = models.CharField(max_length=150)
    image = models.CharField(max_length=300, blank=True)
    link = models.URLField(blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name


class StaffProfile(models.Model):
    """Public profile for SaltaDev staff members displayed on the homepage."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    role = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo = models.CharField(max_length=300, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.user.email

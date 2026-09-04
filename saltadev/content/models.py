from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db import models
from django.urls import reverse
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

    class Kind(models.TextChoices):
        """Public-facing type shown as a badge on event cards."""

        MEETUP = "meetup", "Meetup"
        TALK = "talk", "Charla"
        WORKSHOP = "workshop", "Taller"
        HACKATHON = "hackathon", "Hackatón"
        SOCIAL = "social", "Social"

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
    slug = models.SlugField(max_length=255, unique=True)
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
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        default=Kind.MEETUP,
        verbose_name="tipo",
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
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["creator"]),
            models.Index(fields=["event_start_date"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Return the public detail URL for this event."""
        return reverse("event_detail", kwargs={"slug": self.slug})

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

    @property
    def is_online(self) -> bool:
        """Return True when the venue reads as virtual."""
        location = (self.location or "").casefold()
        markers = ("online", "virtual", "remoto", "remote", "zoom", "meet", "discord")
        return any(marker in location for marker in markers)

    @property
    def modality_label(self) -> str:
        """Return Presencial/Online when a location exists."""
        if not self.location:
            return ""
        return "Online" if self.is_online else "Presencial"

    @property
    def kind_icon(self) -> str:
        """Return the Material icon name for this event kind."""
        icons: dict[str, str] = {
            self.Kind.MEETUP: "groups",
            self.Kind.TALK: "campaign",
            self.Kind.WORKSHOP: "school",
            self.Kind.HACKATHON: "terminal",
            self.Kind.SOCIAL: "local_cafe",
        }
        return icons.get(self.kind, "event")


class Collaborator(models.Model):
    """Organization or company that collaborates with the SaltaDev community."""

    name = models.CharField(max_length=150, verbose_name="nombre")
    image_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="imagen (URL)",
        help_text="URL externa de la imagen",
    )
    image_file = models.ImageField(
        upload_to="partners/",
        blank=True,
        null=True,
        verbose_name="imagen",
        help_text="Subir imagen desde tu computadora",
    )
    link = models.URLField(blank=True, verbose_name="sitio web")
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="creado")

    class Meta:
        verbose_name = "colaborador"
        verbose_name_plural = "colaboradores"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @property
    def image(self) -> str:
        """Return the image URL, prioritizing uploaded file over external URL."""
        if self.image_file:
            return self.image_file.url
        return self.image_url


class StaffProfile(models.Model):
    """Public profile for SaltaDev staff members displayed on the homepage."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    role = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="foto (URL)",
        help_text="URL externa de la imagen",
    )
    photo_file = models.ImageField(
        upload_to="staff/",
        blank=True,
        null=True,
        verbose_name="foto",
        help_text="Subir imagen desde tu computadora",
    )
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    github = models.URLField(blank=True, verbose_name="GitHub")
    twitter = models.URLField(blank=True, verbose_name="Twitter/X")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    website = models.URLField(blank=True, verbose_name="sitio web")
    order = models.PositiveIntegerField(default=0, verbose_name="orden")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "perfil de staff"
        verbose_name_plural = "perfiles de staff"
        ordering = ("order",)

    def __str__(self) -> str:
        return self.user.email

    @property
    def photo(self) -> str:
        """Return the photo URL, prioritizing uploaded file over external URL."""
        if self.photo_file:
            return self.photo_file.url
        return self.photo_url


class LearningResource(models.Model):
    """Course or tip shown on /recursos/, managed by administrators."""

    class Track(models.TextChoices):
        """Audience track on the public catalog."""

        DEVELOPERS = "developers", "Developers"
        VIBECODERS = "vibecoders", "Vibecoders"

    class Status(models.TextChoices):
        """Moderation state for community-submitted courses."""

        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        REJECTED = "rejected", "Rechazado"

    title = models.CharField(max_length=200, verbose_name="título")
    tip = models.TextField(verbose_name="tip")
    url = models.URLField(verbose_name="enlace")
    source = models.CharField(max_length=80, blank=True, verbose_name="fuente")
    duration = models.CharField(max_length=40, blank=True, verbose_name="duración")
    instructor = models.CharField(
        max_length=160, blank=True, verbose_name="dictado por"
    )
    track = models.CharField(
        max_length=20,
        choices=Track.choices,
        verbose_name="pista",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPROVED,
        verbose_name="estado",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learning_resources",
        verbose_name="creador",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_learning_resources",
        verbose_name="aprobado por",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="fecha de aprobación"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="motivo de rechazo")
    order = models.PositiveIntegerField(default=0, verbose_name="orden")
    is_published = models.BooleanField(default=True, verbose_name="publicado")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "curso / tip"
        verbose_name_plural = "cursos y tips"
        ordering = ("track", "order", "created_at")
        indexes = [
            models.Index(fields=["is_published", "track", "order"]),
            models.Index(fields=["status", "is_published"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_pending(self) -> bool:
        """Return True when the course waits for reviewer action."""
        return self.status == self.Status.PENDING

    def approve(self, user: "User") -> None:
        """Mark a submitted course as public."""
        self.status = self.Status.APPROVED
        self.is_published = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = ""
        self.save(
            update_fields=[
                "status",
                "is_published",
                "approved_by",
                "approved_at",
                "rejection_reason",
            ]
        )

    def reject(self, user: "User", reason: str = "") -> None:
        """Decline a submitted course without deleting it."""
        self.status = self.Status.REJECTED
        self.is_published = False
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = reason.strip()
        self.save(
            update_fields=[
                "status",
                "is_published",
                "approved_by",
                "approved_at",
                "rejection_reason",
            ]
        )


class TechSpecialty(models.Model):
    """IT role shown on /recursos/especialidades/, managed by administrators."""

    class Family(models.TextChoices):
        """Grouping used on the public specialties page."""

        DEVELOPMENT = "development", "Desarrollo"
        DATA = "data", "Datos e IA"
        OPERATIONS = "operations", "Operaciones y calidad"
        DESIGN = "design", "Diseño"
        PRODUCT = "product", "Producto"
        LEADERSHIP = "leadership", "Liderazgo"

    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=120, verbose_name="título")
    summary = models.TextField(verbose_name="qué hace")
    stack = models.TextField(
        blank=True,
        verbose_name="tecnologías",
        help_text="Una tecnología por línea. Se muestran como chips.",
    )
    audience = models.TextField(blank=True, verbose_name="para quién")
    family = models.CharField(
        max_length=20,
        choices=Family.choices,
        verbose_name="familia",
    )
    icon = models.CharField(max_length=40, default="layers", verbose_name="ícono")
    sections = models.JSONField(
        default=list,
        blank=True,
        verbose_name="secciones",
        help_text='Lista de {"heading": "...", "items": ["...", "..."]}.',
    )
    order = models.PositiveIntegerField(default=0, verbose_name="orden")
    is_published = models.BooleanField(default=True, verbose_name="publicado")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "especialidad"
        verbose_name_plural = "especialidades"
        ordering = ("family", "order", "title")
        indexes = [
            models.Index(fields=["is_published", "family", "order"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def stack_items(self) -> list[str]:
        """Return technologies as a list of non-empty lines."""
        return [line.strip() for line in self.stack.splitlines() if line.strip()]

    @property
    def section_list(self) -> list[dict[str, Any]]:
        """Return validated heading/items blocks for the public role sheet."""
        raw = self.sections
        if not isinstance(raw, list):
            return []
        blocks: list[dict[str, Any]] = []
        for block in raw:
            if not isinstance(block, dict):
                continue
            heading = str(block.get("heading") or "").strip()
            items = block.get("items") or []
            if not heading or not isinstance(items, list):
                continue
            cleaned = [str(item).strip() for item in items if str(item).strip()]
            if cleaned:
                blocks.append({"heading": heading, "items": cleaned})
        return blocks


class CatalogEntry(models.Model):
    """Book, tool or community project shown on the Recursos hub."""

    class Kind(models.TextChoices):
        """Which Recursos tab this entry belongs to."""

        READING = "reading", "Lectura"
        TOOL = "tool", "Herramienta"
        PROJECT = "project", "Proyecto"

    class Status(models.TextChoices):
        """Moderation state for community-submitted projects."""

        PENDING = "pending", "Pendiente"
        APPROVED = "approved", "Aprobado"
        REJECTED = "rejected", "Rechazado"

    kind = models.CharField(max_length=20, choices=Kind.choices, verbose_name="tipo")
    title = models.CharField(max_length=200, verbose_name="título")
    summary = models.TextField(verbose_name="descripción")
    url = models.URLField(blank=True, verbose_name="enlace")
    category = models.CharField(max_length=80, blank=True, verbose_name="categoría")
    authors = models.CharField(max_length=200, blank=True, verbose_name="autores")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="año")
    pricing = models.CharField(max_length=40, blank=True, verbose_name="precio")
    tags = models.TextField(
        blank=True,
        verbose_name="etiquetas",
        help_text="Una etiqueta por línea.",
    )
    stack = models.TextField(
        blank=True,
        verbose_name="stack",
        help_text="Una tecnología por línea. Útil en proyectos.",
    )
    extra = models.CharField(max_length=80, blank=True, verbose_name="sello")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPROVED,
        verbose_name="estado",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catalog_entries",
        verbose_name="creador",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_catalog_entries",
        verbose_name="aprobado por",
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name="fecha de aprobación"
    )
    rejection_reason = models.TextField(blank=True, verbose_name="motivo de rechazo")
    order = models.PositiveIntegerField(default=0, verbose_name="orden")
    is_published = models.BooleanField(default=True, verbose_name="publicado")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "ítem de catálogo"
        verbose_name_plural = "ítems de catálogo"
        ordering = ("kind", "order", "title")
        indexes = [
            models.Index(fields=["kind", "is_published", "order"]),
            models.Index(fields=["kind", "status"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_pending(self) -> bool:
        """Return True when the entry waits for administrator review."""
        return self.status == self.Status.PENDING

    def approve(self, user: "User") -> None:
        """Mark a submitted project as public."""
        self.status = self.Status.APPROVED
        self.is_published = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = ""
        self.save(
            update_fields=[
                "status",
                "is_published",
                "approved_by",
                "approved_at",
                "rejection_reason",
            ]
        )

    def reject(self, user: "User", reason: str = "") -> None:
        """Decline a submitted catalog entry without deleting it."""
        self.status = self.Status.REJECTED
        self.is_published = False
        self.approved_by = user
        self.approved_at = timezone.now()
        self.rejection_reason = reason.strip()
        self.save(
            update_fields=[
                "status",
                "is_published",
                "approved_by",
                "approved_at",
                "rejection_reason",
            ]
        )

    @property
    def tag_items(self) -> list[str]:
        """Return tags as a list of non-empty lines."""
        return [line.strip() for line in self.tags.splitlines() if line.strip()]

    @property
    def stack_items(self) -> list[str]:
        """Return project technologies as a list of non-empty lines."""
        return [line.strip() for line in self.stack.splitlines() if line.strip()]

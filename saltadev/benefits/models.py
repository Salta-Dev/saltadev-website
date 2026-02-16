"""Benefits models for the SaltaDev community."""

from django.db import models
from django.utils import timezone
from users.models import User


class Benefit(models.Model):
    """
    Benefit model representing discounts, promotions, or redeemable offers.

    Benefits can be created by collaborators, moderators, and administrators.
    Only the creator can edit/delete their own benefits (collaborators),
    while moderators and administrators can manage all benefits.
    """

    class BenefitType(models.TextChoices):
        """Type of benefit offered."""

        REDEEMABLE = "redeemable", "Canjeable"
        DISCOUNT = "discount", "Descuento"

    class Modality(models.TextChoices):
        """Whether the benefit is virtual or in-person."""

        VIRTUAL = "virtual", "Virtual"
        IN_PERSON = "in_person", "Presencial"
        BOTH = "both", "Virtual y Presencial"

    class ContactSource(models.TextChoices):
        """Source of contact information."""

        USER_PROFILE = "user_profile", "Usar datos de mi perfil"
        CUSTOM = "custom", "Ingresar manualmente"

    # Basic information
    title = models.CharField(
        max_length=200,
        verbose_name="título",
    )
    description = models.TextField(
        verbose_name="descripción",
    )
    image = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="imagen",
        help_text="URL de la imagen del beneficio",
    )

    # Benefit type and details
    benefit_type = models.CharField(
        max_length=20,
        choices=BenefitType.choices,
        default=BenefitType.DISCOUNT,
        verbose_name="tipo de beneficio",
    )
    redemption_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="límite de canjes",
        help_text="Cantidad máxima de veces que se puede canjear (dejar vacío para ilimitado)",
    )
    redemption_count = models.PositiveIntegerField(
        default=0,
        verbose_name="canjes realizados",
    )
    discount_percentage = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="porcentaje de descuento",
        help_text="Porcentaje de descuento (1-100)",
    )

    # Validity
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de expiración",
    )

    # Contact information
    contact_source = models.CharField(
        max_length=20,
        choices=ContactSource.choices,
        default=ContactSource.USER_PROFILE,
        verbose_name="fuente de contacto",
    )
    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="teléfono de contacto",
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name="email de contacto",
    )
    contact_website = models.URLField(
        max_length=300,
        blank=True,
        verbose_name="sitio web",
    )

    # Modality and location
    modality = models.CharField(
        max_length=20,
        choices=Modality.choices,
        default=Modality.VIRTUAL,
        verbose_name="modalidad",
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="ubicación",
        help_text="Dirección física donde se puede utilizar el beneficio",
    )

    # Discount codes
    discount_codes = models.TextField(
        blank=True,
        verbose_name="códigos de descuento",
        help_text="Códigos de descuento separados por comas",
    )

    # Metadata
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="benefits",
        verbose_name="creador",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="última actualización",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        verbose_name = "beneficio"
        verbose_name_plural = "beneficios"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Return string representation of the benefit."""
        return self.title

    @property
    def is_expired(self) -> bool:
        """Check if the benefit has expired."""
        if self.expiration_date is None:
            return False
        return self.expiration_date < timezone.now().date()

    @property
    def is_fully_redeemed(self) -> bool:
        """Check if the benefit has reached its redemption limit."""
        if self.redemption_limit is None:
            return False
        return self.redemption_count >= self.redemption_limit

    @property
    def is_available(self) -> bool:
        """Check if the benefit is currently available."""
        return self.is_active and not self.is_expired and not self.is_fully_redeemed

    @property
    def remaining_redemptions(self) -> int | None:
        """Get the number of remaining redemptions."""
        if self.redemption_limit is None:
            return None
        return max(0, self.redemption_limit - self.redemption_count)

    def get_contact_phone(self) -> str:
        """Get the contact phone based on contact source."""
        if self.contact_source == self.ContactSource.USER_PROFILE:
            profile = getattr(self.creator, "profile", None)
            return profile.phone if profile else ""
        return self.contact_phone

    def get_contact_email(self) -> str:
        """Get the contact email based on contact source."""
        if self.contact_source == self.ContactSource.USER_PROFILE:
            return self.creator.email
        return self.contact_email

    def get_contact_website(self) -> str:
        """Get the contact website based on contact source."""
        if self.contact_source == self.ContactSource.USER_PROFILE:
            profile = getattr(self.creator, "profile", None)
            return profile.website if profile else ""
        return self.contact_website

    def get_discount_codes_list(self) -> list[str]:
        """Get discount codes as a list."""
        if not self.discount_codes:
            return []
        return [code.strip() for code in self.discount_codes.split(",") if code.strip()]

    def can_edit(self, user: User) -> bool:
        """Check if a user can edit this benefit.

        Admins, moderators, and collaborators can edit any benefit.
        Other users can only edit benefits they created.
        """
        if user.is_superuser or user.role in [
            "administrador",
            "moderador",
            "colaborador",
        ]:
            return True
        return self.creator == user

    def can_delete(self, user: User) -> bool:
        """Check if a user can delete this benefit."""
        return self.can_edit(user)

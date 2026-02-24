import secrets
import string
from datetime import date
from typing import Any, ClassVar, cast

from django.contrib.auth import password_validation
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

# Help text for social media username fields
SOCIAL_USERNAME_HELP = "Solo el nombre de usuario (ej: facundopadilla)"


def generate_public_id() -> str:
    """Generate a short, URL-safe public ID (8 characters)."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


class UserManager(BaseUserManager):
    """Custom user manager that uses email as the unique identifier."""

    def create_user(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        birth_date: date | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", "miembro")
        user = cast(
            "User",
            self.model(
                email=email,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                **extra_fields,
            ),
        )
        if password:
            password_validation.validate_password(password, user)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        birth_date: date | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "administrador")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email, first_name, last_name, birth_date, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model using email as the authentication identifier."""

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        indexes = [
            models.Index(fields=["email_confirmed"]),
            models.Index(fields=["role"]),
        ]

    class Role(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        MODERADOR = "moderador", "Moderador"
        COLABORADOR = "colaborador", "Colaborador"
        MIEMBRO = "miembro", "Miembro"

    class RegistrationMethod(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE = "google", "Google"

    public_id = models.CharField(
        max_length=8,
        unique=True,
        default=generate_public_id,
        editable=False,
        verbose_name="ID público",
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    country = models.ForeignKey(
        "locations.Country",
        on_delete=models.PROTECT,
        related_name="users",
        default="AR",
    )
    province = models.ForeignKey(
        "locations.Province",
        on_delete=models.PROTECT,
        related_name="users",
        default=1,  # Salta (pk=1 in fixture)
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MIEMBRO)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registered_at = models.DateTimeField(default=timezone.now)
    email_confirmed = models.BooleanField(default=False)
    registration_method = models.CharField(
        max_length=20,
        choices=RegistrationMethod.choices,
        default=RegistrationMethod.EMAIL,
        verbose_name="método de registro",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = ["first_name", "last_name", "birth_date"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def needs_profile_completion(self) -> bool:
        """Check if user needs to complete their profile (social login users)."""
        return self.birth_date is None


class Profile(models.Model):
    """Extended user profile with technical role, social links, and bio."""

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    class TechnicalRole(models.TextChoices):
        BACKEND = "backend", "Backend"
        FRONTEND = "frontend", "Frontend"
        FULL_STACK = "fullstack", "Full Stack"
        BLOCKCHAIN = "blockchain", "Blockchain Developer"
        DEVOPS = "devops", "DevOps"
        MOBILE = "mobile", "Mobile Developer"
        DATA_SCIENCE = "data_science", "Data Science"
        IA_ML = "ia_ml", "IA/ML Engineer"
        SECURITY = "security", "Security Engineer"
        QA = "qa", "QA Engineer"
        UI_UX = "ui_ux", "UI/UX Designer"
        OTRO = "otro", "Otro"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    dni = models.CharField(max_length=15, blank=True, verbose_name="DNI")
    phone = models.CharField(max_length=20, blank=True, verbose_name="teléfono")
    technologies = models.JSONField(default=list, blank=True)
    technical_role = models.CharField(
        max_length=20, choices=TechnicalRole.choices, blank=True
    )
    bio = models.TextField(blank=True)
    github = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="GitHub",
        help_text=SOCIAL_USERNAME_HELP,
    )
    linkedin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="LinkedIn",
        help_text=SOCIAL_USERNAME_HELP,
    )
    twitter = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Twitter/X",
        help_text=SOCIAL_USERNAME_HELP,
    )
    instagram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Instagram",
        help_text=SOCIAL_USERNAME_HELP,
    )
    discord = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Discord",
        help_text="Tu ID de usuario de Discord (ej: 123456789012345678)",
    )
    website = models.URLField(blank=True, verbose_name="Sitio web")
    avatar_url = models.URLField(blank=True, default="")
    avatar_delete_url = models.URLField(blank=True, default="")
    location = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=100, blank=True)
    available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile for {self.user.email}"

    @property
    def github_url(self) -> str:
        """Return the full GitHub profile URL."""
        if self.github:
            return f"https://github.com/{self.github}"
        return ""

    @property
    def linkedin_url(self) -> str:
        """Return the full LinkedIn profile URL."""
        if self.linkedin:
            return f"https://linkedin.com/in/{self.linkedin}"
        return ""

    @property
    def twitter_url(self) -> str:
        """Return the full Twitter/X profile URL."""
        if self.twitter:
            return f"https://x.com/{self.twitter}"
        return ""

    @property
    def instagram_url(self) -> str:
        """Return the full Instagram profile URL."""
        if self.instagram:
            return f"https://instagram.com/{self.instagram}"
        return ""

    @property
    def discord_url(self) -> str:
        """Return the full Discord user URL."""
        if self.discord:
            return f"https://discord.com/users/{self.discord}"
        return ""

    @property
    def has_social_links(self) -> bool:
        """Check if any social link is set."""
        return any(
            [
                self.github,
                self.linkedin,
                self.twitter,
                self.instagram,
                self.discord and self.discord.strip(),
                self.website,
            ]
        )


class EmailVerificationCode(models.Model):
    """Six-digit code sent via email to verify a user's email address."""

    class Meta:
        verbose_name = "codigo de verificacion"
        verbose_name_plural = "codigos de verificacion"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_codes"
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Verification code for {self.user.email}"

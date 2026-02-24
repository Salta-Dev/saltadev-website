"""Forms for the dashboard app."""

import re
from datetime import date
from typing import cast

from django import forms
from django.forms import ModelChoiceField
from locations.models import Country, Province
from users.models import Profile, User


class ProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    class Meta:
        model = Profile
        fields = [
            "dni",
            "phone",
            "technical_role",
            "bio",
            "company",
            "position",
            "github",
            "linkedin",
            "twitter",
            "instagram",
            "discord",
            "website",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    # Technologies as comma-separated input
    technologies_input = forms.CharField(
        required=False,
        help_text="Separar con comas (ej: Python, Django, JavaScript)",
    )

    # Avatar file upload (handled separately, not in model)
    avatar_file = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize form with technologies as comma-separated string."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.technologies:
            self.fields["technologies_input"].initial = ", ".join(
                self.instance.technologies
            )

    def _clean_username(self, value: str, platform: str) -> str:
        """Extract username from value, removing @ prefix or full URL if provided."""
        if not value:
            return ""

        value = value.strip()

        # Remove @ prefix if present
        if value.startswith("@"):
            value = value[1:]

        # Extract username from common URL patterns
        url_patterns = {
            "github": r"(?:https?://)?(?:www\.)?github\.com/([^/?\s]+)",
            "linkedin": r"(?:https?://)?(?:www\.)?linkedin\.com/in/([^/?\s]+)",
            "twitter": r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([^/?\s]+)",
            "instagram": r"(?:https?://)?(?:www\.)?instagram\.com/([^/?\s]+)",
        }

        if platform in url_patterns:
            match = re.match(url_patterns[platform], value, re.IGNORECASE)
            if match:
                value = match.group(1)

        # Validate username length
        if len(value) > 50:
            raise forms.ValidationError(
                f"El nombre de usuario de {platform} es demasiado largo."
            )

        return value

    def clean_github(self) -> str:
        """Clean GitHub username."""
        return self._clean_username(self.cleaned_data.get("github", ""), "github")

    def clean_linkedin(self) -> str:
        """Clean LinkedIn username."""
        return self._clean_username(self.cleaned_data.get("linkedin", ""), "linkedin")

    def clean_twitter(self) -> str:
        """Clean Twitter/X username."""
        return self._clean_username(self.cleaned_data.get("twitter", ""), "twitter")

    def clean_instagram(self) -> str:
        """Clean Instagram username."""
        return self._clean_username(self.cleaned_data.get("instagram", ""), "instagram")

    def clean_discord(self) -> str:
        """Clean Discord username (allows # for discriminator)."""
        value = self.cleaned_data.get("discord", "")
        if not value:
            return ""
        # Remove @ prefix if present, but keep # for discriminator
        return value.strip().lstrip("@")

    def save(self, commit: bool = True) -> Profile:
        """Save profile with parsed technologies list."""
        profile = super().save(commit=False)

        # Parse technologies from comma-separated input
        tech_input = self.cleaned_data.get("technologies_input", "")
        if tech_input:
            technologies = [t.strip() for t in tech_input.split(",") if t.strip()]
            profile.technologies = technologies
        else:
            profile.technologies = []

        if commit:
            profile.save()
        return profile


class CompleteProfileForm(forms.Form):
    """
    Form for completing user profile after social login.

    Social login users (Google/GitHub) must provide birth_date and optionally
    update their country/province before accessing the dashboard.
    """

    birth_date = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Requerido para ser miembro de la comunidad.",
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label="País",
        initial="AR",
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        label="Provincia",
        required=False,
    )

    def __init__(self, *args, user: User | None = None, **kwargs) -> None:
        """Initialize form with user's current data."""
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            self.fields["country"].initial = user.country_id
            self.fields["province"].initial = user.province_id

            # Populate provinces for current country
            if user.country_id:
                cast(
                    ModelChoiceField, self.fields["province"]
                ).queryset = Province.objects.filter(country_id=user.country_id)

    def clean_birth_date(self) -> date:
        """Validate birth date is reasonable (user must be at least 13 years old)."""
        birth_date = self.cleaned_data["birth_date"]
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        if age < 13:
            raise forms.ValidationError(
                "Debes tener al menos 13 años para registrarte."
            )

        if age > 120:
            raise forms.ValidationError(
                "Por favor ingresa una fecha de nacimiento válida."
            )

        return birth_date

    def save(self) -> User:
        """Save the user's profile data."""
        if not self.user:
            raise ValueError("User is required to save profile")

        self.user.birth_date = self.cleaned_data["birth_date"]
        self.user.country = self.cleaned_data["country"]

        province = self.cleaned_data.get("province")
        if province:
            self.user.province = province

        self.user.save()
        return self.user

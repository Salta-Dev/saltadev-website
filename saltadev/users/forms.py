"""User forms for registration."""

from datetime import date
from typing import cast

from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelChoiceField
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from locations.models import Country, Province

from .models import Profile, User
from .validators import validate_not_disposable_email


def create_recaptcha_field() -> ReCaptchaField:
    """Create a reCAPTCHA field with dark theme and normal size."""
    return ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "dark",
                "data-size": "normal",
            }
        )
    )


class RegisterForm(UserCreationForm):
    """Registration form with separate name fields, location, age validation, and reCAPTCHA."""

    captcha = create_recaptcha_field()
    terms = forms.BooleanField(required=True, label="Acepto los términos y condiciones")

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        initial="AR",
        empty_label=None,
        to_field_name="code",
    )

    province = forms.ModelChoiceField(
        queryset=Province.objects.filter(country_id="AR"),
        empty_label="Seleccionar provincia",
    )

    class Meta(UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "birth_date",
            "country",
            "province",
        )

    def __init__(self, *args, **kwargs):
        """Initialize form and set province queryset based on selected country."""
        super().__init__(*args, **kwargs)

        # If form has data (POST), filter provinces by selected country
        if self.data.get("country"):
            try:
                country_code = self.data.get("country")
                province_field = cast(ModelChoiceField, self.fields["province"])
                province_field.queryset = Province.objects.filter(
                    country_id=country_code
                )
            except (ValueError, TypeError):
                pass

        # Set default province to Salta (id=1) for initial form
        if not self.data:
            self.fields["province"].initial = 1

    def clean_birth_date(self) -> date:
        """Validate birth date is valid and user is at least 13 years old."""
        birth_date = self.cleaned_data.get("birth_date")
        if not birth_date:
            raise forms.ValidationError("La fecha de nacimiento es obligatoria.")

        today = date.today()

        # No future dates
        if birth_date > today:
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")

        # Reasonable age limit (150 years)
        min_date = today.replace(year=today.year - 150)
        if birth_date < min_date:
            raise forms.ValidationError("Por favor ingresá una fecha válida.")

        # Minimum age (13 years)
        age = relativedelta(today, birth_date).years
        if age < 13:
            raise forms.ValidationError(
                "Debes tener al menos 13 años para registrarte."
            )
        return birth_date

    def clean_first_name(self):
        """Validate that first name is not empty."""
        first_name = self.cleaned_data.get("first_name", "").strip()
        if not first_name:
            raise forms.ValidationError("El nombre es requerido.")
        return first_name

    def clean_last_name(self):
        """Validate that last name is not empty."""
        last_name = self.cleaned_data.get("last_name", "").strip()
        if not last_name:
            raise forms.ValidationError("El apellido es requerido.")
        return last_name

    def clean_email(self) -> str:
        """Validate email is not already registered and not disposable."""
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError("El email es requerido.")

        # Check disposable email first
        validate_not_disposable_email(email)

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.email_confirmed:
                raise forms.ValidationError(
                    "Ya existe una cuenta verificada con este email."
                )
            else:
                raise forms.ValidationError(
                    "Ya tienes una cuenta registrada. Por favor verifica tu email desde la página de login."
                )
        return email

    def save(self, commit: bool = True) -> User:
        """Save user with default role and send verification email."""
        user = super().save(commit=False)
        user.role = "miembro"
        user.email_confirmed = False
        if commit:
            user.save()
            Profile.objects.create(user=user)
            from users.utils import send_verification_code

            send_verification_code(user)
        return user

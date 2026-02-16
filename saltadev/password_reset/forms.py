from typing import Any

from django import forms
from django.contrib.auth import password_validation
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset email."""

    email = forms.EmailField()
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "dark",
                "data-size": "normal",
            }
        )
    )

    def clean_email(self) -> str:
        return (self.cleaned_data.get("email") or "").strip().lower()


class PasswordResetConfirmForm(forms.Form):
    """Form for setting a new password after a valid reset token is provided."""

    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "dark",
                "data-size": "normal",
            }
        )
    )

    def __init__(self, *args: Any, **kwargs: Any):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            return cleaned_data
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")

        if new_password:
            try:
                password_validation.validate_password(new_password, self.user)
            except forms.ValidationError as exc:
                self.add_error("new_password", exc)

        return cleaned_data

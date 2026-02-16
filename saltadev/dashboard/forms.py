"""Forms for the dashboard app."""

from django import forms

from users.models import Profile


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

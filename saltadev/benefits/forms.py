"""Forms for the benefits app."""

from django import forms

from .models import Benefit


class ImageSourceChoices:
    """Choices for image source selection."""

    URL = "url"
    FILE = "file"

    CHOICES = [
        (URL, "Ingresar URL"),
        (FILE, "Subir archivo"),
    ]


class BenefitForm(forms.ModelForm):
    """Form for creating and editing benefits."""

    image_source = forms.ChoiceField(
        choices=ImageSourceChoices.CHOICES,
        initial=ImageSourceChoices.URL,
        widget=forms.RadioSelect(
            attrs={
                "class": "hidden peer",
            }
        ),
        required=False,
    )

    image_file = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "hidden",
                "accept": "image/*",
                "id": "id_image_file",
            }
        ),
    )

    class Meta:
        model = Benefit
        fields = [
            "title",
            "description",
            "image",
            "benefit_type",
            "discount_percentage",
            "redemption_limit",
            "expiration_date",
            "contact_source",
            "contact_phone",
            "contact_email",
            "contact_website",
            "modality",
            "location",
            "discount_codes",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Título del beneficio",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none",
                    "placeholder": "Descripción detallada del beneficio...",
                    "rows": 4,
                }
            ),
            "image": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "https://ejemplo.com/imagen.jpg",
                    "id": "id_image_url",
                }
            ),
            "benefit_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                }
            ),
            "discount_percentage": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Ej: 20",
                    "min": 1,
                    "max": 100,
                }
            ),
            "redemption_limit": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Dejar vacío para ilimitado",
                    "min": 1,
                }
            ),
            "expiration_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "type": "date",
                }
            ),
            "contact_source": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "id": "contact_source",
                }
            ),
            "contact_phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "+54 9 387 123 4567",
                }
            ),
            "contact_email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "contacto@ejemplo.com",
                }
            ),
            "contact_website": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "https://ejemplo.com",
                }
            ),
            "modality": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "id": "modality",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Av. Ejemplo 123, Salta",
                }
            ),
            "discount_codes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none",
                    "placeholder": "CODIGO1, CODIGO2, CODIGO3",
                    "rows": 2,
                }
            ),
        }

    def clean_discount_percentage(self) -> int | None:
        """Validate discount percentage is between 1 and 100."""
        percentage = self.cleaned_data.get("discount_percentage")
        benefit_type = self.cleaned_data.get("benefit_type")

        if benefit_type == Benefit.BenefitType.DISCOUNT and not percentage:
            raise forms.ValidationError(
                "El porcentaje de descuento es requerido para beneficios de tipo descuento."
            )

        if percentage is not None and (percentage < 1 or percentage > 100):
            raise forms.ValidationError("El porcentaje debe estar entre 1 y 100.")

        return percentage

    def clean(self) -> dict[str, object]:
        """Validate form data."""
        cleaned_data = super().clean() or {}
        contact_source = cleaned_data.get("contact_source")
        modality = cleaned_data.get("modality")

        # Validate custom contact info when contact_source is custom
        if contact_source == Benefit.ContactSource.CUSTOM:
            contact_phone = cleaned_data.get("contact_phone")
            contact_email = cleaned_data.get("contact_email")
            contact_website = cleaned_data.get("contact_website")

            if not any([contact_phone, contact_email, contact_website]):
                raise forms.ValidationError(
                    "Debe proporcionar al menos un método de contacto cuando "
                    "selecciona 'Ingresar manualmente'."
                )

        # Validate location when modality requires it
        if modality in [Benefit.Modality.IN_PERSON, Benefit.Modality.BOTH]:
            location = cleaned_data.get("location")
            if not location:
                raise forms.ValidationError(
                    "La ubicación es requerida para beneficios presenciales."
                )

        return cleaned_data

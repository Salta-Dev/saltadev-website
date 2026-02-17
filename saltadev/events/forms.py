"""Forms for the events app."""

from content.models import Event
from django import forms
from django.utils.text import slugify


class ImageSourceChoices:
    """Choices for image source selection."""

    URL = "url"
    FILE = "file"

    CHOICES = [
        (URL, "Ingresar URL"),
        (FILE, "Subir archivo"),
    ]


class EventForm(forms.ModelForm):
    """Form for creating and editing events."""

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
        model = Event
        fields = [
            "title",
            "description",
            "photo",
            "location",
            "link",
            "event_start_date",
            "event_end_date",
            "event_date_display",
            "event_time_display",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Título del evento",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none",
                    "placeholder": "Descripción del evento...",
                    "rows": 4,
                }
            ),
            "photo": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "https://ejemplo.com/imagen.jpg",
                    "id": "id_image_url",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Lugar del evento o 'Virtual'",
                }
            ),
            "link": forms.URLInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "https://ejemplo.com/registro",
                }
            ),
            "event_start_date": forms.DateTimeInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "type": "datetime-local",
                }
            ),
            "event_end_date": forms.DateTimeInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "type": "datetime-local",
                }
            ),
            "event_date_display": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Ej: 15 de Marzo",
                }
            ),
            "event_time_display": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white placeholder-[#6b605f] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                    "placeholder": "Ej: 18:00 hs",
                }
            ),
        }

    def clean_title(self) -> str:
        """Validate title is provided."""
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("El título es requerido.")
        return title

    def clean(self) -> dict[str, object]:
        """Validate form data and generate slug."""
        cleaned_data = super().clean() or {}

        # Validate dates
        start_date = cleaned_data.get("event_start_date")
        end_date = cleaned_data.get("event_end_date")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError(
                "La fecha de fin no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data

    def save(self, commit: bool = True) -> Event:
        """Save the event with auto-generated slug."""
        event = super().save(commit=False)

        # Generate slug if not set
        if not event.slug:
            base_slug = slugify(event.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=event.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            event.slug = slug

        if commit:
            event.save()

        return event

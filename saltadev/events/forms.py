"""Forms for the events app."""

from datetime import datetime
from typing import Any

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

    # Separate date and time fields for better 24h format control
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                "type": "date",
            }
        ),
    )
    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                "type": "time",
                "step": "60",
            }
        ),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                "type": "date",
            }
        ),
    )
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={
                "class": "w-full px-4 py-3 bg-[#1d1919] border border-[#3d2f2f] rounded-xl text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary",
                "type": "time",
                "step": "60",
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize form and populate separate date/time fields."""
        super().__init__(*args, **kwargs)
        instance: Event | None = kwargs.get("instance")
        if instance:
            if instance.event_start_date:
                self.fields["start_date"].initial = instance.event_start_date.date()
                self.fields["start_time"].initial = instance.event_start_date.time()
            if instance.event_end_date:
                self.fields["end_date"].initial = instance.event_end_date.date()
                self.fields["end_time"].initial = instance.event_end_date.time()

    def clean_title(self) -> str:
        """Validate title is provided."""
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("El título es requerido.")
        return title

    def clean(self) -> dict[str, object]:
        """Validate form data and combine date/time fields."""
        cleaned_data = super().clean() or {}

        # Combine date and time fields into datetime
        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")

        event_start_datetime = None
        event_end_datetime = None

        if start_date and start_time:
            event_start_datetime = datetime.combine(start_date, start_time)
        elif start_date:
            event_start_datetime = datetime.combine(start_date, datetime.min.time())

        if end_date and end_time:
            event_end_datetime = datetime.combine(end_date, end_time)
        elif end_date:
            event_end_datetime = datetime.combine(end_date, datetime.min.time())

        # Store combined datetime values
        cleaned_data["event_start_date"] = event_start_datetime
        cleaned_data["event_end_date"] = event_end_datetime

        # Validate dates
        if (
            event_start_datetime
            and event_end_datetime
            and event_end_datetime < event_start_datetime
        ):
            raise forms.ValidationError(
                "La fecha de fin no puede ser anterior a la fecha de inicio."
            )

        return cleaned_data

    def save(self, commit: bool = True) -> Event:
        """Save the event with auto-generated slug and combined datetime."""
        event = super().save(commit=False)

        # Set datetime fields from cleaned data
        event.event_start_date = self.cleaned_data.get("event_start_date")
        event.event_end_date = self.cleaned_data.get("event_end_date")

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

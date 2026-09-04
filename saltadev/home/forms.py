"""Forms for public Recursos submissions."""

from typing import Any

from content.models import CatalogEntry, LearningResource
from django import forms
from saltadev.form_widgets import INPUT_CLASS, SELECT_CLASS, TEXTAREA_CLASS


class ProjectForm(forms.ModelForm):
    """Public form to propose a community project."""

    class Meta:
        model = CatalogEntry
        fields = ("title", "summary", "url", "authors", "stack")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "summary": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "url": forms.URLInput(attrs={"class": INPUT_CLASS}),
            "authors": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "stack": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
        }
        labels = {
            "title": "Nombre del proyecto",
            "summary": "Qué hace",
            "url": "Enlace",
            "authors": "Autores",
            "stack": "Stack",
        }
        help_texts = {
            "url": "Repo, demo o sitio del proyecto.",
            "stack": "Una tecnología por línea.",
            "authors": "Quién lo construyó. Si queda vacío se usa el nombre de la cuenta.",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["url"].required = True
        self.fields["authors"].required = False
        self.fields["stack"].required = False


class ToolForm(forms.ModelForm):
    """Public form to propose a tool for the catalog."""

    class Meta:
        model = CatalogEntry
        fields = ("title", "summary", "url", "category", "pricing", "tags")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "summary": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "url": forms.URLInput(attrs={"class": INPUT_CLASS}),
            "category": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "pricing": forms.Select(attrs={"class": SELECT_CLASS}),
            "tags": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 2}),
        }
        labels = {
            "title": "Nombre de la herramienta",
            "summary": "Qué es y para qué sirve",
            "url": "Enlace",
            "category": "Categoría",
            "pricing": "Precio",
            "tags": "Etiquetas",
        }
        help_texts = {
            "url": "Sitio oficial o docs.",
            "category": "Por ejemplo: Desarrollo, IA, Diseño, DevOps.",
            "tags": "Una por línea.",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["url"].required = True
        self.fields["category"].required = False
        self.fields["pricing"].required = False
        self.fields["tags"].required = False
        self.fields["pricing"].widget.choices = [
            ("", "Sin especificar"),
            ("Gratis", "Gratis"),
            ("Freemium", "Freemium"),
            ("De pago", "De pago"),
        ]


class ReadingForm(forms.ModelForm):
    """Public form to propose a book for Lectura."""

    class Meta:
        model = CatalogEntry
        fields = ("title", "summary", "url", "authors")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "summary": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "url": forms.URLInput(attrs={"class": INPUT_CLASS}),
            "authors": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }
        labels = {
            "title": "Título del libro",
            "summary": "De qué trata",
            "url": "Enlace",
            "authors": "Autores",
        }
        help_texts = {
            "url": "Ficha, editorial o compra.",
            "authors": "Opcional.",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["url"].required = True
        self.fields["authors"].required = False


class CourseForm(forms.ModelForm):
    """Public form to propose a course or tip."""

    class Meta:
        model = LearningResource
        fields = (
            "title",
            "tip",
            "url",
            "track",
            "source",
            "duration",
            "instructor",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "tip": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 4}),
            "url": forms.URLInput(attrs={"class": INPUT_CLASS}),
            "track": forms.Select(attrs={"class": SELECT_CLASS}),
            "source": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "duration": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "instructor": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }
        labels = {
            "title": "Título del curso",
            "tip": "Qué vas a aprender",
            "url": "Enlace",
            "track": "Pista",
            "source": "Fuente",
            "duration": "Duración",
            "instructor": "Dictado por",
        }
        help_texts = {
            "track": "Developers o Vibecoders.",
            "source": "Plataforma u organización (opcional).",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["url"].required = True
        self.fields["track"].required = True
        self.fields["source"].required = False
        self.fields["duration"].required = False
        self.fields["instructor"].required = False

"""Add LearningResource and seed the first curated courses."""

from django.db import migrations, models
from django.utils import timezone

SEED = (
    (
        "developers",
        1,
        "Tutorial oficial de Python",
        "Tutorial oficial del lenguaje: tipos, funciones y control de flujo. Disponible en español.",
        "https://docs.python.org/es/3/tutorial/",
        "docs.python.org",
    ),
    (
        "developers",
        2,
        "Django: primer proyecto",
        "Tutorial oficial para crear una aplicación web. Es el framework que usa salta.dev.",
        "https://docs.djangoproject.com/es/5.2/intro/tutorial01/",
        "docs.djangoproject.com",
    ),
    (
        "developers",
        3,
        "Git y GitHub",
        "Guía de Git y GitHub: commits, ramas y flujo de trabajo en equipo.",
        "https://docs.github.com/es/get-started/using-git",
        "docs.github.com",
    ),
    (
        "developers",
        4,
        "HTML semántico (MDN)",
        "Documentación de MDN sobre HTML semántico y estructura de contenido web.",
        "https://developer.mozilla.org/es/docs/Learn_web_development/Core/Structuring_content",
        "MDN",
    ),
    (
        "vibecoders",
        1,
        "Cursor: trabajo con el agente",
        "Documentación de Cursor sobre contexto, alcance y trabajo con el agente.",
        "https://cursor.com/docs",
        "cursor.com",
    ),
    (
        "vibecoders",
        2,
        "Revisión de cambios generados por agentes",
        "Guía para revisar el diff de un agente antes de integrarlo.",
        "https://cursor.com/docs/agent/overview",
        "cursor.com",
    ),
    (
        "vibecoders",
        3,
        "Buenas prácticas de Claude Code",
        "Prácticas recomendadas de Anthropic para Claude Code: plan, tests y unidades de trabajo.",
        "https://www.anthropic.com/engineering/claude-code-best-practices",
        "Anthropic",
    ),
    (
        "vibecoders",
        4,
        "Secretos fuera del contexto de IA",
        "Guía de GitHub para no incluir secretos en el contexto del agente ni en el repositorio.",
        "https://docs.github.com/es/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository",
        "GitHub",
    ),
)


def seed_learning_resources(apps, schema_editor) -> None:
    """Load the first catalog so /recursos/ is not empty after migrate."""
    resource_model = apps.get_model("content", "LearningResource")
    now = timezone.now()
    resource_model.objects.bulk_create(
        [
            resource_model(
                title=title,
                tip=tip,
                url=url,
                source=source,
                track=track,
                order=order,
                is_published=True,
                created_at=now,
            )
            for track, order, title, tip, url, source in SEED
        ]
    )


def unseed_learning_resources(apps, schema_editor) -> None:
    """Remove only the seeded titles on reverse."""
    resource_model = apps.get_model("content", "LearningResource")
    resource_model.objects.filter(title__in=[row[2] for row in SEED]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0013_event_kind"),
    ]

    operations = [
        migrations.CreateModel(
            name="LearningResource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="título")),
                ("tip", models.TextField(verbose_name="tip")),
                ("url", models.URLField(verbose_name="enlace")),
                (
                    "source",
                    models.CharField(blank=True, max_length=80, verbose_name="fuente"),
                ),
                (
                    "track",
                    models.CharField(
                        choices=[
                            ("developers", "Developers"),
                            ("vibecoders", "Vibecoders"),
                        ],
                        max_length=20,
                        verbose_name="pista",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="orden")),
                (
                    "is_published",
                    models.BooleanField(default=True, verbose_name="publicado"),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=timezone.now),
                ),
            ],
            options={
                "verbose_name": "curso / tip",
                "verbose_name_plural": "cursos y tips",
                "ordering": ("track", "order", "created_at"),
            },
        ),
        migrations.AddIndex(
            model_name="learningresource",
            index=models.Index(
                fields=["is_published", "track", "order"],
                name="content_lea_is_publ_8c1a2f_idx",
            ),
        ),
        migrations.RunPython(seed_learning_resources, unseed_learning_resources),
    ]

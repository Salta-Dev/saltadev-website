"""Replace conversational Recursos copy with catalog wording."""

import importlib

from django.db import migrations

COURSES = {
    "Tutorial oficial de Python": (
        "Tutorial oficial de Python",
        "Tutorial oficial del lenguaje: tipos, funciones y control de "
        "flujo. Disponible en español.",
    ),
    "Django: primer proyecto": (
        "Django: primer proyecto",
        "Tutorial oficial para crear una aplicación web. Es el framework "
        "que usa salta.dev.",
    ),
    "Git y GitHub, sin misterio": (
        "Git y GitHub",
        "Guía de Git y GitHub: commits, ramas y flujo de trabajo en equipo.",
    ),
    "HTML semántico (MDN)": (
        "HTML semántico (MDN)",
        "Documentación de MDN sobre HTML semántico y estructura de contenido web.",
    ),
    "Cursor: cómo pedirle trabajo al agente": (
        "Cursor: trabajo con el agente",
        "Documentación de Cursor sobre contexto, alcance y trabajo con el agente.",
    ),
    "Revisá el diff como si fuera de un junior": (
        "Revisión de cambios generados por agentes",
        "Guía para revisar el diff de un agente antes de integrarlo.",
    ),
    "Buenas prácticas de Claude Code": (
        "Buenas prácticas de Claude Code",
        "Prácticas recomendadas de Anthropic para Claude Code: plan, "
        "tests y unidades de trabajo.",
    ),
    "Nunca pegues secretos en el chat": (
        "Secretos fuera del contexto de IA",
        "Guía de GitHub para no incluir secretos en el contexto del "
        "agente ni en el repositorio.",
    ),
}


def update_copy(apps, schema_editor) -> None:
    """Refresh seeded specialties, audiences and course blurbs."""
    hub = importlib.import_module("content.migrations.0016_resource_hub")
    specialties_mod = importlib.import_module("content.migrations.0015_techspecialty")
    specialty_model = apps.get_model("content", "TechSpecialty")
    resource_model = apps.get_model("content", "LearningResource")

    audience_by_slug = {row[1]: row[7] for row in specialties_mod.SEED}
    for slug, sections in hub.SECTIONS.items():
        specialty_model.objects.filter(slug=slug).update(
            sections=sections,
            audience=audience_by_slug.get(slug, ""),
        )

    for old_title, (new_title, tip) in COURSES.items():
        resource_model.objects.filter(title=old_title).update(title=new_title, tip=tip)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0020_update_specialty_summaries"),
    ]

    operations = [
        migrations.RunPython(update_copy, migrations.RunPython.noop),
    ]

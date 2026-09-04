"""Rewrite public book descriptions to a catalog tone."""

from django.db import migrations

SUMMARIES = {
    "The Pragmatic Programmer": (
        "Libro sobre el oficio de programar: debugging, automatización, "
        "aprendizaje continuo y cómo tomar mejores decisiones día a día."
    ),
    "Clean Code": (
        "Guía para escribir código más legible: nombres claros, funciones "
        "chicas, tests y criterios para revisar un cambio."
    ),
    "Designing Data-Intensive Applications": (
        "Cómo se almacenan, replican y consultan datos a escala: consistencia, "
        "particionado y sistemas distribuidos."
    ),
    "Domain-Driven Design": (
        "Cómo modelar software con el idioma del negocio: bounded contexts, "
        "lenguaje ubicuo y diseño táctico."
    ),
    "Refactoring": (
        "Catálogo de técnicas para cambiar la estructura del código sin "
        "cambiar el comportamiento, con olores y movimientos."
    ),
    "Accelerate": (
        "Investigación sobre qué practican y miden los equipos que entregan "
        "software seguido y con estabilidad."
    ),
    "The Manager's Path": (
        "Recorrido de la carrera de management en ingeniería: de tech lead a "
        "director, 1:1 y criterio técnico."
    ),
    "The Staff Engineer's Path": (
        "Cómo crecer como individual contributor senior: influencia, "
        "proyectos transversales y alcance sin pasar a management."
    ),
    "The Mythical Man-Month": (
        "Ensayos clásicos de gestión de proyectos de software, incluido por "
        "qué sumar gente a un proyecto atrasado lo atrasa más."
    ),
    "You Don't Know JS": (
        "Serie sobre JavaScript por dentro: scope, closures, this y async. "
        "El material está publicado gratis en GitHub."
    ),
    "Shape Up": (
        "Método de producto de Basecamp: ciclos de seis semanas, definición "
        "del trabajo (shaping) y apuestas en lugar de un backlog continuo."
    ),
    "Site Reliability Engineering": (
        "Cómo Google opera sistemas en producción: SLIs y SLOs, error "
        "budgets, toil y trabajo de guardia."
    ),
}


def update_summaries(apps, schema_editor) -> None:
    """Replace snarky one-liners with catalog copy."""
    catalog_model = apps.get_model("content", "CatalogEntry")
    for title, summary in SUMMARIES.items():
        catalog_model.objects.filter(kind="reading", title=title).update(
            summary=summary
        )


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0018_update_tool_summaries"),
    ]

    operations = [
        migrations.RunPython(update_summaries, migrations.RunPython.noop),
    ]

"""Rewrite public tool descriptions to a catalog tone."""

from django.db import migrations

SUMMARIES = {
    "Visual Studio Code": (
        "Editor de código de Microsoft: Git integrado, debugging, resaltado de "
        "sintaxis y miles de extensiones. Corre en Windows, macOS y Linux."
    ),
    "Cursor": (
        "Editor basado en VS Code con un agente de IA. Autocompletado, chat "
        "sobre el proyecto y cambios en varios archivos a la vez."
    ),
    "Claude": (
        "Asistente de Anthropic para redactar, explicar código y discutir diseño. "
        "Funciona por chat; también hay API y agente en la terminal."
    ),
    "Docker": (
        "Plataforma de contenedores: empaquetás la app con sus dependencias para "
        "que corra igual en cualquier máquina. Compose arma varios servicios juntos."
    ),
    "GitHub": (
        "Alojamiento de repositorios Git con pull requests, issues y GitHub Actions "
        "para integrar y desplegar. Plan gratuito para uso personal."
    ),
    "Figma": (
        "Diseño de interfaces y prototipos en el navegador, con comentarios y "
        "edición en simultáneo. Sirve para UI, flujos y handoff al código."
    ),
    "Postman": (
        "Cliente para probar APIs HTTP: armás requests, guardás colecciones y "
        "compartís entornos con el equipo. Hay plan gratuito individual."
    ),
    "PostgreSQL": (
        "Base de datos relacional open source. SQL, transacciones, índices, JSON "
        "y réplicas. Es el motor que usa mucha web, incluida esta."
    ),
    "Notion": (
        "Espacio de trabajo con notas, wikis, bases de datos y tareas. Sirve para "
        "docs de equipo y seguimiento liviano de trabajo."
    ),
    "Linear": (
        "Gestor de issues, ciclos y roadmaps para equipos de software. Atajos de "
        "teclado y una UI pensada para ir rápido."
    ),
    "Warp": (
        "Terminal con bloques de output, autocompletado y ayuda de IA. Disponible "
        "para macOS, Linux y Windows."
    ),
    "Django": (
        "Framework web de Python: ORM, panel de admin, autenticación y "
        "convenciones para armar backends. Open source y gratis."
    ),
}


def update_summaries(apps, schema_editor) -> None:
    """Replace snarky one-liners with catalog copy."""
    catalog_model = apps.get_model("content", "CatalogEntry")
    for title, summary in SUMMARIES.items():
        catalog_model.objects.filter(kind="tool", title=title).update(summary=summary)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0017_catalog_project_approval"),
    ]

    operations = [
        migrations.RunPython(update_summaries, migrations.RunPython.noop),
    ]

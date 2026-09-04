"""Rewrite public specialty descriptions to a catalog tone."""

from django.db import migrations

SUMMARIES = {
    "frontend": (
        "Construye la interfaz en el navegador: layout, estados, "
        "accesibilidad y rendimiento percibido."
    ),
    "backend": (
        "Implementa la lógica del servidor, los datos y las APIs que "
        "consume el resto de la aplicación."
    ),
    "full-stack": (
        "Trabaja las dos capas de una app para cerrar un feature de la "
        "interfaz a la base de datos."
    ),
    "mobile-ios": (
        "Desarrolla apps nativas para iPhone y iPad con las herramientas "
        "y el store de Apple."
    ),
    "mobile-android": (
        "Desarrolla apps nativas para Android, la plataforma con más dispositivos."
    ),
    "mobile-multiplataforma": (
        "Publica en iOS y Android con un código compartido, útil cuando "
        "el equipo es chico."
    ),
    "videojuegos": (
        "Programa jugabilidad, físicas y sistemas de juego, generalmente "
        "sobre un motor como Unity, Godot o Unreal."
    ),
    "blockchain": (
        "Escribe contratos y aplicaciones que corren en redes compartidas, "
        "con énfasis en seguridad y criptografía."
    ),
    "ciencia-de-datos": (
        "Limpia, analiza y visualiza datos para explicar qué cambió y con "
        "qué evidencia."
    ),
    "machine-learning": (
        "Entrena y evalúa modelos que aprenden de datos. Incluye agentes "
        "y revisión humana del resultado."
    ),
    "data-engineering": (
        "Diseña pipelines de ingest y transformación para que el resto del "
        "equipo tenga tablas confiables."
    ),
    "devops": (
        "Automatiza build, deploy y observación para que el código llegue "
        "a producción de forma repetible."
    ),
    "ciberseguridad": (
        "Encuentra y cierra vulnerabilidades en apps, redes e identidades. "
        "Incluye no guardar secretos en el repositorio."
    ),
    "qa": (
        "Diseña casos de prueba, automatiza regresiones y valida que el "
        "build esté listo para publicar."
    ),
    "redes": ("Configura ruteo, DNS, firewalls y la red que el cloud abstrae."),
    "soporte-tecnico": (
        "Primera línea con usuarios: diagnostica, documenta y escala incidentes."
    ),
    "bases-de-datos": (
        "Modela, indexa y resguarda la fuente de verdad: backups, réplicas "
        "e integridad."
    ),
    "diseno-ui-ux": (
        "Investiga, dibuja flujos y prototipa interfaces para que el "
        "producto se entienda y se pueda usar."
    ),
    "product-management": (
        "Define qué se construye y qué no: habla con usuarios, recorta "
        "alcance y prioriza el porqué."
    ),
    "project-management": (
        "Coordina fechas, dependencias y riesgos para que el trabajo cruce la línea."
    ),
    "tech-lead": (
        "Sigue en el código y marca el rumbo técnico: reviews, mentoría "
        "y estándares del equipo."
    ),
    "engineering-management": (
        "Cuida al equipo: hiring, 1:1, carga y foco. El delivery depende "
        "de las personas, no solo del tablero."
    ),
    "arquitectura": (
        "Define límites, contratos y trade-offs del sistema para que aguante el cambio."
    ),
}


def update_summaries(apps, schema_editor) -> None:
    """Replace punchy one-liners with catalog copy."""
    specialty_model = apps.get_model("content", "TechSpecialty")
    for slug, summary in SUMMARIES.items():
        specialty_model.objects.filter(slug=slug).update(summary=summary)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0019_update_book_summaries"),
    ]

    operations = [
        migrations.RunPython(update_summaries, migrations.RunPython.noop),
    ]

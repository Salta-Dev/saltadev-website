"""Add TechSpecialty and seed the first IT roles catalog."""

from django.db import migrations, models
from django.utils import timezone

# title, slug, family, icon, order, summary, stack, audience
SEED = (
    (
        "Frontend web",
        "frontend",
        "development",
        "web",
        1,
        "Construye la interfaz en el navegador: layout, estados, accesibilidad y rendimiento percibido.",
        "HTML\nCSS\nJavaScript\nTypeScript\nReact\nVue\nSvelte",
        "Quien desarrolla la interfaz, el layout y la experiencia en el navegador.",
    ),
    (
        "Backend",
        "backend",
        "development",
        "dns",
        2,
        "Implementa la lógica del servidor, los datos y las APIs que consume el resto de la aplicación.",
        "Python\nDjango\nNode.js\nGo\nPostgreSQL\nRedis",
        "Quien implementa APIs, modelos de datos y lógica de servidor.",
    ),
    (
        "Full stack",
        "full-stack",
        "development",
        "stacks",
        3,
        "Trabaja las dos capas de una app para cerrar un feature de la interfaz a la base de datos.",
        "TypeScript\nDjango\nReact\nPostgreSQL\nAPIs REST",
        "Quien cubre interfaz y servidor para cerrar un feature de punta a punta.",
    ),
    (
        "Mobile iOS",
        "mobile-ios",
        "development",
        "phone_iphone",
        4,
        "Desarrolla apps nativas para iPhone y iPad con las herramientas y el store de Apple.",
        "Swift\nSwiftUI\nXcode\nTestFlight",
        "Quien desarrolla aplicaciones nativas en el ecosistema Apple.",
    ),
    (
        "Mobile Android",
        "mobile-android",
        "development",
        "android",
        5,
        "Desarrolla apps nativas para Android, la plataforma con más dispositivos.",
        "Kotlin\nJetpack Compose\nAndroid Studio\nGoogle Play",
        "Quien desarrolla aplicaciones nativas para Android.",
    ),
    (
        "Mobile multiplataforma",
        "mobile-multiplataforma",
        "development",
        "smartphone",
        6,
        "Publica en iOS y Android con un código compartido, útil cuando el equipo es chico.",
        "Flutter\nReact Native\nExpo\nDart",
        "Equipos que publican en iOS y Android sin mantener dos apps nativas.",
    ),
    (
        "Videojuegos",
        "videojuegos",
        "development",
        "sports_esports",
        7,
        "Programa jugabilidad, físicas y sistemas de juego, generalmente sobre un motor como Unity, Godot o Unreal.",
        "Unity\nGodot\nUnreal\nC#\nC++",
        "Quien programa jugabilidad, físicas y sistemas de juego.",
    ),
    (
        "Blockchain y Web3",
        "blockchain",
        "development",
        "currency_bitcoin",
        8,
        "Escribe contratos y aplicaciones que corren en redes compartidas, con énfasis en seguridad y criptografía.",
        "Solidity\nEthereum\nEthers.js\nCriptografía",
        "Quien desarrolla contratos y aplicaciones sobre redes compartidas.",
    ),
    (
        "Ciencia de datos",
        "ciencia-de-datos",
        "data",
        "query_stats",
        1,
        "Limpia, analiza y visualiza datos para explicar qué cambió y con qué evidencia.",
        "Python\nPandas\nSQL\nJupyter\nTableau",
        "Quien analiza, visualiza y comunica hallazgos a partir de datos.",
    ),
    (
        "Machine learning e IA",
        "machine-learning",
        "data",
        "psychology",
        2,
        "Entrena y evalúa modelos que aprenden de datos. Incluye agentes y revisión humana del resultado.",
        "Python\nPyTorch\nscikit-learn\nTransformers",
        "Quien entrena, evalúa y pone en producción modelos.",
    ),
    (
        "Data engineering",
        "data-engineering",
        "data",
        "sync_alt",
        3,
        "Diseña pipelines de ingest y transformación para que el resto del equipo tenga tablas confiables.",
        "SQL\ndbt\nSpark\nAirflow\nWarehouses",
        "Quien construye pipelines y tablas para el resto del equipo.",
    ),
    (
        "DevOps y cloud",
        "devops",
        "operations",
        "cloud",
        1,
        "Automatiza build, deploy y observación para que el código llegue a producción de forma repetible.",
        "Docker\nKubernetes\nGitHub Actions\nTerraform\nAWS",
        "Quien automatiza infraestructura, deploy y observación.",
    ),
    (
        "Ciberseguridad",
        "ciberseguridad",
        "operations",
        "shield",
        2,
        "Encuentra y cierra vulnerabilidades en apps, redes e identidades. Incluye no guardar secretos en el repositorio.",
        "OWASP\nAppSec\nPentest\nIAM",
        "Quien identifica y mitiga vulnerabilidades.",
    ),
    (
        "QA y testing",
        "qa",
        "operations",
        "bug_report",
        3,
        "Diseña casos de prueba, automatiza regresiones y valida que el build esté listo para publicar.",
        "Pytest\nPlaywright\nCypress\nTDD",
        "Quien diseña pruebas y valida que el software esté listo para publicar.",
    ),
    (
        "Redes e infraestructura",
        "redes",
        "operations",
        "lan",
        4,
        "Configura ruteo, DNS, firewalls y la red que el cloud abstrae.",
        "TCP/IP\nDNS\nVPN\nLinux\nFirewalls",
        "Quien configura conectividad, DNS y seguridad de red.",
    ),
    (
        "Soporte técnico",
        "soporte-tecnico",
        "operations",
        "support_agent",
        5,
        "Primera línea con usuarios: diagnostica, documenta y escala incidentes.",
        "Tickets\nLinux\nRedes\nDocumentación",
        "Quien diagnostica y escala incidentes con usuarios.",
    ),
    (
        "Bases de datos",
        "bases-de-datos",
        "operations",
        "database",
        6,
        "Modela, indexa y resguarda la fuente de verdad: backups, réplicas e integridad.",
        "PostgreSQL\nMySQL\nBackups\nÍndices\nReplicación",
        "Quien modela, indexa y opera la fuente de verdad.",
    ),
    (
        "Diseño UI/UX",
        "diseno-ui-ux",
        "design",
        "palette",
        1,
        "Investiga, dibuja flujos y prototipa interfaces para que el producto se entienda y se pueda usar.",
        "Figma\nWireframes\nDesign systems\nAccesibilidad",
        "Quien investiga, prototipa y define la experiencia de uso.",
    ),
    (
        "Product management",
        "product-management",
        "product",
        "inventory_2",
        1,
        "Define qué se construye y qué no: habla con usuarios, recorta alcance y prioriza el porqué.",
        "Discovery\nRoadmap\nMétricas\nHistorias de usuario",
        "Quien define problema, alcance y prioridad del producto.",
    ),
    (
        "Project management",
        "project-management",
        "product",
        "assignment",
        2,
        "Coordina fechas, dependencias y riesgos para que el trabajo cruce la línea.",
        "Scrum\nKanban\nJira\nEstimación",
        "Quien coordina fechas, dependencias y riesgos.",
    ),
    (
        "Tech lead",
        "tech-lead",
        "leadership",
        "group",
        1,
        "Sigue en el código y marca el rumbo técnico: reviews, mentoría y estándares del equipo.",
        "Arquitectura\nCode review\nMentoría\nEstándares",
        "Quien combina trabajo técnico con rumbo y mentoría del equipo.",
    ),
    (
        "Engineering management",
        "engineering-management",
        "leadership",
        "supervisor_account",
        2,
        "Cuida al equipo: hiring, 1:1, carga y foco. El delivery depende de las personas, no solo del tablero.",
        "1:1\nHiring\nProcesos\nMétricas de equipo",
        "Quien gestiona personas, hiring y foco del equipo.",
    ),
    (
        "Arquitectura de software",
        "arquitectura",
        "leadership",
        "account_tree",
        3,
        "Define límites, contratos y trade-offs del sistema para que aguante el cambio.",
        "DDD\nMicroservicios\nEventos\nAPIs",
        "Quien define límites, contratos y evolución del sistema.",
    ),
)


def seed_specialties(apps, schema_editor) -> None:
    """Insert the first curated IT roles."""
    specialty_model = apps.get_model("content", "TechSpecialty")
    now = timezone.now()
    specialty_model.objects.bulk_create(
        [
            specialty_model(
                title=title,
                slug=slug,
                family=family,
                icon=icon,
                order=order,
                summary=summary,
                stack=stack,
                audience=audience,
                is_published=True,
                created_at=now,
            )
            for title, slug, family, icon, order, summary, stack, audience in SEED
        ]
    )


def unseed_specialties(apps, schema_editor) -> None:
    """Remove seeded specialties by slug."""
    specialty_model = apps.get_model("content", "TechSpecialty")
    specialty_model.objects.filter(slug__in=[row[1] for row in SEED]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0014_learningresource"),
    ]

    operations = [
        migrations.CreateModel(
            name="TechSpecialty",
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
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("title", models.CharField(max_length=120, verbose_name="título")),
                ("summary", models.TextField(verbose_name="qué hace")),
                (
                    "stack",
                    models.TextField(
                        blank=True,
                        help_text="Una tecnología por línea. Se muestran como chips.",
                        verbose_name="tecnologías",
                    ),
                ),
                ("audience", models.TextField(blank=True, verbose_name="para quién")),
                (
                    "family",
                    models.CharField(
                        choices=[
                            ("development", "Desarrollo"),
                            ("data", "Datos e IA"),
                            ("operations", "Operaciones y calidad"),
                            ("design", "Diseño"),
                            ("product", "Producto"),
                            ("leadership", "Liderazgo"),
                        ],
                        max_length=20,
                        verbose_name="familia",
                    ),
                ),
                (
                    "icon",
                    models.CharField(
                        default="layers", max_length=40, verbose_name="ícono"
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(default=0, verbose_name="orden"),
                ),
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
                "verbose_name": "especialidad",
                "verbose_name_plural": "especialidades",
                "ordering": ("family", "order", "title"),
            },
        ),
        migrations.AddIndex(
            model_name="techspecialty",
            index=models.Index(
                fields=["is_published", "family", "order"],
                name="content_tec_is_publ_a1b2c3_idx",
            ),
        ),
        migrations.RunPython(seed_specialties, unseed_specialties),
    ]

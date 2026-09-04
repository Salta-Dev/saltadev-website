"""Enrich specialties and add the reading/tools/projects catalog."""

from django.db import migrations, models
from django.utils import timezone

SECTIONS = {
    "frontend": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "HTML, CSS y JavaScript",
                "TypeScript",
                "React, Vue, Svelte u otro framework de interfaz",
                "Herramientas de build: Vite, Webpack, Next.js",
                "CSS: Tailwind, tokens y design systems",
                "Accesibilidad y métricas de rendimiento (LCP, CLS)",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien desarrolla la interfaz, el layout y la experiencia en el navegador.",
            ],
        },
    ],
    "backend": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Lenguajes: Python, Node.js, Go, Java, C#",
                "Frameworks: Django, FastAPI, Express, Spring, NestJS",
                "PostgreSQL, MySQL, MongoDB, Redis",
                "APIs REST y GraphQL, autenticación y permisos",
                "Colas, trabajos en segundo plano y observabilidad",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien implementa APIs, modelos de datos y lógica de servidor.",
            ],
        },
    ],
    "full-stack": [
        {
            "heading": "Qué cubre",
            "items": [
                "Interfaz y servidor en un mismo flujo de trabajo",
                "Trade-offs de cada capa",
                "Equipos chicos, startups y productos en etapa temprana",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien cubre interfaz y servidor para cerrar un feature de punta a punta.",
            ],
        },
    ],
    "mobile-ios": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Swift y, en código legado, Objective-C",
                "SwiftUI y UIKit",
                "Xcode, TestFlight, App Store Connect",
                "Core Data / SwiftData, notificaciones y permisos del sistema",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien desarrolla aplicaciones nativas en el ecosistema Apple.",
            ],
        },
    ],
    "mobile-android": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Kotlin y, en codebases largos, Java",
                "Jetpack Compose y Views",
                "Android Studio, Room, Material",
                "Google Play Console y Firebase",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien desarrolla aplicaciones nativas para Android.",
            ],
        },
    ],
    "mobile-multiplataforma": [
        {
            "heading": "Frameworks principales",
            "items": [
                "Flutter (Dart)",
                "React Native / Expo",
                "Un código compartido para iOS y Android",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Equipos que publican en iOS y Android sin mantener dos apps nativas.",
            ],
        },
    ],
    "videojuegos": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Motores: Unity, Godot, Unreal",
                "C#, C++ o GDScript según el motor",
                "Físicas, shaders, audio y diseño de mecánicas",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien programa jugabilidad, físicas y sistemas de juego.",
            ],
        },
    ],
    "blockchain": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Smart contracts: Solidity, Rust",
                "Ethereum, L2, wallets y explorers",
                "Criptografía aplicada y revisión de contratos",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien desarrolla contratos y aplicaciones sobre redes compartidas.",
            ],
        },
    ],
    "ciencia-de-datos": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Python: Pandas, NumPy, notebooks",
                "SQL y warehouses",
                "Visualización: Matplotlib, Seaborn, Tableau, Power BI",
                "Estadística aplicada a visualización",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien analiza, visualiza y comunica hallazgos a partir de datos.",
            ],
        },
    ],
    "machine-learning": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "PyTorch, scikit-learn, TensorFlow",
                "Preparación de datos y evaluación de modelos",
                "NLP, visión y transformers",
                "MLOps: versionado de datos y modelos",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien entrena, evalúa y pone en producción modelos.",
            ],
        },
    ],
    "data-engineering": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "SQL, dbt y orquestadores como Airflow",
                "Spark u otros motores de lote",
                "Warehouses e ingest",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien construye pipelines y tablas para el resto del equipo.",
            ],
        },
    ],
    "devops": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "Docker y Kubernetes",
                "CI/CD: GitHub Actions, GitLab CI",
                "Cloud: AWS, GCP, Azure o un VPS",
                "Terraform o Ansible, métricas y alertas",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien automatiza infraestructura, deploy y observación.",
            ],
        },
    ],
    "ciberseguridad": [
        {
            "heading": "Áreas principales",
            "items": [
                "AppSec: OWASP, autenticación y secretos fuera del repositorio",
                "Pentest y análisis de vulnerabilidades",
                "Redes, identidades y compliance",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien identifica y mitiga vulnerabilidades.",
            ],
        },
    ],
    "qa": [
        {
            "heading": "Tipos de testing",
            "items": [
                "Pruebas exploratorias y casos de regresión",
                "Unitarias, de integración y E2E (Playwright, Cypress, pytest)",
                "Pruebas de performance y criterio de publicación",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien diseña pruebas y valida que el software esté listo para publicar.",
            ],
        },
    ],
    "redes": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "TCP/IP, DNS, HTTP, TLS",
                "Routers, firewalls, VPN",
                "Redes cloud: VPC, load balancers, CDN",
                "Certificaciones habituales: CCNA, Network+",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien configura conectividad, DNS y seguridad de red.",
            ],
        },
    ],
    "soporte-tecnico": [
        {
            "heading": "Qué hace el rol",
            "items": [
                "Diagnosticar, documentar y escalar incidentes",
                "Primera línea con usuarios",
                "Linux, sistemas de tickets y documentación",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien diagnostica y escala incidentes con usuarios.",
            ],
        },
    ],
    "bases-de-datos": [
        {
            "heading": "Tecnologías principales",
            "items": [
                "PostgreSQL y MySQL",
                "Índices, planes de consulta, backups y réplicas",
                "Migraciones y mantenimiento",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien modela, indexa y opera la fuente de verdad.",
            ],
        },
    ],
    "diseno-ui-ux": [
        {
            "heading": "Qué cubre",
            "items": [
                "UI: jerarquía, tipografía, color y componentes",
                "UX: investigación, flujos, prototipos y pruebas con usuarios",
                "Figma, design systems y accesibilidad",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien investiga, prototipa y define la experiencia de uso.",
            ],
        },
    ],
    "product-management": [
        {
            "heading": "Responsabilidades",
            "items": [
                "Definir qué se construye y qué no",
                "Hablar con usuarios y recortar el alcance",
                "Roadmap, métricas e historias implementables",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien define problema, alcance y prioridad del producto.",
            ],
        },
    ],
    "project-management": [
        {
            "heading": "Metodologías y herramientas",
            "items": [
                "Scrum, Kanban y, en algunos equipos, SAFe",
                "Jira, Trello u otra herramienta de seguimiento",
                "Fechas, riesgos y seguimiento diario",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien coordina fechas, dependencias y riesgos.",
            ],
        },
    ],
    "tech-lead": [
        {
            "heading": "Responsabilidades",
            "items": [
                "Trabajo en el código y rumbo técnico",
                "Reviews, mentoría y estándares",
                "Explicar trade-offs a quienes no escriben el cambio",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien combina trabajo técnico con rumbo y mentoría del equipo.",
            ],
        },
    ],
    "engineering-management": [
        {
            "heading": "Responsabilidades",
            "items": [
                "Hiring, 1:1 y carga de trabajo",
                "Procesos y cultura del equipo",
                "Coordinación con producto y el resto de la organización",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien gestiona personas, hiring y foco del equipo.",
            ],
        },
    ],
    "arquitectura": [
        {
            "heading": "Responsabilidades",
            "items": [
                "Límites, contratos y formas que aguanten el cambio",
                "Selección de stack con criterios explícitos",
                "Documentar decisiones para que se puedan revisar",
            ],
        },
        {
            "heading": "Patrones habituales",
            "items": [
                "Capas, hexagonal, eventos y microservicios",
                "DDD y contextos acotados",
                "CQRS cuando el problema lo justifica",
            ],
        },
        {
            "heading": "A quién está orientado",
            "items": [
                "Quien define límites, contratos y evolución del sistema.",
            ],
        },
    ],
}

BOOKS = (
    (
        "The Pragmatic Programmer",
        "Andrew Hunt, David Thomas",
        1999,
        "Programación",
        "Libro sobre el oficio de programar: debugging, automatización, aprendizaje continuo y cómo tomar mejores decisiones día a día.",
        "https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/",
        "Programación\nOficio",
        1,
    ),
    (
        "Clean Code",
        "Robert C. Martin",
        2008,
        "Programación",
        "Guía para escribir código más legible: nombres claros, funciones chicas, tests y criterios para revisar un cambio.",
        "https://www.oreilly.com/library/view/clean-code-a/9780136083238/",
        "Programación\nCalidad",
        2,
    ),
    (
        "Designing Data-Intensive Applications",
        "Martin Kleppmann",
        2017,
        "Arquitectura",
        "Cómo se almacenan, replican y consultan datos a escala: consistencia, particionado y sistemas distribuidos.",
        "https://dataintensive.net/",
        "Arquitectura\nDatos",
        3,
    ),
    (
        "Domain-Driven Design",
        "Eric Evans",
        2003,
        "Arquitectura",
        "Cómo modelar software con el idioma del negocio: bounded contexts, lenguaje ubicuo y diseño táctico.",
        "https://www.domainlanguage.com/ddd/",
        "Arquitectura\nDDD",
        4,
    ),
    (
        "Refactoring",
        "Martin Fowler",
        1999,
        "Programación",
        "Catálogo de técnicas para cambiar la estructura del código sin cambiar el comportamiento, con olores y movimientos.",
        "https://refactoring.com/",
        "Programación\nCalidad",
        5,
    ),
    (
        "Accelerate",
        "Nicole Forsgren, Jez Humble, Gene Kim",
        2018,
        "DevOps",
        "Investigación sobre qué practican y miden los equipos que entregan software seguido y con estabilidad.",
        "https://itrevolution.com/product/accelerate/",
        "DevOps\nGestión",
        6,
    ),
    (
        "The Manager's Path",
        "Camille Fournier",
        2017,
        "Gestión",
        "Recorrido de la carrera de management en ingeniería: de tech lead a director, 1:1 y criterio técnico.",
        "https://www.oreilly.com/library/view/the-managers-path/9781491973882/",
        "Gestión\nLiderazgo",
        7,
    ),
    (
        "The Staff Engineer's Path",
        "Tanya Reilly",
        2022,
        "Gestión",
        "Cómo crecer como individual contributor senior: influencia, proyectos transversales y alcance sin pasar a management.",
        "https://www.oreilly.com/library/view/the-staff-engineers/9781098118723/",
        "Gestión\nCarrera",
        8,
    ),
    (
        "The Mythical Man-Month",
        "Frederick P. Brooks Jr.",
        1975,
        "Gestión",
        "Ensayos clásicos de gestión de proyectos de software, incluido por qué sumar gente a un proyecto atrasado lo atrasa más.",
        "https://en.wikipedia.org/wiki/The_Mythical_Man-Month",
        "Gestión\nProyectos",
        9,
    ),
    (
        "You Don't Know JS",
        "Kyle Simpson",
        2014,
        "Programación",
        "Serie sobre JavaScript por dentro: scope, closures, this y async. El material está publicado gratis en GitHub.",
        "https://github.com/getify/You-Dont-Know-JS",
        "Programación\nJavaScript",
        10,
    ),
    (
        "Shape Up",
        "Ryan Singer",
        2019,
        "Producto",
        "Método de producto de Basecamp: ciclos de seis semanas, definición del trabajo (shaping) y apuestas en lugar de un backlog continuo.",
        "https://basecamp.com/shapeup",
        "Producto\nGestión",
        11,
    ),
    (
        "Site Reliability Engineering",
        "Betsy Beyer et al.",
        2016,
        "DevOps",
        "Cómo Google opera sistemas en producción: SLIs y SLOs, error budgets, toil y trabajo de guardia.",
        "https://sre.google/sre-book/table-of-contents/",
        "DevOps\nSRE",
        12,
    ),
)

TOOLS = (
    (
        "Visual Studio Code",
        "Desarrollo",
        "Gratis",
        "Editor de código de Microsoft: Git integrado, debugging, resaltado de sintaxis y miles de extensiones. Corre en Windows, macOS y Linux.",
        "https://code.visualstudio.com/",
        "Editor\nJavaScript\nPython\nGit",
        1,
    ),
    (
        "Cursor",
        "IA",
        "Freemium",
        "Editor basado en VS Code con un agente de IA. Autocompletado, chat sobre el proyecto y cambios en varios archivos a la vez.",
        "https://cursor.com/",
        "Editor\nIA\nAgente",
        2,
    ),
    (
        "Claude",
        "IA",
        "Freemium",
        "Asistente de Anthropic para redactar, explicar código y discutir diseño. Funciona por chat; también hay API y agente en la terminal.",
        "https://claude.ai/",
        "IA\nAsistente",
        3,
    ),
    (
        "Docker",
        "DevOps",
        "Freemium",
        "Plataforma de contenedores: empaquetás la app con sus dependencias para que corra igual en cualquier máquina. Compose arma varios servicios juntos.",
        "https://www.docker.com/",
        "Contenedores\nDevOps",
        4,
    ),
    (
        "GitHub",
        "Desarrollo",
        "Freemium",
        "Alojamiento de repositorios Git con pull requests, issues y GitHub Actions para integrar y desplegar. Plan gratuito para uso personal.",
        "https://github.com/",
        "Git\nColaboración\nCI",
        5,
    ),
    (
        "Figma",
        "Diseño",
        "Freemium",
        "Diseño de interfaces y prototipos en el navegador, con comentarios y edición en simultáneo. Sirve para UI, flujos y handoff al código.",
        "https://www.figma.com/",
        "Diseño\nUI\nPrototipo",
        6,
    ),
    (
        "Postman",
        "Desarrollo",
        "Freemium",
        "Cliente para probar APIs HTTP: armás requests, guardás colecciones y compartís entornos con el equipo. Hay plan gratuito individual.",
        "https://www.postman.com/",
        "API\nHTTP\nTesting",
        7,
    ),
    (
        "PostgreSQL",
        "Desarrollo",
        "Gratis",
        "Base de datos relacional open source. SQL, transacciones, índices, JSON y réplicas. Es el motor que usa mucha web, incluida esta.",
        "https://www.postgresql.org/",
        "SQL\nDatos",
        8,
    ),
    (
        "Notion",
        "Productividad",
        "Freemium",
        "Espacio de trabajo con notas, wikis, bases de datos y tareas. Sirve para docs de equipo y seguimiento liviano de trabajo.",
        "https://www.notion.so/",
        "Notas\nDocs",
        9,
    ),
    (
        "Linear",
        "Productividad",
        "Freemium",
        "Gestor de issues, ciclos y roadmaps para equipos de software. Atajos de teclado y una UI pensada para ir rápido.",
        "https://linear.app/",
        "Issues\nSprints",
        10,
    ),
    (
        "Warp",
        "Desarrollo",
        "Freemium",
        "Terminal con bloques de output, autocompletado y ayuda de IA. Disponible para macOS, Linux y Windows.",
        "https://www.warp.dev/",
        "Terminal\nIA",
        11,
    ),
    (
        "Django",
        "Desarrollo",
        "Gratis",
        "Framework web de Python: ORM, panel de admin, autenticación y convenciones para armar backends. Open source y gratis.",
        "https://www.djangoproject.com/",
        "Python\nWeb\nBackend",
        12,
    ),
)


def enrich_hub(apps, schema_editor) -> None:
    """Fill specialty sheets and seed the other Recursos tabs."""
    specialty_model = apps.get_model("content", "TechSpecialty")
    for slug, sections in SECTIONS.items():
        specialty_model.objects.filter(slug=slug).update(sections=sections)

    catalog_model = apps.get_model("content", "CatalogEntry")
    now = timezone.now()
    catalog_model.objects.bulk_create(
        [
            catalog_model(
                kind="reading",
                title=title,
                authors=authors,
                year=year,
                category=category,
                summary=summary,
                url=url,
                tags=tags,
                order=order,
                is_published=True,
                created_at=now,
            )
            for title, authors, year, category, summary, url, tags, order in BOOKS
        ]
        + [
            catalog_model(
                kind="tool",
                title=title,
                category=category,
                pricing=pricing,
                summary=summary,
                url=url,
                tags=tags,
                order=order,
                is_published=True,
                created_at=now,
            )
            for title, category, pricing, summary, url, tags, order in TOOLS
        ]
    )


def rollback_hub(apps, schema_editor) -> None:
    """Clear seeded catalog rows and specialty sections."""
    specialty_model = apps.get_model("content", "TechSpecialty")
    specialty_model.objects.filter(slug__in=SECTIONS).update(sections=[])
    catalog_model = apps.get_model("content", "CatalogEntry")
    catalog_model.objects.filter(title__in=[row[0] for row in BOOKS + TOOLS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0015_techspecialty"),
    ]

    operations = [
        migrations.AddField(
            model_name="learningresource",
            name="duration",
            field=models.CharField(blank=True, max_length=40, verbose_name="duración"),
        ),
        migrations.AddField(
            model_name="learningresource",
            name="instructor",
            field=models.CharField(
                blank=True, max_length=160, verbose_name="dictado por"
            ),
        ),
        migrations.AddField(
            model_name="techspecialty",
            name="sections",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Lista de {"heading": "...", "items": ["...", "..."]}.',
                verbose_name="secciones",
            ),
        ),
        migrations.CreateModel(
            name="CatalogEntry",
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
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("reading", "Lectura"),
                            ("tool", "Herramienta"),
                            ("project", "Proyecto"),
                        ],
                        max_length=20,
                        verbose_name="tipo",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="título")),
                ("summary", models.TextField(verbose_name="descripción")),
                ("url", models.URLField(blank=True, verbose_name="enlace")),
                (
                    "category",
                    models.CharField(
                        blank=True, max_length=80, verbose_name="categoría"
                    ),
                ),
                (
                    "authors",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="autores"
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="año"
                    ),
                ),
                (
                    "pricing",
                    models.CharField(blank=True, max_length=40, verbose_name="precio"),
                ),
                (
                    "tags",
                    models.TextField(
                        blank=True,
                        help_text="Una etiqueta por línea.",
                        verbose_name="etiquetas",
                    ),
                ),
                (
                    "stack",
                    models.TextField(
                        blank=True,
                        help_text="Una tecnología por línea. Útil en proyectos.",
                        verbose_name="stack",
                    ),
                ),
                (
                    "extra",
                    models.CharField(blank=True, max_length=80, verbose_name="sello"),
                ),
                (
                    "order",
                    models.PositiveIntegerField(default=0, verbose_name="orden"),
                ),
                (
                    "is_published",
                    models.BooleanField(default=True, verbose_name="publicado"),
                ),
                ("created_at", models.DateTimeField(default=timezone.now)),
            ],
            options={
                "verbose_name": "ítem de catálogo",
                "verbose_name_plural": "ítems de catálogo",
                "ordering": ("kind", "order", "title"),
            },
        ),
        migrations.AddIndex(
            model_name="catalogentry",
            index=models.Index(
                fields=["kind", "is_published", "order"],
                name="content_cat_kind_9f1a2b_idx",
            ),
        ),
        migrations.RunPython(enrich_hub, rollback_hub),
    ]

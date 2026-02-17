<p align="center">
  <img src="saltadev/static/assets/img/logo.webp" alt="SaltaDev Logo" width="120" height="120">
</p>

<h1 align="center">SaltaDev Website</h1>

<p align="center">
  <strong>Plataforma web oficial de la comunidad de desarrolladores de Salta, Argentina</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.12">
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/django-5.2-green.svg?style=flat-square&logo=django&logoColor=white" alt="Django 5.2">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-purple.svg?style=flat-square" alt="Ruff">
  </a>
  <a href="https://github.com/biomejs/biome">
    <img src="https://img.shields.io/badge/format-biome-blue.svg?style=flat-square" alt="Biome">
  </a>
  <a href="https://pre-commit.com/">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white" alt="pre-commit">
  </a>
  <a href="http://mypy-lang.org/">
    <img src="https://img.shields.io/badge/type%20checked-mypy-blue.svg?style=flat-square" alt="mypy">
  </a>
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#configuración">Configuración</a> •
  <a href="#arquitectura">Arquitectura</a> •
  <a href="#despliegue">Despliegue</a> •
  <a href="#almacenamiento-de-imágenes">Imágenes</a> •
  <a href="#seguridad">Seguridad</a> •
  <a href="#seo">SEO</a> •
  <a href="#desarrollo">Desarrollo</a>
</p>

---

## Características

- **Autenticación completa** - Login, registro con verificación de email y recuperación de contraseña
- **Dashboard de usuario** - Panel personalizado con perfil, credencial digital y gestión de datos
- **Credencial digital** - Credencial verificable con QR code, descargable como PNG
- **Sistema de roles** - Miembro, Colaborador, Moderador y Administrador
- **Eventos** - Listado y gestión de eventos con workflow de aprobación
- **Notificaciones** - Sistema de notificaciones in-app para usuarios
- **Colaboradores** - Showcase de empresas y organizaciones aliadas
- **Staff** - Perfiles del equipo organizador
- **Código de conducta** - Reglamento de la comunidad

## Tech Stack

### Backend
| Tecnología | Versión | Descripción |
|------------|---------|-------------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) | 3.12 | Lenguaje principal |
| ![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white) | 5.2 | Framework web |
| ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) | 15+ | Base de datos |
| ![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat-square&logo=redis&logoColor=white) | 7+ | Cache y rate limiting |
| ![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) | 23.0 | WSGI Server |
| ![Cloudinary](https://img.shields.io/badge/-Cloudinary-3448C5?style=flat-square&logo=cloudinary&logoColor=white) | - | CDN de imágenes |

### Frontend
| Tecnología | Versión | Descripción |
|------------|---------|-------------|
| ![TailwindCSS](https://img.shields.io/badge/-TailwindCSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white) | 4.x | CSS compilado via django-tailwind-cli |
| ![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) | ES6+ | Interactividad |
| ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) | - | Templates Django |

### DevOps & Herramientas
| Tecnología | Descripción |
|------------|-------------|
| ![Render](https://img.shields.io/badge/-Render-46E3B7?style=flat-square&logo=render&logoColor=white) | Cloud hosting |
| ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Containerización |
| ![Nginx](https://img.shields.io/badge/-Nginx-269539?style=flat-square&logo=nginx&logoColor=white) | Reverse proxy |
| ![uv](https://img.shields.io/badge/-uv-DE5FE9?style=flat-square) | Package manager |

## Estructura del Proyecto

```
saltadev-website/
├── saltadev/                   # Django project root
│   ├── manage.py
│   ├── tailwind.config.js      # Configuración Tailwind CSS
│   ├── saltadev/               # Django settings package
│   │   ├── settings/
│   │   │   ├── base.py         # Configuración base
│   │   │   ├── local.py        # Desarrollo local
│   │   │   ├── development.py  # Desarrollo
│   │   │   ├── staging.py      # Staging
│   │   │   └── production.py   # Producción
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── home/                   # Landing page
│   ├── auth_login/             # Login
│   ├── auth_register/          # Registro + verificación email
│   ├── password_reset/         # Recuperación de contraseña
│   ├── users/                  # Modelo de usuario y perfil
│   ├── dashboard/              # Panel de usuario
│   ├── events/                 # Eventos
│   ├── benefits/               # Beneficios para miembros
│   ├── locations/              # Países y provincias
│   ├── content/                # Contenido (colaboradores, etc)
│   ├── code_of_conduct/        # Código de conducta
│   ├── user_notifications/     # Sistema de notificaciones
│   │
│   ├── static/                 # Archivos estáticos
│   │   └── css/
│   │       └── source.css      # CSS fuente para Tailwind
│   └── templates/              # Templates HTML
│
├── deploy/                     # Configuración de despliegue
│   └── render.yaml             # IaC para Render.com
├── build.sh                    # Script de build para Render
├── tests/                      # Tests con pytest
├── docker/                     # Configuración Docker
├── nginx/                      # Configuración Nginx
├── scripts/                    # Scripts de utilidad
│
├── pyproject.toml              # Dependencias y configuración
├── uv.lock                     # Lockfile
├── pytest.ini                  # Configuración pytest
├── mypy.ini                    # Configuración mypy
├── biome.json                  # Configuración Biome
└── .pre-commit-config.yaml     # Pre-commit hooks
```

## Instalación

### Requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- PostgreSQL 15+ (producción) o SQLite (desarrollo)
- Redis 7+ (opcional, para rate limiting)

### Setup Local

```bash
# Clonar repositorio
git clone https://github.com/saltadev/saltadev-website.git
cd saltadev-website

# Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate
uv pip install -e .[dev]

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con tus valores

# Aplicar migraciones
cd saltadev
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## Configuración

### Variables de Entorno

Crear archivo `.env.local` en la raíz del proyecto:

```env
# Django
DJANGO_ENV=local
SECRET_KEY=tu-secret-key-muy-segura
DEBUG=True

# Base de datos (opcional para local, usa SQLite por defecto)
DATABASE_URL=postgres://user:pass@localhost:5432/saltadev

# Email - Opción 1: SMTP (Gmail)
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password

# Email - Opción 2: Resend (requerido en Render.com free tier)
RESEND_API_KEY=re_xxx
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# reCAPTCHA v2
RECAPTCHA_V2_SITE_KEY=tu-site-key
RECAPTCHA_V2_SECRET=tu-secret-key

# URL del sitio
SITE_URL=http://localhost:8000
```

### Entornos Disponibles

| Entorno | Archivo | Descripción |
|---------|---------|-------------|
| `local` | `.env.local` | Desarrollo local con DEBUG=True |
| `development` | `.env.development` | Servidor de desarrollo |
| `staging` | `.env.staging` | Pre-producción |
| `production` | `.env.production` | Producción |

## Arquitectura

### Diagrama de Aplicaciones

```mermaid
flowchart TB
    subgraph Public["Páginas Públicas"]
        home[Home]
        events[Eventos]
        coc[Código de Conducta]
        credential[Credencial Pública]
    end

    subgraph Auth["Autenticación"]
        login[Login]
        register[Registro]
        verify[Verificación Email]
        reset[Password Reset]
    end

    subgraph Private["Área Privada"]
        dashboard[Dashboard]
        profile[Perfil]
    end

    subgraph Core["Core"]
        users[Users Model]
        locations[Locations]
        content[Content]
    end

    home --> login
    home --> register
    register --> verify
    verify --> dashboard
    login --> dashboard
    login --> reset
    reset --> login
    dashboard --> profile
    dashboard --> credential

    users --> locations
    users --> content
```

### Flujo de Verificación de Email

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Registro
    participant US as Users
    participant M as Email

    U->>R: Envía formulario de registro
    R->>US: Crea usuario (email_confirmed=False)
    US->>M: Envía código de verificación (6 dígitos)
    M-->>U: Email con código
    U->>US: Ingresa código
    US->>US: Verifica código y confirma email
    US->>U: Login automático → Dashboard
```

### Flujo de Recuperación de Contraseña

```mermaid
sequenceDiagram
    participant U as Usuario
    participant PR as Password Reset
    participant M as Email

    U->>PR: Solicita recuperación
    PR->>PR: Genera token (válido 10 min)
    PR->>M: Envía email con link
    M-->>U: Email con link de reset
    U->>PR: Abre link y envía nueva contraseña
    PR->>PR: Valida token y actualiza password
    PR->>U: Redirige a login con mensaje de éxito
```

### Sistema de Notificaciones

El proyecto usa **django-notifications-hq** para notificaciones in-app:

```python
from notifications.signals import notify
notify.send(sender, recipient=user, verb="aprobó tu evento", target=event)
```

**Endpoints disponibles:**

| Endpoint | Descripción |
|----------|-------------|
| `/notificaciones/` | Lista de notificaciones del usuario |
| `/notificaciones/marcar-leidas/` | Marcar todas como leídas |
| `/notificaciones/<id>/marcar-leida/` | Marcar una como leída |

### Gestión de Eventos

Los eventos tienen un workflow de aprobación con tres estados:

| Estado | Descripción |
|--------|-------------|
| `PENDING` | Evento creado, esperando aprobación |
| `APPROVED` | Evento aprobado, visible públicamente |
| `REJECTED` | Evento rechazado |

**Flujo:**
1. Usuario crea evento → estado `PENDING`
2. Staff/Admin revisa en el admin
3. Al aprobar/rechazar → se envía notificación automática al creador

## Despliegue

### Render.com (Recomendado)

El proyecto incluye configuración Infrastructure as Code (IaC) para Render.com en `deploy/render.yaml`.

Ver [deploy/RENDER.md](deploy/RENDER.md) para la guía completa de despliegue.

| Servicio | Tipo | Plan | Descripción |
|----------|------|------|-------------|
| `saltadev-db` | PostgreSQL | Free | Base de datos |
| `saltadev-redis` | Redis | Free | Cache y rate limiting |
| `saltadev-website` | Web Service | Free | Aplicación Django |

#### Deploy automático

1. Conectar repositorio en [Render Dashboard](https://dashboard.render.com)
2. Seleccionar "Blueprint" y apuntar a `deploy/render.yaml`
3. Configurar variables secretas (Cloudinary, Email, reCAPTCHA)
4. Deploy!

#### Variables de entorno

Las siguientes se generan automáticamente:
- `DATABASE_URL` - Conexión a PostgreSQL
- `REDIS_URL` - Conexión a Redis
- `SECRET_KEY` - Generada automáticamente

Las siguientes requieren configuración manual:
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- `RESEND_API_KEY`, `DEFAULT_FROM_EMAIL`
- `RECAPTCHA_V2_SITE_KEY`, `RECAPTCHA_V2_SECRET`
- `SITE_URL`

#### Script de build

El archivo `build.sh` ejecuta durante el deploy:
```bash
pip install -r requirements.txt
python manage.py tailwind build
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata locations
```

## Almacenamiento de Imágenes

### Cloudinary CDN

El proyecto usa Cloudinary para almacenar y servir imágenes (avatares, etc.):

| Característica | Detalle |
|----------------|---------|
| **CDN Global** | Servido desde edge locations mundiales |
| **Formato automático** | WebP/AVIF según el navegador |
| **Calidad automática** | Optimización sin pérdida visible |
| **Transformaciones on-the-fly** | No consume créditos de transformación |

#### Estrategia de transformaciones

Las imágenes se suben SIN transformación y se procesan on-the-fly via URL:

```
https://res.cloudinary.com/{cloud}/upload/w_400,h_400,c_fill,g_face,q_auto,f_auto/{path}
```

Esto evita consumir los 25 créditos/mes del free tier, ya que las transformaciones
on-the-fly no consumen créditos de transformación.

#### Desarrollo local

En desarrollo local, las imágenes usan Django `ImageField` y se guardan en `static/assets/img/`:

| Tipo | Ruta |
|------|------|
| Colaboradores | `static/assets/img/partners/` |
| Staff | `static/assets/img/staff/` |
| Avatares | `media/avatars/` |

Cloudinary es **opcional** en desarrollo. Si no se configuran las credenciales,
las imágenes se guardan localmente.

## Seguridad

### Medidas Implementadas

| Medida | Descripción |
|--------|-------------|
| **CSRF Protection** | Token CSRF en todos los formularios |
| **reCAPTCHA v2** | Protección contra bots en login/registro |
| **Rate Limiting** | Límite de intentos por IP, email y fingerprint |
| **Password Validation** | Validación de fortaleza de contraseñas |
| **Token Expiration** | Tokens de recuperación expiran en 10 minutos |
| **Single-use Tokens** | Tokens de un solo uso para reset de contraseña |
| **Email Verification** | Verificación obligatoria de email |
| **No User Enumeration** | Misma respuesta para emails existentes y no existentes |
| **Disposable Email Block** | Rechaza emails de proveedores temporales (10minutemail, etc.) |
| **Secure Headers** | Headers de seguridad configurados |
| **HTTPS Only** | Forzado en producción |

### django-axes

Protección contra ataques de fuerza bruta:
- Bloqueo después de 5 intentos fallidos
- Bloqueo por IP y por nombre de usuario
- Desbloqueo automático después de 1 hora

## SEO

### Optimizaciones Implementadas

| Característica | Descripción |
|----------------|-------------|
| **robots.txt** | Control de crawlers con reglas Disallow para áreas privadas |
| **sitemap.xml** | Sitemap generado dinámicamente con `django.contrib.sitemaps` |
| **JSON-LD** | Schema Organization en la homepage para rich snippets |
| **Meta descriptions** | Descripciones únicas y optimizadas por página |
| **Canonical URLs** | URLs canónicas en todas las páginas públicas |
| **Open Graph** | Meta tags para compartir en Facebook y LinkedIn |
| **Twitter Cards** | Meta tags para compartir en Twitter/X |
| **Redirects 301** | Links sociales con redirect permanente para tracking |

### Archivos Clave

```
saltadev/
├── saltadev/
│   ├── sitemaps.py              # Configuración de sitemap.xml
│   └── urls.py                  # Rutas de robots.txt y sitemap
│
├── templates/
│   ├── robots.txt               # Template de robots.txt
│   └── includes/
│       ├── head.html            # Meta tags, OG y Twitter Cards
│       └── structured_data/
│           └── organization.html # JSON-LD Organization schema
│
└── content/
    └── redirects.py             # Redirects 301 para redes sociales
```

## Desarrollo

### Comandos Útiles

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar servidor
python manage.py runserver

# Ejecutar tests
pytest -q

# Tests con coverage
pytest --cov=saltadev --cov-report=html

# Linting y formato
pre-commit run --all-files

# Solo ruff
ruff check .
ruff format .

# Solo mypy
mypy saltadev/

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Limpiar tokens expirados
python manage.py cleanup_expired_tokens
```

### Pre-commit Hooks

El proyecto usa pre-commit con los siguientes hooks:

| Hook | Descripción |
|------|-------------|
| **ruff** | Linting y formato de Python |
| **biome** | Formato de JS/CSS/HTML y linting |
| **bandit** | Análisis de seguridad en Python |
| **detect-secrets** | Detección de secretos en el código |
| **mypy** | Chequeo de tipos estático |

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### Estructura de Tests

```
tests/
├── conftest.py                     # Fixtures globales
├── test_password_validation.py     # Validación de contraseñas
├── test_password_reset_validation.py
├── test_users/                     # Tests del módulo users
│   ├── test_models.py
│   └── test_views.py
└── ...
```

## Docker

El proyecto usa un **Dockerfile unificado** con docker-compose para cada ambiente.

### Estructura

```
docker/
├── Dockerfile                    # Dockerfile unificado (multi-stage)
├── entrypoint.sh                 # Script de entrada (migraciones, collectstatic)
├── docker-compose.local.yml      # Desarrollo local con hot reload
├── docker-compose.dev.yml        # Servidor de desarrollo
├── docker-compose.staging.yml    # Staging con SSL
└── docker-compose.prod.yml       # Producción con SSL
```

### Desarrollo Local

```bash
# Crear archivo .env.local (si no existe)
cp saltadev/.env.local.example saltadev/.env.local

# Iniciar todos los servicios (Django + PostgreSQL + Redis)
docker compose -f docker/docker-compose.local.yml up

# Ejecutar en background
docker compose -f docker/docker-compose.local.yml up -d

# Ver logs
docker compose -f docker/docker-compose.local.yml logs -f web

# Detener servicios
docker compose -f docker/docker-compose.local.yml down

# Eliminar volúmenes (reset de base de datos)
docker compose -f docker/docker-compose.local.yml down -v
```

El ambiente local incluye:
- **Hot reload**: los cambios en `saltadev/` se reflejan sin rebuild
- **Migraciones automáticas**: se ejecutan al iniciar el contenedor
- **Fixtures**: se cargan automáticamente (locations)
- **PostgreSQL**: puerto 5432 expuesto para acceso directo
- **Redis**: puerto 6379 expuesto para acceso directo

### Otros Ambientes

```bash
# Development (gunicorn + nginx)
docker compose -f docker/docker-compose.dev.yml up

# Staging (gunicorn + nginx + SSL)
docker compose -f docker/docker-compose.staging.yml up

# Production (gunicorn + nginx + SSL + 4 workers)
docker compose -f docker/docker-compose.prod.yml up
```

### Comparación de Ambientes

| Ambiente | Servidor | Workers | Hot Reload | SSL |
|----------|----------|---------|------------|-----|
| local | runserver | 1 | Sí | No |
| development | gunicorn | 2 | No | No |
| staging | gunicorn | 2 | No | Sí |
| production | gunicorn | 4 | No | Sí |

## Tailwind CSS

El proyecto usa **django-tailwind-cli** para compilar Tailwind CSS sin necesidad de Node.js.

### Desarrollo Local

```bash
# Compilar CSS una vez
cd saltadev
python manage.py tailwind build

# Watch mode (recompila automáticamente)
python manage.py tailwind watch
```

### Docker

El CSS se compila automáticamente al iniciar los containers via `entrypoint.sh`.

### Configuración

| Archivo | Descripción |
|---------|-------------|
| `saltadev/tailwind.config.js` | Colores, fuentes, sombras personalizadas |
| `saltadev/static/css/source.css` | Directivas @tailwind |
| `saltadev/static/css/tailwind.css` | Output (gitignored) |

## API de Credenciales

### Credencial Pública

```
GET /credencial/<public_id>/
```

Muestra la credencial pública de un usuario. Incluye:
- Foto de perfil
- Nombre completo
- Rol en la comunidad
- Estado de verificación
- DNI (si está configurado)
- ID de miembro
- Fecha de registro
- Ubicación
- Código QR verificable

La credencial se puede descargar como PNG o compartir.

## Emails

### Proveedores Soportados

| Proveedor | Backend | Cuándo usar |
|-----------|---------|-------------|
| **SMTP (Gmail)** | `django.core.mail.backends.smtp.EmailBackend` | Desarrollo local |
| **Resend** | `anymail.backends.resend.EmailBackend` | Render.com (SMTP bloqueado) |

El sistema detecta automáticamente qué backend usar según `RESEND_API_KEY`:
- Si está configurado → usa Resend via HTTP API
- Si no → usa SMTP tradicional

### Templates de Email

Los templates HTML se encuentran en `templates/emails/`:

| Template | Uso |
|----------|-----|
| `verification.html` | Código de verificación de email |
| `password_reset.html` | Link de recuperación de contraseña |

Los emails incluyen fallback de texto plano y el logo de SaltaDev.

## Contribuir

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Guía de Estilo

- **Python**: Seguir PEP 8, usar ruff para linting
- **JavaScript**: Formato con Biome
- **Commits**: Mensajes descriptivos en español o inglés
- **Código**: Código en inglés, UI en español

## Licencia

Este proyecto es propiedad de la comunidad SaltaDev.

---

<p align="center">
  Hecho con ❤️ en Salta, Argentina
</p>

<p align="center">
  <a href="https://salta.dev.ar">salta.dev.ar</a> •
  <a href="https://github.com/saltadev">GitHub</a> •
  <a href="https://linkedin.com/company/saltadev">LinkedIn</a> •
  <a href="https://instagram.com/saltadev">Instagram</a>
</p>

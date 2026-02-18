# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/claude-code) when working with this codebase.

## Project Overview

SaltaDev Website - Community website for SaltaDev (Salta, Argentina). Built with Django 5.2, featuring custom authentication with email verification, rate limiting, reCAPTCHA v2, password reset, events management with approval workflow, staff profiles, and in-app notifications.

## Key Architecture

```
saltadev-website/
├── saltadev/                    # Django project root (contains manage.py)
│   ├── saltadev/                # Django settings package
│   │   └── settings/
│   │       ├── base.py          # Shared settings
│   │       ├── local.py         # Local development
│   │       ├── development.py   # Development server
│   │       ├── staging.py       # Staging environment
│   │       └── production.py    # Production (Render.com)
│   ├── home/                    # Landing page
│   ├── events/                  # Events management
│   ├── users/                   # Custom User model and Profile
│   ├── auth_login/              # Login views
│   ├── auth_register/           # Registration with email verification
│   ├── password_reset/          # Password reset flow
│   ├── content/                 # Site content (links, etc.)
│   ├── locations/               # Argentine provinces/cities
│   ├── dashboard/               # User dashboard
│   ├── benefits/                # Member benefits
│   └── user_notifications/      # Notification system
├── tests/                       # Pytest tests (outside Django root)
└── deploy/                      # Deployment configs
```

## Development Commands

```bash
# Setup
uv sync                                    # Install dependencies
cd saltadev && python manage.py migrate    # Apply migrations
cd saltadev && python manage.py runserver  # Start dev server

# Testing
pytest                                     # Run all tests
pytest tests/test_users.py -v              # Run specific test file

# Code quality (run automatically via pre-commit)
pre-commit run --all-files                 # Run all checks
uv run ruff check saltadev                 # Linting only
uv run ruff format saltadev                # Formatting only

# Tailwind CSS
cd saltadev && python manage.py tailwind build   # Build CSS
cd saltadev && python manage.py tailwind watch   # Watch mode
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR to main:
- pytest with coverage
- ruff check/format
- mypy type checking
- bandit security scan

```bash
# Run CI checks locally
uv run pytest --cov=saltadev
uv run ruff check saltadev && uv run ruff format --check saltadev
uv run mypy saltadev
uv run bandit -r saltadev -x "**/tests/**"
```

## Healthcheck

Endpoint `/health/` returns JSON with Django, PostgreSQL, and Redis status.
Used by Render.com for service monitoring.

## Code Conventions

### Language
- **Code**: English (variables, functions, classes, comments, docstrings)
- **UI/Templates**: Spanish (user-facing text stays in Spanish)
- **Model verbose_name**: Spanish (for Django admin)

### Python Style
- Type annotations on all functions
- Docstrings on all public functions/classes
- Ruff rules: E, F, I, B, UP, SIM, RUF

### Test Imports
Tests are in `/tests/` (outside Django root). Use direct app imports:
```python
# Correct
from users.models import User, Profile

# Wrong
from saltadev.users.models import User, Profile
```

## External Services

| Service | Purpose | Config |
|---------|---------|--------|
| Cloudinary | Image storage/CDN | `CLOUDINARY_*` env vars |
| Resend | Transactional email | `RESEND_API_KEY` |
| reCAPTCHA v2 | Form protection | `RECAPTCHA_V2_*` env vars |
| Redis | Cache & sessions | `REDIS_URL` |
| PostgreSQL | Database | `DATABASE_URL` |
| django-csp | CSP headers (production) | Middleware in production.py |

## Common Patterns

### Email Sending
Uses Resend via django-anymail (SMTP ports blocked on Render):
```python
from django.core.mail import send_mail
send_mail(subject, message, from_email, [to_email])
```

### Image Uploads
Uses Cloudinary with on-the-fly transformations:
```python
from cloudinary import CloudinaryImage
CloudinaryImage(public_id).build_url(transformation=[...])
```

### Rate Limiting
django-axes handles login attempt limiting (5 attempts, 1 hour lockout).

### Notifications
Uses django-notifications-hq for in-app notifications:
```python
from notifications.signals import notify
notify.send(sender, recipient=user, verb="Message", target=object)
```

### Image Uploads (Local Dev)
In local development, images use Django's ImageField stored in `static/assets/img/`:
- Collaborator images: `static/assets/img/partners/`
- Staff photos: `static/assets/img/staff/`

In production, images are stored in Cloudinary.

## Deployment

Production runs on Render.com (free tier). See `deploy/RENDER.md` for full guide.

Key files:
- `deploy/render.yaml` - Infrastructure as Code
- `build.sh` - Build script (Tailwind, collectstatic, migrate)

## Performance Optimizations

- **Database indexes**: Event (status, creator, event_start_date), Benefit (is_active, creator), User (email_confirmed, role)
- **Query optimization**: Views use `select_related()` to avoid N+1 queries
- **View caching**: Home page cached for 1 minute

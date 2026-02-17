# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/claude-code) when working with this codebase.

## Project Overview

SaltaDev Website - Community website for SaltaDev (Salta, Argentina). Built with Django 5.2, featuring custom authentication with email verification, rate limiting, reCAPTCHA v2, password reset, events management, and staff profiles.

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
│   └── benefits/                # Member benefits
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

## Deployment

Production runs on Render.com (free tier). See `deploy/RENDER.md` for full guide.

Key files:
- `deploy/render.yaml` - Infrastructure as Code
- `build.sh` - Build script (Tailwind, collectstatic, migrate)

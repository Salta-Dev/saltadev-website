#!/usr/bin/env bash
# Verify that the Django environment is correctly configured.
set -euo pipefail

ENV="${1:-local}"

echo "=== Verifying environment: $ENV ==="

case "$ENV" in
    local)
        SETTINGS_MODULE="saltadev.settings.local"
        ;;
    development)
        SETTINGS_MODULE="saltadev.settings.development"
        ;;
    staging)
        SETTINGS_MODULE="saltadev.settings.staging"
        ;;
    production)
        SETTINGS_MODULE="saltadev.settings.production"
        ;;
    *)
        echo "Unknown environment: $ENV"
        echo "Usage: $0 [local|development|staging|production]"
        exit 1
        ;;
esac

export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"

echo "1. Settings module: $SETTINGS_MODULE"

echo "2. Running Django system checks..."
uv run python saltadev/manage.py check 2>&1

echo "3. Verifying settings can be imported..."
PYTHONPATH=saltadev uv run python -c "from django.conf import settings; print(f'   DEBUG={settings.DEBUG}'); print(f'   DATABASES={list(settings.DATABASES.keys())}'); print(f'   ALLOWED_HOSTS={settings.ALLOWED_HOSTS}')"

echo ""
echo "=== Environment $ENV verified successfully ==="

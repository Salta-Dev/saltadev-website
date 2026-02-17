#!/bin/bash
set -e

cd /app

# Build Tailwind CSS (needed for local dev due to volume mount)
echo "Building Tailwind CSS..."
uv run python saltadev/manage.py tailwind build

# Run migrations
echo "Running migrations..."
uv run python saltadev/manage.py migrate --noinput

# Collect static files (skip for local development)
if [ "$DJANGO_SETTINGS_MODULE" != "saltadev.settings.local" ]; then
    echo "Collecting static files..."
    uv run python saltadev/manage.py collectstatic --noinput
fi

# Load fixtures if requested
if [ "$LOAD_FIXTURES" = "true" ]; then
    echo "Loading fixtures..."
    uv run python saltadev/manage.py loaddata locations
fi

# Execute the command passed to the container
exec "$@"

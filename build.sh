#!/usr/bin/env bash
# Build script for Render.com deployment
set -o errexit

# Install uv package manager
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Install production dependencies only (no dev dependencies)
echo "Installing dependencies with uv..."
uv sync --no-dev --frozen

# Generate SECRET_KEY if not set (for dev/staging/production environments)
if [ -z "$SECRET_KEY" ]; then
    echo "SECRET_KEY not set, generating a secure random key..."
    export SECRET_KEY=$(uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo "SECRET_KEY generated successfully"
fi

# Build and deploy Django
cd saltadev
uv run python manage.py tailwind build
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate
uv run python manage.py loaddata locations
uv run python manage.py configure_site

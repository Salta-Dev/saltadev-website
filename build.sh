#!/usr/bin/env bash
# Build script for Render.com deployment
set -o errexit

pip install -r requirements.txt

# Generate SECRET_KEY if not set (for dev/staging/production environments)
if [ -z "$SECRET_KEY" ]; then
    echo "SECRET_KEY not set, generating a secure random key..."
    export SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo "SECRET_KEY generated successfully"
fi

cd saltadev
python manage.py tailwind build
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata locations

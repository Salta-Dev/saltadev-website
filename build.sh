#!/usr/bin/env bash
# Build script for Render.com deployment
set -o errexit

pip install -r requirements.txt

cd saltadev
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata locations

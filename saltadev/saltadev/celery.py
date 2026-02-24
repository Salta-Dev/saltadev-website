"""
Celery configuration for saltadev project.

Provides asynchronous task execution for email sending and other background jobs.
"""

import os

from celery import Celery

# Set default Django settings module for celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saltadev.settings.local")

app = Celery("saltadev")

# Use CELERY_ prefix for all celery-related settings in Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()

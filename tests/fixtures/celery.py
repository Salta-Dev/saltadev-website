"""Celery test fixtures."""

import pytest


@pytest.fixture(autouse=True)
def celery_eager_mode(settings):
    """Run all Celery tasks synchronously during tests."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

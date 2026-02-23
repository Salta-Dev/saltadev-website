"""Notification-related fixtures for testing."""

import pytest
from notifications.models import Notification


@pytest.fixture
def notification(db, verified_user, collaborator_user):
    """Create and return a notification for a user."""
    return Notification.objects.create(
        recipient=verified_user,
        actor=collaborator_user,
        verb="created a new benefit",
        description="Test Benefit",
        unread=True,
    )


@pytest.fixture
def read_notification(db, verified_user, collaborator_user):
    """Create and return a read notification."""
    return Notification.objects.create(
        recipient=verified_user,
        actor=collaborator_user,
        verb="created a new benefit",
        description="Read Benefit",
        unread=False,
    )


@pytest.fixture
def unread_notifications(db, verified_user, collaborator_user):
    """Create and return multiple unread notifications."""
    notifications = []
    for i in range(5):
        notifications.append(
            Notification.objects.create(
                recipient=verified_user,
                actor=collaborator_user,
                verb=f"notification {i}",
                description=f"Description {i}",
                unread=True,
            )
        )
    return notifications


@pytest.fixture
def other_user_notification(db, collaborator_user, moderator_user):
    """Create a notification for a different user."""
    return Notification.objects.create(
        recipient=collaborator_user,
        actor=moderator_user,
        verb="other user notification",
        description="Not for verified_user",
        unread=True,
    )

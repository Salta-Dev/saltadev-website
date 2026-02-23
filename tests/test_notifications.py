"""Tests for user notifications."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestNotificationViews:
    """Tests for notification views."""

    def test_list_requires_login(self, client):
        """Test notification list requires authentication."""
        response = client.get(reverse("user_notifications:list"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_list_returns_200_for_authenticated(self, client, verified_user):
        """Test authenticated user can access notification list."""
        client.force_login(verified_user)
        response = client.get(reverse("user_notifications:list"))
        assert response.status_code == 200

    def test_list_shows_own_notifications(
        self, client, verified_user, notification, other_user_notification
    ):
        """Test list shows only user's own notifications."""
        client.force_login(verified_user)
        response = client.get(reverse("user_notifications:list"))
        assert notification.verb in response.content.decode()
        assert other_user_notification.verb not in response.content.decode()

    def test_list_unread_count(self, client, verified_user, unread_notifications):
        """Test list shows correct unread count."""
        client.force_login(verified_user)
        response = client.get(reverse("user_notifications:list"))
        assert response.context["unread_count"] == 5

    def test_mark_as_read_own_notification(self, client, verified_user, notification):
        """Test marking own notification as read."""
        client.force_login(verified_user)
        assert notification.unread is True

        response = client.post(
            reverse("user_notifications:mark_as_read", kwargs={"notification_id": notification.pk})
        )
        assert response.status_code == 302

        notification.refresh_from_db()
        assert notification.unread is False

    def test_mark_as_read_others_notification_404(
        self, client, verified_user, other_user_notification
    ):
        """Test cannot mark others' notification as read."""
        client.force_login(verified_user)
        response = client.post(
            reverse(
                "user_notifications:mark_as_read",
                kwargs={"notification_id": other_user_notification.pk},
            )
        )
        assert response.status_code == 404

    def test_mark_all_as_read(self, client, verified_user, unread_notifications):
        """Test marking all notifications as read."""
        client.force_login(verified_user)

        # Verify all are unread
        for n in unread_notifications:
            assert n.unread is True

        response = client.post(reverse("user_notifications:mark_all_as_read"))
        assert response.status_code == 302

        # Verify all are now read
        for n in unread_notifications:
            n.refresh_from_db()
            assert n.unread is False

    def test_mark_as_read_requires_post(self, client, verified_user, notification):
        """Test mark as read requires POST method."""
        client.force_login(verified_user)
        response = client.get(
            reverse("user_notifications:mark_as_read", kwargs={"notification_id": notification.pk})
        )
        assert response.status_code == 405

    def test_mark_all_as_read_requires_post(self, client, verified_user):
        """Test mark all as read requires POST method."""
        client.force_login(verified_user)
        response = client.get(reverse("user_notifications:mark_all_as_read"))
        assert response.status_code == 405


@pytest.mark.django_db
class TestNotificationModel:
    """Tests for Notification model behavior."""

    def test_notification_creation(self, notification):
        """Test notification is created correctly."""
        assert notification.unread is True
        assert notification.verb == "created a new benefit"

    def test_read_notification(self, read_notification):
        """Test read notification has unread=False."""
        assert read_notification.unread is False

    def test_mark_as_read(self, notification):
        """Test mark_as_read method."""
        assert notification.unread is True
        notification.mark_as_read()
        assert notification.unread is False

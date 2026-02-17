"""Context processors for user notifications."""

from django.http import HttpRequest


def unread_notifications_count(request: HttpRequest) -> dict[str, int]:
    """Add unread notifications count to the template context.

    Returns:
        Dictionary with 'unread_notifications_count' key.
    """
    if request.user.is_authenticated:
        return {
            "unread_notifications_count": request.user.notifications.unread().count()  # type: ignore[attr-defined]
        }
    return {"unread_notifications_count": 0}

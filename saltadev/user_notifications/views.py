"""Views for user notifications."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from notifications.models import Notification


@login_required
def notification_list(request: HttpRequest) -> HttpResponse:
    """Display list of user notifications.

    Shows all notifications for the current user, grouped by read status.
    """
    notifications = request.user.notifications.all()[:50]  # type: ignore[union-attr]
    unread_count = request.user.notifications.unread().count()  # type: ignore[union-attr]

    return render(
        request,
        "dashboard/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_as_read(request: HttpRequest, notification_id: int) -> HttpResponseRedirect:
    """Mark a single notification as read.

    Args:
        notification_id: ID of the notification to mark as read.
    """
    notification = get_object_or_404(
        Notification, pk=notification_id, recipient=request.user
    )
    notification.mark_as_read()
    return redirect(reverse("user_notifications:list"))


@login_required
def mark_all_as_read(request: HttpRequest) -> HttpResponseRedirect:
    """Mark all notifications as read for the current user."""
    request.user.notifications.mark_all_as_read()  # type: ignore[union-attr]
    return redirect(reverse("user_notifications:list"))

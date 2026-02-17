"""URL configuration for user notifications."""

from django.urls import path

from . import views

app_name = "user_notifications"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("<int:notification_id>/leer/", views.mark_as_read, name="mark_as_read"),
    path("leer-todas/", views.mark_all_as_read, name="mark_all_as_read"),
]

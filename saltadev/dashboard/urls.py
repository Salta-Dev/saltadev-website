"""URL configuration for dashboard app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("perfil/editar/", views.profile_edit_view, name="profile_edit"),
]

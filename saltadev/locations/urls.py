"""URL configuration for locations app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "api/provinces/<str:country_code>/",
        views.provinces_by_country,
        name="provinces_by_country",
    ),
]

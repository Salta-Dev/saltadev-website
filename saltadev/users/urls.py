from django.urls import path

from . import views

urlpatterns = [
    path("", views.verify_email, name="verify_email"),
    path("clear-rate-limits/", views.clear_rate_limits_view, name="clear_rate_limits"),
]

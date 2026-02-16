from django.urls import path

from . import views

urlpatterns = [
    path("", views.request_reset_view, name="password_reset_request"),
    path("confirm/", views.confirm_reset_view, name="password_reset_confirm"),
]

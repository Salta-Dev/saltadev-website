from django.urls import path

from auth_register import views

urlpatterns = [
    path("", views.register_view, name="register"),
]

from django.urls import path

from auth_login import views

urlpatterns = [
    path("", views.login_view, name="login"),
]

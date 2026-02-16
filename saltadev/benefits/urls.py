"""URL configuration for the benefits app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.benefits_list, name="benefits_list"),
    path("mis-beneficios/", views.benefits_my_list, name="benefits_my_list"),
    path("crear/", views.benefit_create, name="benefit_create"),
    path("<int:pk>/", views.benefit_detail, name="benefit_detail"),
    path("<int:pk>/editar/", views.benefit_edit, name="benefit_edit"),
    path("<int:pk>/eliminar/", views.benefit_delete, name="benefit_delete"),
    path(
        "<int:pk>/toggle-active/",
        views.benefit_toggle_active,
        name="benefit_toggle_active",
    ),
]

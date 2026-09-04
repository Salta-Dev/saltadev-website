from django.urls import path

from home import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recursos/", views.resources, name="resources"),
    path(
        "recursos/especialidades/",
        views.resource_specialties,
        name="resource_specialties",
    ),
    path("recursos/lectura/", views.resource_reading, name="resource_reading"),
    path("recursos/herramientas/", views.resource_tools, name="resource_tools"),
    path("recursos/proyectos/", views.resource_projects, name="resource_projects"),
]

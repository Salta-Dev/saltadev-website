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
    path(
        "recursos/mis-propuestas/",
        views.my_resource_proposals,
        name="my_resource_proposals",
    ),
    path(
        "recursos/pendientes/",
        views.pending_resource_proposals,
        name="pending_resource_proposals",
    ),
    path(
        "recursos/catalogo/<int:pk>/aprobar/",
        views.catalog_proposal_approve,
        name="catalog_proposal_approve",
    ),
    path(
        "recursos/catalogo/<int:pk>/rechazar/",
        views.catalog_proposal_reject,
        name="catalog_proposal_reject",
    ),
    path(
        "recursos/cursos/<int:pk>/aprobar/",
        views.course_proposal_approve,
        name="course_proposal_approve",
    ),
    path(
        "recursos/cursos/<int:pk>/rechazar/",
        views.course_proposal_reject,
        name="course_proposal_reject",
    ),
]

from django.urls import path

from events import views

urlpatterns = [
    path("", views.events_list, name="events"),
    path("mis-eventos/", views.my_events, name="my_events"),
    path("pendientes/", views.pending_events, name="pending_events"),
    path("crear/", views.event_create, name="event_create"),
    path("<int:pk>/editar/", views.event_edit, name="event_edit"),
    path("<int:pk>/eliminar/", views.event_delete, name="event_delete"),
    path("<int:pk>/aprobar/", views.event_approve, name="event_approve"),
    path("<int:pk>/rechazar/", views.event_reject, name="event_reject"),
]

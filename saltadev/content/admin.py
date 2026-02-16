from django.contrib import admin

from .models import Collaborator, Event, StaffProfile


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date_display", "event_time_display", "location")
    search_fields = ("title", "location")
    list_filter = ("event_date_display",)


@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ("name", "link")
    search_fields = ("name",)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "order")
    search_fields = ("user__email", "user__first_name", "user__last_name")

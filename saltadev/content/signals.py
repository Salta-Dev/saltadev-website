"""Signals for the content app."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify
from users.models import User

from .models import Event


@receiver(post_save, sender=Event)
def notify_new_event(
    sender: type[Event],
    instance: Event,
    created: bool,
    **kwargs: object,
) -> None:
    """Notify verified users when a new event is created."""
    if not created:
        return

    # Use event link if available, otherwise link to events list
    url = instance.link if instance.link else reverse("events")

    users = User.objects.filter(is_active=True, email_confirmed=True)
    for user in users:
        notify.send(
            sender=instance,
            recipient=user,
            verb="Nuevo evento",
            action_object=instance,
            description=instance.title,
            url=url,
        )

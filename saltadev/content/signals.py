"""Signals for the content app."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify
from users.models import User

from .models import Event


@receiver(pre_save, sender=Event)
def store_previous_status(
    sender: type[Event],
    instance: Event,
    **kwargs: object,
) -> None:
    """Store previous status to detect approval or rejection."""
    if instance.pk:
        try:
            instance._previous_status = Event.objects.get(pk=instance.pk).status  # type: ignore[attr-defined]
        except Event.DoesNotExist:
            instance._previous_status = None  # type: ignore[attr-defined]
    else:
        instance._previous_status = None  # type: ignore[attr-defined]


@receiver(post_save, sender=Event)
def notify_event_approved(
    sender: type[Event],
    instance: Event,
    created: bool,
    **kwargs: object,
) -> None:
    """Notify verified users when an event is approved.

    Sends notifications when:
    - A new event is created with approved status (by admin/moderator)
    - An existing event changes from pending to approved
    """
    # Get previous status from pre_save signal
    previous_status = getattr(instance, "_previous_status", None)

    # Check if this is a new approval:
    # - New event created as approved (by admin/moderator), OR
    # - Existing event changed from pending to approved
    is_newly_approved = instance.status == Event.Status.APPROVED and (
        created or previous_status == Event.Status.PENDING
    )

    if not is_newly_approved:
        return

    # Use event link if available, otherwise link to events list
    url = instance.link if instance.link else reverse("events")

    # Notify all verified users except the creator
    users = User.objects.filter(is_active=True, email_confirmed=True)
    if instance.creator:
        users = users.exclude(pk=instance.creator.pk)

    for user in users:
        notify.send(
            sender=instance,
            recipient=user,
            verb="Nuevo evento",
            action_object=instance,
            description=instance.title,
            url=url,
        )


@receiver(post_save, sender=Event)
def notify_event_rejected(
    sender: type[Event],
    instance: Event,
    created: bool,
    **kwargs: object,
) -> None:
    """Notify the creator when their event is rejected.

    Sends a notification when an existing event changes from pending to rejected.
    """
    previous_status = getattr(instance, "_previous_status", None)

    # Only notify if event was pending and is now rejected
    is_rejected = (
        not created
        and previous_status == Event.Status.PENDING
        and instance.status == Event.Status.REJECTED
    )

    if not is_rejected or not instance.creator:
        return

    notify.send(
        sender=instance,
        recipient=instance.creator,
        verb="Evento rechazado",
        action_object=instance,
        description=f'Tu evento "{instance.title}" fue rechazado.',
        url=reverse("my_events"),
    )

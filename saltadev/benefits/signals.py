"""Signals for the benefits app."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from notifications.signals import notify
from users.models import User

from .models import Benefit


@receiver(post_save, sender=Benefit)
def notify_new_benefit(
    sender: type[Benefit],
    instance: Benefit,
    created: bool,
    **kwargs: object,
) -> None:
    """Notify verified users when a new benefit is created."""
    if not created:
        return

    url = reverse("benefit_detail", kwargs={"pk": instance.pk})

    users = User.objects.filter(is_active=True, email_confirmed=True).exclude(
        pk=instance.creator_id
    )
    for user in users:
        notify.send(
            sender=instance.creator,
            recipient=user,
            verb="Nuevo beneficio",
            action_object=instance,
            description=instance.title,
            url=url,
        )

from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import PasswordResetToken


class Command(BaseCommand):
    help = "Delete expired or used password reset tokens."

    def handle(self, *args: Any, **options: Any) -> None:
        now = timezone.now()
        expired_count, _ = PasswordResetToken.objects.filter(
            expires_at__lt=now
        ).delete()
        used_count, _ = PasswordResetToken.objects.filter(used=True).delete()

        self.stdout.write(
            f"Expired tokens deleted: {expired_count}. Used tokens deleted: {used_count}."
        )

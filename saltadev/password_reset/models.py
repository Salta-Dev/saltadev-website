from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordResetToken(models.Model):
    """Time-limited, single-use token for password reset requests."""

    class Meta:
        verbose_name = "token de recuperacion"
        verbose_name_plural = "tokens de recuperacion"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_active(self) -> bool:
        """Return True if the token has not been used and has not expired."""
        return (not self.used) and self.expires_at >= timezone.now()

    def __str__(self) -> str:
        return f"Reset token para {self.user.email}"

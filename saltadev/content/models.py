from django.conf import settings
from django.db import models
from django.utils import timezone


class Event(models.Model):
    """Community event with date, location, and registration link."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    photo = models.CharField(max_length=300, blank=True)
    link = models.URLField(blank=True)
    event_start_date = models.DateTimeField(null=True, blank=True)
    event_end_date = models.DateTimeField(null=True, blank=True)
    event_date_display = models.CharField(max_length=30, blank=True)
    event_time_display = models.CharField(max_length=30, blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title


class Collaborator(models.Model):
    """Organization or company that collaborates with the SaltaDev community."""

    name = models.CharField(max_length=150)
    image = models.CharField(max_length=300, blank=True)
    link = models.URLField(blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name


class StaffProfile(models.Model):
    """Public profile for SaltaDev staff members displayed on the homepage."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    role = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo = models.CharField(max_length=300, blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.user.email

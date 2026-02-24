"""Management command to configure Django Site domain."""

import os
from argparse import ArgumentParser
from typing import Any

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Configure the Django Site domain."""

    help = "Configure the Django Site domain"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--domain",
            type=str,
            help="Site domain (defaults to SITE_DOMAIN env var or localhost:8000)",
        )
        parser.add_argument(
            "--name",
            type=str,
            help="Site name (defaults to SITE_NAME env var or SaltaDev)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        domain = options["domain"] or os.getenv("SITE_DOMAIN", "localhost:8000")
        name = options["name"] or os.getenv("SITE_NAME", "SaltaDev")

        site, created = Site.objects.update_or_create(
            id=1,
            defaults={"domain": domain, "name": name},
        )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(f"{action} Site: {site.name} ({site.domain})")
        )

        self._cleanup_google_socialapps()

    def _cleanup_google_socialapps(self) -> None:
        """Remove Google SocialApps from DB — credentials are managed via settings."""
        from allauth.socialaccount.models import SocialApp

        deleted_count, _ = SocialApp.objects.filter(provider="google").delete()
        if deleted_count:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Removed {deleted_count} Google SocialApp(s) from DB "
                    "(credentials are now managed via environment variables)"
                )
            )

"""Management command to configure Django Site domain and Google OAuth."""

import os
from argparse import ArgumentParser
from typing import Any

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Configure the Django Site domain and Google OAuth SocialApp."""

    help = "Configure the Django Site domain and Google OAuth SocialApp"

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

        self._configure_google_oauth(site)

    def _configure_google_oauth(self, site: Site) -> None:
        """Create or update the Google OAuth SocialApp and associate it with the site."""
        from allauth.socialaccount.models import SocialApp

        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        google_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        if not google_client_id or not google_secret:
            self.stdout.write(
                self.style.WARNING(
                    "Google OAuth: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set — skipping SocialApp setup"
                )
            )
            return

        app, created = SocialApp.objects.update_or_create(
            provider="google",
            defaults={
                "name": "Google",
                "client_id": google_client_id,
                "secret": google_secret,
            },
        )

        app.sites.add(site)

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} Google SocialApp: client_id={google_client_id[:20]}..."
            )
        )

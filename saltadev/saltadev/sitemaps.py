"""Sitemap configuration for SEO."""

from content.models import Event
from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""

    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self) -> list[str]:
        """Return list of URL names for static pages."""
        return [
            "home",
            "events",
            "resources",
            "resource_reading",
            "resource_specialties",
            "resource_tools",
            "resource_projects",
            "code_of_conduct",
            "benefits_list",
        ]

    def location(self, item: str) -> str:
        """Return the URL for the given item."""
        return reverse(item)


class EventSitemap(Sitemap):
    """Sitemap for approved public event detail pages."""

    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self) -> QuerySet[Event]:
        """Return approved events included in the sitemap."""
        return Event.objects.filter(status=Event.Status.APPROVED)

    def location(self, obj: Event) -> str:
        """Return the public detail URL for an approved event."""
        return obj.get_absolute_url()


sitemaps = {
    "static": StaticViewSitemap,
    "events": EventSitemap,
}

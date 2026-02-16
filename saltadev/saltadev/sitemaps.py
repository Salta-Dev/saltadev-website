"""Sitemap configuration for SEO."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""

    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self) -> list[str]:
        """Return list of URL names for static pages."""
        return ["home", "events_list", "code_of_conduct", "benefits_list"]

    def location(self, item: str) -> str:
        """Return the URL for the given item."""
        return reverse(item)


sitemaps = {
    "static": StaticViewSitemap,
}

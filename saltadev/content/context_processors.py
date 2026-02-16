from django.conf import settings
from django.http import HttpRequest


def site_links(_request: HttpRequest) -> dict[str, str]:
    """Inject social media and community links into every template context."""
    return {
        "site_whatsapp": getattr(settings, "SITE_WHATSAPP", ""),
        "site_discord": getattr(settings, "SITE_DISCORD", ""),
        "site_github": getattr(settings, "SITE_GITHUB", ""),
        "site_linkedin": getattr(settings, "SITE_LINKEDIN", ""),
        "site_twitter": getattr(settings, "SITE_TWITTER", ""),
        "site_instagram": getattr(settings, "SITE_INSTAGRAM", ""),
    }

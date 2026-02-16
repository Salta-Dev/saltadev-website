from django.conf import settings
from django.http import HttpRequest, HttpResponsePermanentRedirect


def redirect_discord(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev Discord server (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_DISCORD)


def redirect_whatsapp(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev WhatsApp group (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_WHATSAPP)


def redirect_linkedin(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev LinkedIn page (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_LINKEDIN)


def redirect_github(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev GitHub organization (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_GITHUB)


def redirect_twitter(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev X/Twitter account (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_TWITTER)


def redirect_instagram(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev Instagram page (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_INSTAGRAM)

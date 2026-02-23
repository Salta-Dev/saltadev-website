from django.conf import settings
from django.http import HttpRequest, HttpResponsePermanentRedirect
from django.views.decorators.http import require_GET


@require_GET
def redirect_discord(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev Discord server (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_DISCORD)


@require_GET
def redirect_whatsapp(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev WhatsApp group (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_WHATSAPP)


@require_GET
def redirect_linkedin(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev LinkedIn page (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_LINKEDIN)


@require_GET
def redirect_github(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev GitHub organization (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_GITHUB)


@require_GET
def redirect_twitter(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev X/Twitter account (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_TWITTER)


@require_GET
def redirect_instagram(_request: HttpRequest) -> HttpResponsePermanentRedirect:
    """Redirect to the SaltaDev Instagram page (301 permanent)."""
    return HttpResponsePermanentRedirect(settings.SITE_INSTAGRAM)

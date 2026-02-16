from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect


def redirect_discord(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev Discord server."""
    return redirect(settings.SITE_DISCORD)


def redirect_whatsapp(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev WhatsApp group."""
    return redirect(settings.SITE_WHATSAPP)


def redirect_linkedin(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev LinkedIn page."""
    return redirect(settings.SITE_LINKEDIN)


def redirect_github(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev GitHub organization."""
    return redirect(settings.SITE_GITHUB)


def redirect_twitter(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev X/Twitter account."""
    return redirect(settings.SITE_TWITTER)


def redirect_instagram(_request: HttpRequest) -> HttpResponseRedirect:
    """Redirect to the SaltaDev Instagram page."""
    return redirect(settings.SITE_INSTAGRAM)

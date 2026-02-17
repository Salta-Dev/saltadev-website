from django.conf import settings
from django.http import HttpResponse

from .ratelimit import FINGERPRINT_COOKIE, FINGERPRINT_MAX_AGE


def attach_fingerprint_cookie(
    response: HttpResponse, fingerprint: str, should_set_cookie: bool
) -> HttpResponse:
    """Set the fingerprint cookie on the response if needed."""
    if should_set_cookie:
        response.set_cookie(
            FINGERPRINT_COOKIE,
            fingerprint,
            max_age=FINGERPRINT_MAX_AGE,
            httponly=True,
            samesite="Lax",
            secure=not settings.DEBUG,  # Only HTTPS in production
        )
    return response

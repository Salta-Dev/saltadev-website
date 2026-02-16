"""Login view with rate limiting and email verification."""

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from saltadev.logging import get_logger
from users.fingerprint import attach_fingerprint_cookie
from users.models import User
from users.ratelimit import (
    LOGIN_LIMIT,
    build_keys,
    get_client_ip,
    get_fingerprint,
    increment,
    is_blocked,
    reset,
)

logger = get_logger()

# Template constant to avoid duplication
TEMPLATE_LOGIN = "auth_login/index.html"


def _get_lockout_message() -> str:
    """Get the lockout message from settings or use default."""
    return getattr(
        settings,
        "AXES_LOCKOUT_MESSAGE",
        "Demasiados intentos fallidos. Intentá nuevamente más tarde.",
    )


def _render_login_blocked(
    request: HttpRequest,
    form: AuthenticationForm,
    email_value: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Render login page with blocked message."""
    response = render(
        request,
        TEMPLATE_LOGIN,
        {
            "form": form,
            "email_not_verified": False,
            "email_value": email_value,
            "blocked_message": _get_lockout_message(),
        },
    )
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _render_login_form(
    request: HttpRequest,
    form: AuthenticationForm,
    email_not_verified: bool,
    email_value: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Render login page with form."""
    response = render(
        request,
        TEMPLATE_LOGIN,
        {
            "form": form,
            "email_not_verified": email_not_verified,
            "email_value": email_value,
        },
    )
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _handle_rate_limit_block(
    request: HttpRequest,
    email_value: str,
    ip_address: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle blocked request due to rate limiting."""
    logger.warning(
        "Login blocked by rate limit",
        extra={"ip": ip_address, "email": email_value},
    )
    form = AuthenticationForm(request, data=request.POST)
    return _render_login_blocked(
        request, form, email_value, fingerprint, should_set_cookie
    )


def _handle_axes_block(
    request: HttpRequest,
    email_value: str,
    ip_address: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle blocked request due to Axes lockout."""
    logger.warning(
        "Login blocked by Axes",
        extra={"ip": ip_address, "email": email_value},
    )
    form = AuthenticationForm(request, data=request.POST)
    return _render_login_blocked(
        request, form, email_value, fingerprint, should_set_cookie
    )


def _handle_unverified_email(
    request: HttpRequest,
    form: AuthenticationForm,
    email_value: str,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle login attempt with unverified email."""
    logger.info(
        "Login failed: unverified email",
        extra={"ip": ip_address, "email": email_value},
    )
    increment(keys)
    return _render_login_form(
        request, form, True, email_value, fingerprint, should_set_cookie
    )


def _handle_successful_login(
    request: HttpRequest,
    user: User,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle successful login."""
    login(request, user)
    reset(keys)
    logger.info(
        "Login success",
        extra={"ip": ip_address, "user_id": user.pk},
    )
    response = redirect("dashboard")
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login with rate limiting and email verification check."""
    ip_address = get_client_ip(request)
    fingerprint, should_set_cookie = get_fingerprint(request)
    email_value = request.POST.get("username", "") if request.method == "POST" else ""
    keys = build_keys("login", ip_address, email_value, fingerprint)

    if request.method != "POST":
        form = AuthenticationForm()
        return _render_login_form(
            request, form, False, email_value, fingerprint, should_set_cookie
        )

    # Check rate limiting
    if is_blocked(keys, LOGIN_LIMIT):
        return _handle_rate_limit_block(
            request, email_value, ip_address, fingerprint, should_set_cookie
        )

    # Check Axes lockout
    if getattr(request, "axes_locked_out", False):
        return _handle_axes_block(
            request, email_value, ip_address, fingerprint, should_set_cookie
        )

    form = AuthenticationForm(request, data=request.POST)

    # Check email verification status
    email_not_verified = False
    if email_value:
        user = User.objects.filter(email=email_value).first()
        if user and not user.email_confirmed:
            email_not_verified = True

    if form.is_valid():
        user = form.get_user()
        if not user or not user.email_confirmed:
            return _handle_unverified_email(
                request,
                form,
                email_value,
                ip_address,
                keys,
                fingerprint,
                should_set_cookie,
            )
        return _handle_successful_login(
            request, user, ip_address, keys, fingerprint, should_set_cookie
        )

    # Invalid credentials
    increment(keys)
    logger.info(
        "Login failed: invalid credentials",
        extra={"ip": ip_address, "email": email_value},
    )
    return _render_login_form(
        request, form, email_not_verified, email_value, fingerprint, should_set_cookie
    )

"""Email verification views with rate limiting."""

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from saltadev.logging import get_logger

from .fingerprint import attach_fingerprint_cookie
from .models import User
from .ratelimit import (
    SCOPES,
    VERIFY_LIMIT,
    build_keys,
    clear_limits,
    get_client_ip,
    get_fingerprint,
    increment,
    is_blocked,
    reset,
)
from .utils import get_lockout_message, send_verification_code, verify_code

logger = get_logger()

# Template constant to avoid duplication
TEMPLATE_VERIFY = "users/verificar.html"


def _render_verify_page(
    request: HttpRequest,
    email: str,
    fingerprint: str,
    should_set_cookie: bool,
    blocked_message: str | None = None,
) -> HttpResponse:
    """Render verification page."""
    context: dict[str, str] = {"email": email}
    if blocked_message:
        context["blocked_message"] = blocked_message
    response = render(request, TEMPLATE_VERIFY, context)
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _handle_resend_blocked(
    request: HttpRequest,
    email: str,
    ip_address: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle blocked resend request."""
    logger.warning(
        "Verification resend blocked by rate limit",
        extra={"ip": ip_address, "email": email},
    )
    return _render_verify_page(
        request, email, fingerprint, should_set_cookie, get_lockout_message()
    )


def _handle_resend_request(
    request: HttpRequest,
    email: str,
    ip_address: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle verification code resend."""
    try:
        user = User.objects.get(email=email)
        if user.email_confirmed:
            messages.error(request, "Esta cuenta ya está verificada.")
        else:
            send_verification_code(user)
            messages.success(request, f"Se envió un nuevo código a {email}")
            logger.info(
                "Verification code resent",
                extra={"ip": ip_address, "user_id": user.pk},
            )
    except ObjectDoesNotExist:
        messages.error(request, "No existe una cuenta con ese email.")

    response = redirect(f"/verificar/?{urlencode({'email': email})}")
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _handle_verify_blocked(
    request: HttpRequest,
    email: str,
    ip_address: str,
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle blocked verification request."""
    logger.warning(
        "Verification blocked by rate limit",
        extra={"ip": ip_address, "email": email},
    )
    return _render_verify_page(
        request, email, fingerprint, should_set_cookie, get_lockout_message()
    )


def _handle_missing_fields(
    request: HttpRequest,
    email: str,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle missing email or code fields."""
    increment(keys)
    messages.error(request, "Por favor completá todos los campos.")
    logger.info(
        "Verification failed: missing fields",
        extra={"ip": ip_address, "email": email},
    )
    return _render_verify_page(request, email, fingerprint, should_set_cookie)


def _handle_user_not_found(
    request: HttpRequest,
    email: str,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle user not found error."""
    increment(keys)
    messages.error(request, "Usuario no encontrado.")
    logger.info(
        "Verification failed: user not found",
        extra={"ip": ip_address, "email": email},
    )
    return _render_verify_page(request, email, fingerprint, should_set_cookie)


def _handle_successful_verification(
    request: HttpRequest,
    user: User,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle successful email verification."""
    messages.success(request, "Email verificado correctamente!")
    reset(keys)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    logger.info(
        "Email verified",
        extra={"ip": ip_address, "user_id": user.pk},
    )
    response = redirect("dashboard")
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _handle_invalid_code(
    request: HttpRequest,
    email: str,
    ip_address: str,
    keys: list[str],
    fingerprint: str,
    should_set_cookie: bool,
) -> HttpResponse:
    """Handle invalid or expired verification code."""
    increment(keys)
    messages.error(request, "Código inválido o expirado.")
    logger.info(
        "Verification failed: invalid code",
        extra={"ip": ip_address, "email": email},
    )
    return _render_verify_page(request, email, fingerprint, should_set_cookie)


def verify_email(request: HttpRequest) -> HttpResponse:
    """Handle email verification via 6-digit code submission or code resend.

    Security:
    - Requires valid email parameter
    - Validates user exists and is not already verified
    - Resend uses POST for CSRF protection
    - Rate limited to prevent abuse
    """
    ip_address = get_client_ip(request)
    fingerprint, should_set_cookie = get_fingerprint(request)

    # Handle POST requests (code verification or resend)
    if request.method == "POST":
        email = request.POST.get("email", "")
        action = request.POST.get("action", "verify")
        keys = build_keys("verify", ip_address, email, fingerprint)

        if is_blocked(keys, VERIFY_LIMIT):
            return _handle_verify_blocked(
                request, email, ip_address, fingerprint, should_set_cookie
            )

        # Handle resend request (POST with action=resend)
        if action == "resend":
            if not email:
                messages.error(request, "Email requerido.")
                return redirect("login")
            return _handle_resend_request(
                request, email, ip_address, fingerprint, should_set_cookie
            )

        # Handle code verification
        code = request.POST.get("code", "")

        if not email or not code:
            return _handle_missing_fields(
                request, email, ip_address, keys, fingerprint, should_set_cookie
            )

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return _handle_user_not_found(
                request, email, ip_address, keys, fingerprint, should_set_cookie
            )

        if verify_code(user, code):
            return _handle_successful_verification(
                request, user, ip_address, keys, fingerprint, should_set_cookie
            )
        return _handle_invalid_code(
            request, email, ip_address, keys, fingerprint, should_set_cookie
        )

    # GET request - validate email parameter
    email = request.GET.get("email", "").strip()

    # No email provided - redirect to login
    if not email:
        messages.error(request, "Acceso inválido. Iniciá sesión o registrate.")
        return redirect("login")

    # Validate user exists
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        messages.error(request, "No existe una cuenta con ese email.")
        return redirect("login")

    # Check if already verified
    if user.email_confirmed:
        messages.info(request, "Tu cuenta ya está verificada. Podés iniciar sesión.")
        return redirect("login")

    # Valid unverified user - show verification page
    keys = build_keys("verify", ip_address, email, fingerprint)
    return _render_verify_page(request, email, fingerprint, should_set_cookie)


def clear_rate_limits_view(request: HttpRequest) -> HttpResponse:
    """Staff-only view to clear rate limit blocks by IP, email, or fingerprint."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect("home")

    ip_address = request.GET.get("ip")
    email = request.GET.get("email")
    fingerprint = request.GET.get("fp")
    cleared = clear_limits(
        SCOPES, ip_address=ip_address, email=email, fingerprint=fingerprint
    )
    messages.success(request, f"Se limpiaron {len(cleared)} bloqueos.")
    return redirect("home")

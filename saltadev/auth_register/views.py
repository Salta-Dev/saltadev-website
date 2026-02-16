from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from saltadev.logging import get_logger
from users.fingerprint import attach_fingerprint_cookie
from users.forms import RegisterForm
from users.models import User
from users.ratelimit import (
    REGISTER_LIMIT,
    build_keys,
    get_client_ip,
    get_fingerprint,
    increment,
    is_blocked,
    reset,
)
from users.utils import get_lockout_message

logger = get_logger()


def register_view(request: HttpRequest) -> HttpResponse:
    """Handle new user registration with rate limiting and reCAPTCHA."""
    ip_address = get_client_ip(request)
    fingerprint, should_set_cookie = get_fingerprint(request)
    email = str(request.POST.get("email")) if request.method == "POST" else None
    keys = build_keys("register", ip_address, email, fingerprint)

    if is_blocked(keys, REGISTER_LIMIT):
        logger.warning(
            "Register blocked by rate limit",
            extra={"ip": ip_address, "email": email},
        )
        response = render(
            request,
            "auth_register/index.html",
            {
                "form": RegisterForm(request.POST or None),
                "blocked_message": get_lockout_message(),
            },
        )
        return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            reset(keys)
            logger.info(
                "Register success",
                extra={"ip": ip_address, "user_id": user.pk},
            )
            response = redirect(f"/verificar/?email={user.email}")
            return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)
        increment(keys)
        logger.info(
            "Register failed: invalid form",
            extra={"ip": ip_address, "email": email},
        )
    else:
        form = RegisterForm()
    response = render(request, "auth_register/index.html", {"form": form})
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)

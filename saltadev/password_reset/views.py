from typing import Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from saltadev.logging import get_logger
from users.fingerprint import attach_fingerprint_cookie
from users.models import User
from users.ratelimit import (
    PASSWORD_RESET_CONFIRM_LIMIT,
    PASSWORD_RESET_REQUEST_LIMIT,
    build_keys,
    get_client_ip,
    get_fingerprint,
    increment,
    is_blocked,
    reset,
)
from users.utils import (
    create_password_reset_token,
    get_lockout_message,
    hash_token,
    send_password_reset,
)

from .forms import PasswordResetConfirmForm, PasswordResetRequestForm
from .models import PasswordResetToken

logger = get_logger()


def request_reset_view(request: HttpRequest) -> HttpResponse:
    """Handle the password reset request form and send the reset email."""
    ip_address = get_client_ip(request)
    fingerprint, should_set_cookie = get_fingerprint(request)
    email_value = request.POST.get("email") if request.method == "POST" else None
    keys = build_keys("password_reset_request", ip_address, email_value, fingerprint)

    if is_blocked(keys, PASSWORD_RESET_REQUEST_LIMIT):
        logger.warning(
            "Password reset request blocked by rate limit",
            extra={"ip": ip_address, "email": email_value},
        )
        form = PasswordResetRequestForm(request.POST or None)
        response = render(
            request,
            "password_reset/request.html",
            {
                "form": form,
                "blocked_message": get_lockout_message(),
            },
        )
        return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)

    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                token = create_password_reset_token(user, expires_minutes=10)
                reset_link = request.build_absolute_uri(
                    f"{reverse('password_reset_confirm')}?token={token}"
                )
                send_password_reset(user, reset_link)
                logger.info(
                    "Password reset email sent",
                    extra={"ip": ip_address, "user_id": user.pk},
                )
            reset(keys)
            messages.success(
                request,
                "Te enviamos un correo con las instrucciones para restablecer tu contraseña.",
            )
            response = redirect("password_reset_request")
            return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)
        increment(keys)
        logger.info(
            "Password reset request failed: invalid form",
            extra={"ip": ip_address, "email": email_value},
        )
    else:
        form = PasswordResetRequestForm()

    response = render(
        request,
        "password_reset/request.html",
        {
            "form": form,
            "email_value": email_value,
        },
    )
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def confirm_reset_view(request: HttpRequest) -> HttpResponse:
    """Validate the reset token and allow the user to set a new password."""
    ip_address = get_client_ip(request)
    fingerprint, should_set_cookie = get_fingerprint(request)
    token_value = (
        request.GET.get("token", "")
        if request.method == "GET"
        else request.POST.get("token", "")
    )
    keys = build_keys("password_reset_confirm", ip_address, token_value, fingerprint)

    token_record = _get_token_record(str(token_value))
    if not token_record:
        logger.info(
            "Password reset failed: invalid token",
            extra={"ip": ip_address},
        )
        response = render(request, "password_reset/invalid.html")
        return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)

    if is_blocked(keys, PASSWORD_RESET_CONFIRM_LIMIT):
        logger.warning(
            "Password reset confirm blocked by rate limit",
            extra={"ip": ip_address},
        )
        user = token_record.user
        form = PasswordResetConfirmForm(request.POST or None, user=user)
        response = render(
            request,
            "password_reset/confirm.html",
            {
                "form": form,
                "token": token_value,
                "blocked_message": get_lockout_message(),
            },
        )
        return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)

    if request.method == "POST":
        user = token_record.user
        form = PasswordResetConfirmForm(request.POST, user=user)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            PasswordResetToken.objects.filter(pk=token_record.pk).update(used=True)
            reset(keys)
            logger.info(
                "Password reset success",
                extra={"ip": ip_address, "user_id": user.pk},
            )
            messages.success(
                request,
                "Tu contraseña se actualizó correctamente. Ya podés iniciar sesión.",
            )
            response = redirect("login")
            return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)
        increment(keys)
        logger.info(
            "Password reset confirm failed: invalid form",
            extra={"ip": ip_address},
        )
    else:
        user = token_record.user
        form = PasswordResetConfirmForm(user=user)

    response = render(
        request,
        "password_reset/confirm.html",
        {
            "form": form,
            "token": token_value,
        },
    )
    return attach_fingerprint_cookie(response, fingerprint, should_set_cookie)


def _get_token_record(token_value: str) -> Optional["PasswordResetToken"]:
    """Look up an active, unused password reset token by its raw value."""
    if not token_value:
        return None
    token_hash = hash_token(token_value)
    token_record = (
        PasswordResetToken.objects.filter(token_hash=token_hash, used=False)
        .order_by("-created_at")
        .first()
    )
    if not token_record or not token_record.is_active():
        return None
    return token_record

"""Custom middleware for user-related functionality."""

from collections.abc import Callable
from typing import ClassVar

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import User


class ProfileCompletionMiddleware:
    """
    Middleware that redirects users with incomplete profiles to complete them.

    Social login users (Google/GitHub) don't provide birth_date, which is
    required for membership. This middleware ensures they complete their
    profile before accessing other authenticated areas.
    """

    # URLs that should be accessible even with incomplete profile
    EXEMPT_URLS: ClassVar[list[str]] = [
        "/dashboard/completar-perfil/",
        "/logout/",
        "/admin/",
        "/static/",
        "/media/",
        "/health/",
    ]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware with the next handler in chain."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and redirect if profile completion needed."""
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Skip for exempt URLs
        path = request.path
        if any(path.startswith(exempt) for exempt in self.EXEMPT_URLS):
            return self.get_response(request)

        # Check if user needs to complete their profile
        user: User = request.user
        if hasattr(user, "needs_profile_completion") and user.needs_profile_completion:
            return redirect("complete_profile")

        return self.get_response(request)

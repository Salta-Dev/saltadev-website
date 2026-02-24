"""Custom adapters for django-allauth."""

from typing import TYPE_CHECKING, Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest

if TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin

    from .models import User


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter that disables allauth's default signup.

    We use our own registration flow (auth_register) for email/password users.
    This adapter ensures allauth is only used for social login.
    """

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Disable allauth signup - we use our own registration views."""
        return False


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter for Google login.

    Handles:
    - Linking social accounts to existing users by email
    - Extracting user data from social providers
    - Creating profiles with provider data (avatar, etc.)
    """

    def is_open_for_signup(
        self, request: HttpRequest, sociallogin: "SocialLogin"
    ) -> bool:
        """
        Allow signup through social providers (Google).

        The CustomAccountAdapter disables signup for email/password,
        but we want to allow users to register via OAuth.
        """
        return True

    def pre_social_login(
        self, request: HttpRequest, sociallogin: "SocialLogin"
    ) -> None:
        """
        Link social account to existing user if email matches.

        Called after OAuth callback but before login/signup is complete.
        If user with this email exists, connect the social account to them.
        """
        from .models import User

        # If social account is already connected, nothing to do
        if sociallogin.is_existing:
            return

        # Check if a user with this email exists
        email = sociallogin.account.extra_data.get("email")
        if not email and sociallogin.user and sociallogin.user.email:
            email = sociallogin.user.email

        if email:
            try:
                existing_user = User.objects.get(email=email)
                # Connect this social account to the existing user
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: "SocialLogin",
        data: dict[str, Any],
    ) -> "User":
        """
        Populate user instance from social provider data.

        Called when creating a new user from a social login.
        Extracts first_name, last_name, email from the provider's data.
        """
        from .models import User

        user = super().populate_user(request, sociallogin, data)
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Mark email as verified (social providers verify emails)
        user.email_confirmed = True

        if provider == "google":
            user.registration_method = User.RegistrationMethod.GOOGLE
            # Google provides given_name and family_name
            user.first_name = extra_data.get("given_name", data.get("first_name", ""))
            user.last_name = extra_data.get("family_name", data.get("last_name", ""))

        return user

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: "SocialLogin",
        form: Any = None,
    ) -> "User":
        """
        Save the new user and create their profile with provider data.

        Called after populate_user when creating a new social user.
        Creates a Profile with avatar URL from the provider.
        """
        from .models import Profile

        user = super().save_user(request, sociallogin, form)
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # Get or create profile
        profile, _created = Profile.objects.get_or_create(user=user)

        if provider == "google":
            # Google provides picture URL
            avatar_url = extra_data.get("picture", "")
            if avatar_url and not profile.avatar_url:
                profile.avatar_url = avatar_url

        profile.save()
        return user

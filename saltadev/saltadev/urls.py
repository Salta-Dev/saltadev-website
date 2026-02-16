"""
URL configuration for saltadev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from content import redirects as content_redirects
from dashboard.views import public_credential_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.urls import include, path


def custom_404(request, exception=None):
    """Custom 404 error handler."""
    return render(request, "404.html", status=404)


handler404 = custom_404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("eventos/", include("events.urls")),
    path("reglamento/", include("code_of_conduct.urls")),
    path("login/", include("auth_login.urls")),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="/", http_method_names=["get", "post"]),
        name="logout",
    ),
    path("register/", include("auth_register.urls")),
    path("verificar/", include("users.urls")),
    path("discord/", content_redirects.redirect_discord, name="redirect_discord"),
    path("whatsapp/", content_redirects.redirect_whatsapp, name="redirect_whatsapp"),
    path("linkedin/", content_redirects.redirect_linkedin, name="redirect_linkedin"),
    path("github/", content_redirects.redirect_github, name="redirect_github"),
    path("x/", content_redirects.redirect_twitter, name="redirect_twitter"),
    path("instagram/", content_redirects.redirect_instagram, name="redirect_instagram"),
    path("password-reset/", include("password_reset.urls")),
    path("locations/", include("locations.urls")),
    path("dashboard/", include("dashboard.urls")),
    path(
        "credencial/<str:public_id>/", public_credential_view, name="public_credential"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.BASE_DIR / "static"
    )
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all for 404 - must be last
urlpatterns += [
    path("<path:path>", custom_404),
]

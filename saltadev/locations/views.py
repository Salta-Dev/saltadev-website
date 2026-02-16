"""Views for locations app."""

from django.http import HttpRequest, JsonResponse

from .models import Province


def provinces_by_country(request: HttpRequest, country_code: str) -> JsonResponse:
    """Return provinces for a given country code as JSON."""
    provinces = Province.objects.filter(country_id=country_code.upper()).values(
        "id", "code", "name"
    )
    return JsonResponse(list(provinces), safe=False)

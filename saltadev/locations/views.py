"""Views for locations app."""

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from .models import Province


@require_GET
def provinces_by_country(_request: HttpRequest, country_code: str) -> JsonResponse:
    """Return provinces for a given country code as JSON."""
    provinces = Province.objects.filter(country_id=country_code.upper()).values(
        "id", "code", "name"
    )
    return JsonResponse(list(provinces), safe=False)

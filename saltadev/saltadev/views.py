"""Project-level views for the saltadev project."""

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from loguru import logger

HEALTH_CACHE_KEY = "health_check_result"
HEALTH_CACHE_TTL = 30  # seconds


@require_http_methods(["GET", "HEAD"])
def health_check(_request: HttpRequest) -> JsonResponse:
    """Healthcheck endpoint for Render monitoring.

    Verifies:
    - Django is running
    - PostgreSQL connection
    - Redis connection

    Result is cached for 30 seconds to prevent DB/Redis flood attacks.
    Errors are logged but not exposed in the API response.
    """
    # Return cached result if available (protects DB/Redis from flood)
    cached = cache.get(HEALTH_CACHE_KEY)
    if cached is not None:
        return JsonResponse(cached["data"], status=cached["status_code"])

    services: dict[str, str] = {
        "django": "ok",
        "postgres": "unknown",
        "redis": "unknown",
    }
    health: dict[str, str | dict[str, str]] = {
        "status": "healthy",
        "services": services,
    }

    # Check PostgreSQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        services["postgres"] = "ok"
    except Exception as e:
        logger.error(f"Healthcheck: PostgreSQL error - {e}")
        services["postgres"] = "error"
        health["status"] = "unhealthy"

    # Check Redis
    try:
        cache.set("healthcheck", "ok", 10)
        if cache.get("healthcheck") == "ok":
            services["redis"] = "ok"
        else:
            logger.error("Healthcheck: Redis cache read failed")
            services["redis"] = "error"
            health["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Healthcheck: Redis error - {e}")
        services["redis"] = "error"
        health["status"] = "unhealthy"

    status_code = 200 if health["status"] == "healthy" else 503
    cache.set(
        HEALTH_CACHE_KEY, {"data": health, "status_code": status_code}, HEALTH_CACHE_TTL
    )
    return JsonResponse(health, status=status_code)

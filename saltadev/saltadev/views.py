"""Project-level views for the saltadev project."""

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, JsonResponse
from loguru import logger


def health_check(request: HttpRequest) -> JsonResponse:
    """Healthcheck endpoint for Render monitoring.

    Verifies:
    - Django is running
    - PostgreSQL connection
    - Redis connection

    Errors are logged but not exposed in the API response.
    """
    health: dict[str, str | dict[str, str]] = {
        "status": "healthy",
        "services": {
            "django": "ok",
            "postgres": "unknown",
            "redis": "unknown",
        },
    }
    services = health["services"]
    assert isinstance(services, dict)

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
    return JsonResponse(health, status=status_code)

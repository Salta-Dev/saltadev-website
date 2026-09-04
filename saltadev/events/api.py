"""Internal API for creating events from the Telegram ingest bot."""

from __future__ import annotations

import hmac
import json
from datetime import datetime
from io import BytesIO
from typing import Any, cast

from content.models import Event
from dateutil import parser as date_parser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.timezone import is_naive, make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from users.image_service import upload_event_image

from events.services import (
    find_duplicate_event,
    invalidate_home_events_cache,
    prepare_event_for_save,
)

_MAX_JSON_BYTES = 16_384
_MAX_PHOTO_BYTES = 8 * 1024 * 1024
_PHOTO_TYPES = frozenset(
    {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
)


def _is_authorized(request: HttpRequest) -> bool:
    """Return True when the request carries the configured ingest bearer token."""
    expected = getattr(settings, "SALTADEV_INGEST_TOKEN", "") or ""
    if not expected:
        return False
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "
    if not header.startswith(prefix):
        return False
    provided = header.removeprefix(prefix).strip()
    if len(provided) != len(expected):
        return False
    return hmac.compare_digest(provided, expected)


def _parse_datetime(value: object) -> datetime | None:
    """Parse an ISO datetime string into an aware datetime."""
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError("datetime must be a string")
    parsed = date_parser.isoparse(value.strip())
    if is_naive(parsed):
        parsed = make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _optional_str(
    data: dict[str, Any], key: str, *, max_length: int | None = None
) -> str:
    """Read an optional string field from the payload."""
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    cleaned = value.strip()
    if max_length is not None:
        return cleaned[:max_length]
    return cleaned


def _is_multipart(request: HttpRequest) -> bool:
    """Return True when the request is multipart form data."""
    content_type = request.content_type or ""
    return content_type.startswith("multipart/form-data")


def _parse_multipart(request: HttpRequest) -> None:
    """Populate POST and FILES for PATCH/PUT. Django only parses those on POST."""
    if request.method == "POST" or not _is_multipart(request):
        return
    stream = BytesIO(request.body)
    post, files = request.parse_file_upload(request.META, stream)
    # Django only auto-parses multipart on POST; mirror that for PATCH/PUT.
    mutable_request = cast(Any, request)
    mutable_request._post = post
    mutable_request._files = files


def _read_payload(request: HttpRequest) -> dict[str, Any]:
    """Read JSON or multipart form fields into a dict."""
    if _is_multipart(request):
        _parse_multipart(request)
        return {key: value for key, value in request.POST.items()}

    if len(request.body) > _MAX_JSON_BYTES:
        raise ValueError("payload-too-large")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid-json") from exc
    if not isinstance(payload, dict):
        raise ValueError("invalid-json")
    return payload


def _store_photo(uploaded: UploadedFile | None, photo_url: str) -> str:
    """Upload a photo file when present; otherwise keep the URL from the payload."""
    if uploaded is None:
        return photo_url
    if uploaded.size and uploaded.size > _MAX_PHOTO_BYTES:
        raise ValueError("photo is too large")
    content_type = (uploaded.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in _PHOTO_TYPES:
        raise ValueError("photo must be an image")
    result = upload_event_image(uploaded)
    if not result.success or not result.url:
        raise ValueError(result.error or "could not store photo")
    url = result.url
    if url.startswith("/"):
        url = f"{settings.SITE_URL.rstrip('/')}{url}"
    return url


_LIST_LIMIT = 20


def _event_payload(event: Event) -> dict[str, Any]:
    """Return the public JSON body for an ingested event."""
    site_url = settings.SITE_URL.rstrip("/")
    return {
        "id": event.pk,
        "slug": event.slug,
        "title": event.title,
        "kind": event.kind,
        "link": event.link,
        "event_date_display": event.event_date_display,
        "url": f"{site_url}{event.get_absolute_url()}",
    }


def _apply_optional_fields(event: Event, payload: dict[str, Any]) -> None:
    """Copy provided ingest fields onto an existing event."""
    if "title" in payload:
        title = _optional_str(payload, "title", max_length=200)
        if title:
            event.title = title
    if "description" in payload:
        event.description = _optional_str(payload, "description")
    if "location" in payload:
        event.location = _optional_str(payload, "location", max_length=200)
    if "link" in payload:
        event.link = _optional_str(payload, "link")
    if "kind" in payload:
        kind = _optional_str(payload, "kind", max_length=20)
        if kind:
            if kind not in Event.Kind.values:
                raise ValueError(
                    "kind must be meetup, talk, workshop, hackathon or social"
                )
            event.kind = kind
    if "event_date_display" in payload:
        event.event_date_display = _optional_str(
            payload, "event_date_display", max_length=30
        )
    if "event_time_display" in payload:
        event.event_time_display = _optional_str(
            payload, "event_time_display", max_length=30
        )
    if "event_start_date" in payload:
        event.event_start_date = _parse_datetime(payload.get("event_start_date"))
    if "event_end_date" in payload:
        event.event_end_date = _parse_datetime(payload.get("event_end_date"))
        if (
            event.event_start_date
            and event.event_end_date
            and event.event_end_date < event.event_start_date
        ):
            raise ValueError("event_end_date cannot be before event_start_date")


def list_internal_events(request: HttpRequest) -> JsonResponse:
    """Return recent events for ingest clients."""
    if not _is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    events = Event.objects.order_by("-created_at", "-pk")[:_LIST_LIMIT]
    return JsonResponse({"events": [_event_payload(event) for event in events]})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def internal_events_collection(request: HttpRequest) -> JsonResponse:
    """List events or create one from a trusted ingest client."""
    if request.method == "GET":
        return list_internal_events(request)
    return create_internal_event(request)


@csrf_exempt
@require_POST
def create_internal_event(request: HttpRequest) -> JsonResponse:
    """Create an approved event from a trusted ingest client."""
    if not _is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        payload = _read_payload(request)
    except ValueError as exc:
        if str(exc) == "payload-too-large":
            return JsonResponse({"error": "Payload too large"}, status=413)
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        title = _optional_str(payload, "title", max_length=200)
        if not title:
            raise ValueError("title is required")
        description = _optional_str(payload, "description")
        location = _optional_str(payload, "location", max_length=200)
        photo = _optional_str(payload, "photo", max_length=500)
        uploaded = request.FILES.get("photo") if _is_multipart(request) else None
        if uploaded is not None and not isinstance(uploaded, UploadedFile):
            raise ValueError("photo must be a file")
        photo = _store_photo(uploaded, photo)
        link = _optional_str(payload, "link")
        date_display = _optional_str(payload, "event_date_display", max_length=30)
        time_display = _optional_str(payload, "event_time_display", max_length=30)
        start = _parse_datetime(payload.get("event_start_date"))
        end = _parse_datetime(payload.get("event_end_date"))
        if start and end and end < start:
            raise ValueError("event_end_date cannot be before event_start_date")
        kind = _optional_str(payload, "kind", max_length=20)
        if kind and kind not in Event.Kind.values:
            raise ValueError("kind must be meetup, talk, workshop, hackathon or social")
    except (ValueError, OverflowError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    status = _optional_str(payload, "status") or Event.Status.APPROVED
    if status not in {Event.Status.APPROVED, Event.Status.PENDING}:
        return JsonResponse({"error": "status must be approved or pending"}, status=400)

    duplicate = find_duplicate_event(
        title=title,
        link=link,
        event_start_date=start,
        event_date_display=date_display,
    )
    if duplicate is not None:
        return JsonResponse(
            {
                "error": "duplicate",
                "message": "An event with the same link or title and date already exists",
                "event": _event_payload(duplicate),
            },
            status=409,
        )

    event = Event(
        title=title,
        description=description,
        location=location,
        photo=photo,
        link=link,
        event_start_date=start,
        event_end_date=end,
        event_date_display=date_display,
        event_time_display=time_display,
        status=status,
        kind=kind or Event.Kind.MEETUP,
    )
    if status == Event.Status.APPROVED:
        event.approved_at = timezone.now()
    prepare_event_for_save(event)
    try:
        event.full_clean()
    except ValidationError as exc:
        return JsonResponse(
            {"error": "Invalid event", "details": exc.message_dict},
            status=400,
        )
    event.save()
    invalidate_home_events_cache()

    return JsonResponse(_event_payload(event), status=201)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def update_internal_event(request: HttpRequest, pk: int) -> JsonResponse:
    """Update or delete an existing event from a trusted ingest client."""
    if not _is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method == "DELETE":
        event.delete()
        invalidate_home_events_cache()
        return JsonResponse({"ok": True, "id": pk})

    try:
        payload = _read_payload(request)
    except ValueError as exc:
        if str(exc) == "payload-too-large":
            return JsonResponse({"error": "Payload too large"}, status=413)
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        _apply_optional_fields(event, payload)
        uploaded = request.FILES.get("photo") if _is_multipart(request) else None
        if uploaded is not None and not isinstance(uploaded, UploadedFile):
            raise ValueError("photo must be a file")
        photo_url = _optional_str(payload, "photo", max_length=500)
        if uploaded is not None or photo_url:
            event.photo = _store_photo(uploaded, photo_url or event.photo)
    except (ValueError, OverflowError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    prepare_event_for_save(event)
    try:
        event.full_clean()
    except ValidationError as exc:
        return JsonResponse(
            {"error": "Invalid event", "details": exc.message_dict},
            status=400,
        )
    event.save()
    invalidate_home_events_cache()
    return JsonResponse(_event_payload(event))


@csrf_exempt
@require_GET
def latest_internal_event(request: HttpRequest) -> JsonResponse:
    """Return the most recently created event for ingest clients."""
    if not _is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    event = Event.objects.order_by("-created_at", "-pk").first()
    if event is None:
        return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse(_event_payload(event))

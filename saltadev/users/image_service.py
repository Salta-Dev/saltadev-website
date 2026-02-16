"""Image upload service supporting local storage and ImgBB API."""

import base64
import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import requests
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


@dataclass
class ImageUploadResult:
    """Result of an image upload operation."""

    success: bool
    url: str | None = None
    delete_url: str | None = None
    error: str | None = None


def _upload_to_imgbb(image_file: UploadedFile) -> ImageUploadResult:
    """Upload image to ImgBB API.

    Args:
        image_file: The uploaded image file.

    Returns:
        ImageUploadResult with URL on success or error message on failure.
    """
    api_key = getattr(settings, "IMGBB_API_KEY", None)
    if not api_key:
        return ImageUploadResult(
            success=False,
            error="IMGBB_API_KEY not configured",
        )

    try:
        # Read and encode image as base64
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # Upload to ImgBB
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": api_key,
                "image": image_data,
                "name": f"avatar_{uuid.uuid4().hex[:8]}",
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            data = result["data"]
            return ImageUploadResult(
                success=True,
                url=data.get("display_url") or data.get("url"),
                delete_url=data.get("delete_url"),
            )
        return ImageUploadResult(
            success=False,
            error=result.get("error", {}).get("message", "Unknown error"),
        )

    except requests.RequestException as e:
        logger.error("ImgBB upload failed: %s", e)
        return ImageUploadResult(
            success=False,
            error=f"Upload failed: {e}",
        )


def _upload_locally(image_file: UploadedFile) -> ImageUploadResult:
    """Save image to local media directory.

    Args:
        image_file: The uploaded image file.

    Returns:
        ImageUploadResult with local URL on success.
    """
    try:
        # Generate unique filename
        ext = Path(image_file.name).suffix.lower() or ".jpg"
        filename = f"avatar_{uuid.uuid4().hex[:12]}{ext}"

        # Ensure avatars directory exists
        avatars_dir = Path(settings.MEDIA_ROOT) / "avatars"
        avatars_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = avatars_dir / filename
        with open(file_path, "wb") as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # Return URL
        url = f"{settings.MEDIA_URL}avatars/{filename}"
        return ImageUploadResult(
            success=True,
            url=url,
        )

    except OSError as e:
        logger.error("Local upload failed: %s", e)
        return ImageUploadResult(
            success=False,
            error=f"Failed to save file: {e}",
        )


def upload_avatar(image_file: UploadedFile) -> ImageUploadResult:
    """Upload avatar image using appropriate method based on environment.

    In DEBUG mode, saves locally. Otherwise, uploads to ImgBB.

    Args:
        image_file: The uploaded image file.

    Returns:
        ImageUploadResult with URL on success or error on failure.
    """
    if settings.DEBUG:
        return _upload_locally(image_file)
    return _upload_to_imgbb(image_file)


def delete_imgbb_image(delete_url: str) -> bool:
    """Delete an image from ImgBB using its delete URL.

    Args:
        delete_url: The delete URL provided by ImgBB.

    Returns:
        True if deletion was successful, False otherwise.
    """
    if not delete_url:
        return False

    try:
        response = requests.get(delete_url, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error("ImgBB delete failed: %s", e)
        return False


def delete_local_image(url: str) -> bool:
    """Delete a locally stored image.

    Args:
        url: The URL of the local image.

    Returns:
        True if deletion was successful, False otherwise.
    """
    if not url or not url.startswith(settings.MEDIA_URL):
        return False

    try:
        # Convert URL to file path
        relative_path = url.replace(settings.MEDIA_URL, "")
        file_path = Path(settings.MEDIA_ROOT) / relative_path

        if file_path.exists():
            os.remove(file_path)
            return True
        return False

    except OSError as e:
        logger.error("Local delete failed: %s", e)
        return False

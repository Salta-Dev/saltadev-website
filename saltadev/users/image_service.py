"""Image upload service supporting local storage and Cloudinary."""

import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)

# Default transformation string for on-the-fly processing
# Format: width_height_crop_gravity_quality_format
# This is applied via URL, not on upload, to avoid consuming transformation credits
AVATAR_TRANSFORMATION = "w_400,h_400,c_fill,g_face,q_auto,f_auto"


@dataclass
class ImageUploadResult:
    """Result of an image upload operation."""

    success: bool
    url: str | None = None
    public_id: str | None = None
    error: str | None = None


def _is_cloudinary_configured() -> bool:
    """Check if Cloudinary credentials are configured."""
    cloudinary_settings = getattr(settings, "CLOUDINARY_STORAGE", {})
    return bool(
        cloudinary_settings.get("CLOUD_NAME")
        and cloudinary_settings.get("API_KEY")
        and cloudinary_settings.get("API_SECRET")
    )


def _configure_cloudinary() -> None:
    """Configure Cloudinary SDK from Django settings."""
    cloudinary_settings = settings.CLOUDINARY_STORAGE
    cloudinary.config(
        cloud_name=cloudinary_settings["CLOUD_NAME"],
        api_key=cloudinary_settings["API_KEY"],
        api_secret=cloudinary_settings["API_SECRET"],
    )


def get_transformed_url(
    base_url: str, transformation: str = AVATAR_TRANSFORMATION
) -> str:
    """Generate Cloudinary URL with on-the-fly transformation.

    Cloudinary caches transformed images in their CDN, so this doesn't
    consume transformation credits on subsequent requests. The transformation
    is only processed once on first access.

    Args:
        base_url: The base Cloudinary URL from upload result.
        transformation: Cloudinary transformation string (default: AVATAR_TRANSFORMATION).

    Returns:
        URL with transformation applied.
    """
    return base_url.replace("/upload/", f"/upload/{transformation}/")


def _upload_to_cloudinary(image_file: UploadedFile) -> ImageUploadResult:
    """Upload image to Cloudinary.

    Args:
        image_file: The uploaded image file.

    Returns:
        ImageUploadResult with URL on success or error message on failure.
    """
    if not _is_cloudinary_configured():
        return ImageUploadResult(
            success=False,
            error="Cloudinary credentials not configured",
        )

    try:
        _configure_cloudinary()

        # Generate unique public_id for the avatar
        public_id = f"avatars/avatar_{uuid.uuid4().hex[:12]}"

        # Upload to Cloudinary without transformation on upload
        # This avoids consuming transformation credits (25/month limit on free tier)
        # Transformations are applied on-the-fly via URL and cached by Cloudinary CDN
        result = cloudinary.uploader.upload(
            image_file,
            public_id=public_id,
            folder="saltadev",
            resource_type="image",
            overwrite=True,
        )

        # Generate URL with on-the-fly transformation (cached by CDN)
        base_url = result.get("secure_url")
        transformed_url = get_transformed_url(base_url) if base_url else None

        return ImageUploadResult(
            success=True,
            url=transformed_url,
            public_id=result.get("public_id"),
        )

    except cloudinary.exceptions.Error as e:
        logger.error("Cloudinary upload failed: %s", e)
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
        file_name: str = image_file.name or "avatar.jpg"
        ext = Path(file_name).suffix.lower() or ".jpg"
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

    Uses Cloudinary if configured, otherwise saves locally.

    Args:
        image_file: The uploaded image file.

    Returns:
        ImageUploadResult with URL on success or error on failure.
    """
    if _is_cloudinary_configured():
        return _upload_to_cloudinary(image_file)
    return _upload_locally(image_file)


def delete_cloudinary_image(public_id: str) -> bool:
    """Delete an image from Cloudinary using its public_id.

    Args:
        public_id: The public_id of the image in Cloudinary.

    Returns:
        True if deletion was successful, False otherwise.
    """
    if not public_id or not _is_cloudinary_configured():
        return False

    try:
        _configure_cloudinary()
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except cloudinary.exceptions.Error as e:
        logger.error("Cloudinary delete failed: %s", e)
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

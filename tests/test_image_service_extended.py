"""Extended tests for the image service."""

from io import BytesIO
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from users.image_service import (
    AVATAR_TRANSFORMATION,
    BENEFIT_TRANSFORMATION,
    EVENT_TRANSFORMATION,
    ImageUploadResult,
    _is_cloudinary_configured,
    _upload_locally,
    delete_cloudinary_image,
    delete_local_image,
    get_transformed_url,
    upload_avatar,
    upload_benefit_image,
    upload_event_image,
)


def create_test_image(name: str = "test.jpg", format: str = "JPEG") -> SimpleUploadedFile:
    """Create a test image file for upload."""
    image = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=buffer.read(),
        content_type=f"image/{format.lower()}",
    )


class TestIsCloudinaryConfigured:
    """Tests for _is_cloudinary_configured function."""

    def test_cloudinary_configured_with_all_settings(self, settings):
        """Test returns True when all Cloudinary settings are present."""
        settings.CLOUDINARY_STORAGE = {
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
        assert _is_cloudinary_configured() is True

    def test_cloudinary_not_configured_missing_cloud_name(self, settings):
        """Test returns False when CLOUD_NAME is missing."""
        settings.CLOUDINARY_STORAGE = {
            "CLOUD_NAME": "",
            "API_KEY": "test_key",
            "API_SECRET": "test_secret",
        }
        assert _is_cloudinary_configured() is False

    def test_cloudinary_not_configured_missing_api_key(self, settings):
        """Test returns False when API_KEY is missing."""
        settings.CLOUDINARY_STORAGE = {
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "",
            "API_SECRET": "test_secret",
        }
        assert _is_cloudinary_configured() is False

    def test_cloudinary_not_configured_missing_api_secret(self, settings):
        """Test returns False when API_SECRET is missing."""
        settings.CLOUDINARY_STORAGE = {
            "CLOUD_NAME": "test_cloud",
            "API_KEY": "test_key",
            "API_SECRET": "",
        }
        assert _is_cloudinary_configured() is False

    def test_cloudinary_not_configured_empty_dict(self, settings):
        """Test returns False when CLOUDINARY_STORAGE is empty."""
        settings.CLOUDINARY_STORAGE = {}
        assert _is_cloudinary_configured() is False


class TestGetTransformedUrl:
    """Tests for get_transformed_url function."""

    def test_inserts_transformation_string(self):
        """Test transformation string is inserted correctly."""
        base_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        result = get_transformed_url(base_url, "w_100,h_100")
        assert result == "https://res.cloudinary.com/demo/image/upload/w_100,h_100/sample.jpg"

    def test_default_avatar_transformation(self):
        """Test default avatar transformation is applied."""
        base_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
        result = get_transformed_url(base_url)
        assert AVATAR_TRANSFORMATION in result


@pytest.mark.django_db
class TestUploadLocally:
    """Tests for _upload_locally function."""

    def test_upload_locally_creates_directory(self, settings, tmp_path):
        """Test local upload creates directory if not exists."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        image = create_test_image()
        result = _upload_locally(image, folder="test_folder", prefix="test")

        assert result.success
        assert (tmp_path / "test_folder").exists()

    def test_upload_locally_returns_url(self, settings, tmp_path):
        """Test local upload returns correct URL."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        image = create_test_image()
        result = _upload_locally(image, folder="avatars", prefix="avatar")

        assert result.success
        assert result.url is not None
        assert result.url.startswith("/media/avatars/")
        assert "avatar_" in result.url

    def test_upload_locally_saves_file(self, settings, tmp_path):
        """Test local upload actually saves the file."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        image = create_test_image()
        result = _upload_locally(image, folder="test_folder", prefix="test")

        assert result.success
        # Check file exists
        files = list((tmp_path / "test_folder").glob("test_*.jpg"))
        assert len(files) == 1

    def test_upload_locally_preserves_extension(self, settings, tmp_path):
        """Test local upload preserves file extension."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        image = create_test_image(name="test.png", format="PNG")
        result = _upload_locally(image, folder="test_folder", prefix="test")

        assert result.success
        assert result.url.endswith(".png")


@pytest.mark.django_db
class TestDeleteLocalImage:
    """Tests for delete_local_image function."""

    def test_delete_local_image_success(self, settings, tmp_path):
        """Test successful local image deletion."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        # Create a test file
        folder = tmp_path / "test"
        folder.mkdir()
        test_file = folder / "test_image.jpg"
        test_file.write_bytes(b"test content")

        url = "/media/test/test_image.jpg"
        result = delete_local_image(url)

        assert result is True
        assert not test_file.exists()

    def test_delete_local_image_not_found(self, settings, tmp_path):
        """Test deletion of non-existent file returns False."""
        settings.MEDIA_ROOT = str(tmp_path)
        settings.MEDIA_URL = "/media/"

        url = "/media/test/nonexistent.jpg"
        result = delete_local_image(url)

        assert result is False

    def test_delete_local_image_invalid_url(self, settings):
        """Test deletion with invalid URL returns False."""
        settings.MEDIA_URL = "/media/"

        result = delete_local_image("https://example.com/image.jpg")
        assert result is False

    def test_delete_local_image_empty_url(self, settings):
        """Test deletion with empty URL returns False."""
        result = delete_local_image("")
        assert result is False


class TestDeleteCloudinaryImage:
    """Tests for delete_cloudinary_image function."""

    @patch("users.image_service._is_cloudinary_configured")
    def test_delete_cloudinary_not_configured(self, mock_configured):
        """Test returns False when Cloudinary not configured."""
        mock_configured.return_value = False
        result = delete_cloudinary_image("test_public_id")
        assert result is False

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._configure_cloudinary")
    @patch("cloudinary.uploader.destroy")
    def test_delete_cloudinary_success(
        self, mock_destroy, mock_configure, mock_configured
    ):
        """Test successful Cloudinary image deletion."""
        mock_configured.return_value = True
        mock_destroy.return_value = {"result": "ok"}

        result = delete_cloudinary_image("test_public_id")

        assert result is True
        mock_destroy.assert_called_once_with("test_public_id")

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._configure_cloudinary")
    @patch("cloudinary.uploader.destroy")
    def test_delete_cloudinary_failure(
        self, mock_destroy, mock_configure, mock_configured
    ):
        """Test Cloudinary deletion failure returns False."""
        mock_configured.return_value = True
        mock_destroy.return_value = {"result": "not found"}

        result = delete_cloudinary_image("test_public_id")

        assert result is False

    def test_delete_cloudinary_empty_public_id(self):
        """Test returns False for empty public_id."""
        result = delete_cloudinary_image("")
        assert result is False


class TestUploadRouting:
    """Tests for upload function routing."""

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_locally")
    def test_upload_avatar_uses_local_when_not_configured(
        self, mock_local, mock_configured
    ):
        """Test upload_avatar uses local storage when Cloudinary not configured."""
        mock_configured.return_value = False
        mock_local.return_value = ImageUploadResult(success=True, url="/media/test.jpg")

        image = create_test_image()
        upload_avatar(image)

        mock_local.assert_called_once()
        _, kwargs = mock_local.call_args
        assert kwargs["folder"] == "avatars"
        assert kwargs["prefix"] == "avatar"

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_to_cloudinary")
    def test_upload_avatar_uses_cloudinary_when_configured(
        self, mock_cloudinary, mock_configured
    ):
        """Test upload_avatar uses Cloudinary when configured."""
        mock_configured.return_value = True
        mock_cloudinary.return_value = ImageUploadResult(
            success=True, url="https://cloudinary.com/test.jpg"
        )

        image = create_test_image()
        upload_avatar(image)

        mock_cloudinary.assert_called_once()
        _, kwargs = mock_cloudinary.call_args
        assert kwargs["folder"] == "avatars"
        assert kwargs["transformation"] == AVATAR_TRANSFORMATION

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_locally")
    def test_upload_benefit_image_routing(self, mock_local, mock_configured):
        """Test upload_benefit_image uses correct folder and prefix."""
        mock_configured.return_value = False
        mock_local.return_value = ImageUploadResult(success=True, url="/media/test.jpg")

        image = create_test_image()
        upload_benefit_image(image)

        mock_local.assert_called_once()
        _, kwargs = mock_local.call_args
        assert kwargs["folder"] == "benefits"
        assert kwargs["prefix"] == "benefit"

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_locally")
    def test_upload_event_image_routing(self, mock_local, mock_configured):
        """Test upload_event_image uses correct folder and prefix."""
        mock_configured.return_value = False
        mock_local.return_value = ImageUploadResult(success=True, url="/media/test.jpg")

        image = create_test_image()
        upload_event_image(image)

        mock_local.assert_called_once()
        _, kwargs = mock_local.call_args
        assert kwargs["folder"] == "events"
        assert kwargs["prefix"] == "event"

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_to_cloudinary")
    def test_upload_benefit_cloudinary_transformation(
        self, mock_cloudinary, mock_configured
    ):
        """Test upload_benefit_image uses correct Cloudinary transformation."""
        mock_configured.return_value = True
        mock_cloudinary.return_value = ImageUploadResult(
            success=True, url="https://cloudinary.com/test.jpg"
        )

        image = create_test_image()
        upload_benefit_image(image)

        _, kwargs = mock_cloudinary.call_args
        assert kwargs["transformation"] == BENEFIT_TRANSFORMATION

    @patch("users.image_service._is_cloudinary_configured")
    @patch("users.image_service._upload_to_cloudinary")
    def test_upload_event_cloudinary_transformation(
        self, mock_cloudinary, mock_configured
    ):
        """Test upload_event_image uses correct Cloudinary transformation."""
        mock_configured.return_value = True
        mock_cloudinary.return_value = ImageUploadResult(
            success=True, url="https://cloudinary.com/test.jpg"
        )

        image = create_test_image()
        upload_event_image(image)

        _, kwargs = mock_cloudinary.call_args
        assert kwargs["transformation"] == EVENT_TRANSFORMATION


class TestImageUploadResult:
    """Tests for ImageUploadResult dataclass."""

    def test_success_result(self):
        """Test successful result has correct attributes."""
        result = ImageUploadResult(
            success=True,
            url="https://example.com/image.jpg",
            public_id="test_public_id",
        )
        assert result.success is True
        assert result.url == "https://example.com/image.jpg"
        assert result.public_id == "test_public_id"
        assert result.error is None

    def test_error_result(self):
        """Test error result has correct attributes."""
        result = ImageUploadResult(
            success=False,
            error="Upload failed",
        )
        assert result.success is False
        assert result.url is None
        assert result.public_id is None
        assert result.error == "Upload failed"

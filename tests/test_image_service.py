"""Tests for the image service module."""

import pytest

from users.image_service import AVATAR_TRANSFORMATION, get_transformed_url


class TestGetTransformedUrl:
    """Tests for get_transformed_url function."""

    def test_transforms_cloudinary_url(self):
        """Test that transformation is inserted correctly into URL."""
        base_url = "https://res.cloudinary.com/demo/image/upload/saltadev/avatars/avatar_abc123.jpg"
        result = get_transformed_url(base_url)

        expected = f"https://res.cloudinary.com/demo/image/upload/{AVATAR_TRANSFORMATION}/saltadev/avatars/avatar_abc123.jpg"
        assert result == expected

    def test_uses_default_transformation(self):
        """Test that default AVATAR_TRANSFORMATION is used."""
        base_url = "https://res.cloudinary.com/demo/image/upload/test.jpg"
        result = get_transformed_url(base_url)

        assert AVATAR_TRANSFORMATION in result
        assert "/upload/w_400,h_400,c_fill,g_face,q_auto,f_auto/" in result

    def test_custom_transformation(self):
        """Test that custom transformation can be passed."""
        base_url = "https://res.cloudinary.com/demo/image/upload/test.jpg"
        custom_transform = "w_100,h_100,c_thumb"
        result = get_transformed_url(base_url, transformation=custom_transform)

        assert custom_transform in result
        assert f"/upload/{custom_transform}/" in result

    def test_preserves_url_structure(self):
        """Test that URL structure is preserved after transformation."""
        base_url = "https://res.cloudinary.com/mycloud/image/upload/v123456/folder/subfolder/image.png"
        result = get_transformed_url(base_url)

        assert result.startswith("https://res.cloudinary.com/mycloud/image/upload/")
        assert result.endswith("/v123456/folder/subfolder/image.png")


class TestAvatarTransformationConstant:
    """Tests for the AVATAR_TRANSFORMATION constant."""

    def test_has_required_transformations(self):
        """Test that AVATAR_TRANSFORMATION includes required parameters."""
        assert "w_400" in AVATAR_TRANSFORMATION  # width
        assert "h_400" in AVATAR_TRANSFORMATION  # height
        assert "c_fill" in AVATAR_TRANSFORMATION  # crop mode
        assert "g_face" in AVATAR_TRANSFORMATION  # gravity (face detection)
        assert "q_auto" in AVATAR_TRANSFORMATION  # quality auto
        assert "f_auto" in AVATAR_TRANSFORMATION  # format auto

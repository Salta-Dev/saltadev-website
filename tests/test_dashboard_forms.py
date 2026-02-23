"""Tests for dashboard forms."""

import pytest
from dashboard.forms import ProfileForm


@pytest.mark.django_db
class TestProfileForm:
    """Tests for the ProfileForm."""

    def test_github_url_extraction(self, collaborator_user):
        """Test GitHub username is extracted from URL."""
        form = ProfileForm(
            data={"github": "https://github.com/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["github"] == "testuser"

    def test_github_url_with_www(self, collaborator_user):
        """Test GitHub username is extracted from URL with www."""
        form = ProfileForm(
            data={"github": "https://www.github.com/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["github"] == "testuser"

    def test_github_username_with_at(self, collaborator_user):
        """Test GitHub username with @ prefix is cleaned."""
        form = ProfileForm(
            data={"github": "@testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["github"] == "testuser"

    def test_github_plain_username(self, collaborator_user):
        """Test plain GitHub username is kept."""
        form = ProfileForm(
            data={"github": "testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["github"] == "testuser"

    def test_linkedin_url_extraction(self, collaborator_user):
        """Test LinkedIn username is extracted from URL."""
        form = ProfileForm(
            data={"linkedin": "https://linkedin.com/in/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["linkedin"] == "testuser"

    def test_linkedin_url_with_www(self, collaborator_user):
        """Test LinkedIn username is extracted from URL with www."""
        form = ProfileForm(
            data={"linkedin": "https://www.linkedin.com/in/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["linkedin"] == "testuser"

    def test_twitter_url_extraction(self, collaborator_user):
        """Test Twitter username is extracted from URL."""
        form = ProfileForm(
            data={"twitter": "https://twitter.com/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["twitter"] == "testuser"

    def test_twitter_x_url_extraction(self, collaborator_user):
        """Test X.com username is extracted from URL."""
        form = ProfileForm(
            data={"twitter": "https://x.com/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["twitter"] == "testuser"

    def test_instagram_url_extraction(self, collaborator_user):
        """Test Instagram username is extracted from URL."""
        form = ProfileForm(
            data={"instagram": "https://instagram.com/testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["instagram"] == "testuser"

    def test_instagram_username_with_at(self, collaborator_user):
        """Test Instagram username with @ prefix is cleaned."""
        form = ProfileForm(
            data={"instagram": "@testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["instagram"] == "testuser"

    def test_username_too_long(self, collaborator_user):
        """Test username longer than 50 chars is invalid."""
        long_username = "a" * 51
        form = ProfileForm(
            data={"github": long_username},
            instance=collaborator_user.profile,
        )
        assert not form.is_valid()
        assert "github" in form.errors

    def test_discord_plain_username(self, collaborator_user):
        """Test Discord plain username is kept."""
        form = ProfileForm(
            data={"discord": "testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["discord"] == "testuser"

    def test_discord_with_at_prefix(self, collaborator_user):
        """Test Discord username with @ prefix is cleaned."""
        form = ProfileForm(
            data={"discord": "@testuser"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["discord"] == "testuser"

    def test_discord_with_discriminator(self, collaborator_user):
        """Test Discord username with discriminator is kept."""
        form = ProfileForm(
            data={"discord": "testuser#1234"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        assert form.cleaned_data["discord"] == "testuser#1234"

    def test_technologies_parsing(self, collaborator_user):
        """Test technologies are parsed from comma-separated input."""
        form = ProfileForm(
            data={"technologies_input": "Python, Django, JavaScript"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        profile = form.save()
        assert profile.technologies == ["Python", "Django", "JavaScript"]

    def test_technologies_empty_items_filtered(self, collaborator_user):
        """Test empty items are filtered from technologies."""
        form = ProfileForm(
            data={"technologies_input": "Python, , Django, , JavaScript"},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        profile = form.save()
        assert profile.technologies == ["Python", "Django", "JavaScript"]

    def test_technologies_whitespace_stripped(self, collaborator_user):
        """Test whitespace is stripped from technologies."""
        form = ProfileForm(
            data={"technologies_input": "  Python  ,  Django  ,  JavaScript  "},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        profile = form.save()
        assert profile.technologies == ["Python", "Django", "JavaScript"]

    def test_technologies_empty_input(self, collaborator_user):
        """Test empty technologies input results in empty list."""
        form = ProfileForm(
            data={"technologies_input": ""},
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        profile = form.save()
        assert profile.technologies == []

    def test_save_updates_profile(self, collaborator_user):
        """Test save updates profile fields."""
        form = ProfileForm(
            data={
                "bio": "New bio text",
                "company": "Test Company",
                "position": "Developer",
            },
            instance=collaborator_user.profile,
        )
        assert form.is_valid()
        profile = form.save()
        assert profile.bio == "New bio text"
        assert profile.company == "Test Company"
        assert profile.position == "Developer"

    def test_init_with_existing_technologies(self, collaborator_user):
        """Test form init populates technologies input."""
        collaborator_user.profile.technologies = ["Python", "Django"]
        collaborator_user.profile.save()

        form = ProfileForm(instance=collaborator_user.profile)
        assert form.fields["technologies_input"].initial == "Python, Django"

    def test_empty_social_fields_valid(self, collaborator_user):
        """Test all social fields can be empty."""
        form = ProfileForm(
            data={
                "github": "",
                "linkedin": "",
                "twitter": "",
                "instagram": "",
                "discord": "",
            },
            instance=collaborator_user.profile,
        )
        assert form.is_valid()

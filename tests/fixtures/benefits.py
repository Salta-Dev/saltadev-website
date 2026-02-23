"""Benefit-related fixtures for testing."""

from datetime import date, timedelta

import pytest
from benefits.models import Benefit
from django.utils import timezone
from users.models import Profile, User


@pytest.fixture
def benefit_data():
    """Return default benefit data for creation."""
    return {
        "title": "Test Benefit",
        "description": "A test benefit description",
        "benefit_type": Benefit.BenefitType.DISCOUNT,
        "discount_percentage": 20,
        "modality": Benefit.Modality.VIRTUAL,
        "contact_source": Benefit.ContactSource.USER_PROFILE,
        "is_active": True,
    }


@pytest.fixture
def collaborator_user(db):
    """Create and return a user with collaborator role."""
    user = User.objects.create_user(
        email="collaborator@example.com",
        first_name="Collaborator",
        last_name="User",
        birth_date=date(1990, 5, 15),
        password="SecurePass123$",
        role="colaborador",
        email_confirmed=True,
    )
    Profile.objects.create(user=user)
    return user


@pytest.fixture
def moderator_user(db):
    """Create and return a user with moderator role."""
    user = User.objects.create_user(
        email="moderator@example.com",
        first_name="Moderator",
        last_name="User",
        birth_date=date(1988, 3, 20),
        password="SecurePass123$",
        role="moderador",
        email_confirmed=True,
    )
    Profile.objects.create(user=user)
    return user


@pytest.fixture
def admin_user(db):
    """Create and return a user with administrator role."""
    user = User.objects.create_user(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        birth_date=date(1985, 1, 10),
        password="SecurePass123$",
        role="administrador",
        email_confirmed=True,
    )
    Profile.objects.create(user=user)
    return user


@pytest.fixture
def member_user(db):
    """Create and return a regular member user (no special permissions)."""
    user = User.objects.create_user(
        email="member@example.com",
        first_name="Member",
        last_name="User",
        birth_date=date(1995, 7, 25),
        password="SecurePass123$",
        role="miembro",
        email_confirmed=True,
    )
    Profile.objects.create(user=user)
    return user


@pytest.fixture
def benefit(db, collaborator_user, benefit_data):
    """Create and return an active benefit."""
    return Benefit.objects.create(
        **benefit_data,
        creator=collaborator_user,
    )


@pytest.fixture
def expired_benefit(db, collaborator_user, benefit_data):
    """Create and return an expired benefit."""
    data = benefit_data.copy()
    data["title"] = "Expired Benefit"
    data["expiration_date"] = timezone.now().date() - timedelta(days=1)
    return Benefit.objects.create(
        **data,
        creator=collaborator_user,
    )


@pytest.fixture
def future_benefit(db, collaborator_user, benefit_data):
    """Create and return a benefit with future expiration."""
    data = benefit_data.copy()
    data["title"] = "Future Benefit"
    data["expiration_date"] = timezone.now().date() + timedelta(days=30)
    return Benefit.objects.create(
        **data,
        creator=collaborator_user,
    )


@pytest.fixture
def redeemable_benefit(db, collaborator_user):
    """Create and return a redeemable benefit with redemption limit."""
    return Benefit.objects.create(
        title="Redeemable Benefit",
        description="A benefit that can be redeemed",
        benefit_type=Benefit.BenefitType.REDEEMABLE,
        redemption_limit=10,
        redemption_count=0,
        modality=Benefit.Modality.VIRTUAL,
        contact_source=Benefit.ContactSource.USER_PROFILE,
        is_active=True,
        creator=collaborator_user,
    )


@pytest.fixture
def fully_redeemed_benefit(db, collaborator_user):
    """Create and return a benefit that has reached its redemption limit."""
    return Benefit.objects.create(
        title="Fully Redeemed Benefit",
        description="A benefit that has reached its limit",
        benefit_type=Benefit.BenefitType.REDEEMABLE,
        redemption_limit=5,
        redemption_count=5,
        modality=Benefit.Modality.VIRTUAL,
        contact_source=Benefit.ContactSource.USER_PROFILE,
        is_active=True,
        creator=collaborator_user,
    )


@pytest.fixture
def inactive_benefit(db, collaborator_user, benefit_data):
    """Create and return an inactive benefit."""
    data = benefit_data.copy()
    data["title"] = "Inactive Benefit"
    data["is_active"] = False
    return Benefit.objects.create(
        **data,
        creator=collaborator_user,
    )


@pytest.fixture
def in_person_benefit(db, collaborator_user):
    """Create and return an in-person benefit with location."""
    return Benefit.objects.create(
        title="In-Person Benefit",
        description="A benefit available in person",
        benefit_type=Benefit.BenefitType.DISCOUNT,
        discount_percentage=15,
        modality=Benefit.Modality.IN_PERSON,
        location="Av. San Martin 123, Salta",
        contact_source=Benefit.ContactSource.USER_PROFILE,
        is_active=True,
        creator=collaborator_user,
    )


@pytest.fixture
def custom_contact_benefit(db, collaborator_user):
    """Create and return a benefit with custom contact info."""
    return Benefit.objects.create(
        title="Custom Contact Benefit",
        description="A benefit with custom contact information",
        benefit_type=Benefit.BenefitType.DISCOUNT,
        discount_percentage=25,
        modality=Benefit.Modality.VIRTUAL,
        contact_source=Benefit.ContactSource.CUSTOM,
        contact_phone="+54 9 387 123 4567",
        contact_email="contact@example.com",
        contact_website="https://example.com",
        is_active=True,
        creator=collaborator_user,
    )

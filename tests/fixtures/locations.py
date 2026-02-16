"""Location fixtures for testing."""

import pytest
from locations.models import Country, Province


@pytest.fixture
def argentina(db):
    """Create Argentina country."""
    return Country.objects.get_or_create(code="AR", defaults={"name": "Argentina"})[0]


@pytest.fixture
def salta_province(argentina):
    """Create Salta province."""
    return Province.objects.get_or_create(
        id=1,
        defaults={"country": argentina, "code": "AR-A", "name": "Salta"},
    )[0]


@pytest.fixture(autouse=True)
def load_locations(db):
    """Load basic location data for all tests."""
    # Create Argentina
    argentina, _ = Country.objects.get_or_create(code="AR", defaults={"name": "Argentina"})

    # Create Salta province with id=1
    Province.objects.get_or_create(
        id=1,
        defaults={"country": argentina, "code": "AR-A", "name": "Salta"},
    )

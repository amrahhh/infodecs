import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from crops.models import Crop, CropCategory


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture that creates a Django user."""

    def _create_user(username="testuser", email="test@example.com", password="TestPass123!"):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

    return _create_user


@pytest.fixture
def user(create_user):
    """Return a default test user."""
    return create_user()


@pytest.fixture
def auth_client(api_client, user):
    """Return an APIClient authenticated with a JWT access token."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def category(db):
    """Create and return a sample CropCategory."""
    return CropCategory.objects.create(
        name="Cereals",
        description="Cereal grain crops.",
    )


@pytest.fixture
def crop(category):
    """Create and return a sample Crop linked to the default category."""
    return Crop.objects.create(
        name="Wheat",
        scientific_name="Triticum aestivum",
        category=category,
        description="A staple cereal crop.",
        growth_duration_days=120,
        water_requirements="medium",
    )

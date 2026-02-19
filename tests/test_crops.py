import pytest
from django.urls import reverse

from crops.models import Crop, CropCategory


@pytest.mark.django_db
class TestCropCategoryEndpoints:
    """Tests for /api/crops/categories/."""

    list_url = reverse("category-list")

    def test_create_category(self, auth_client):
        """Authenticated user can create a category (201)."""
        payload = {"name": "Test Legumes", "description": "Legume crops."}
        response = auth_client.post(self.list_url, payload, format="json")

        assert response.status_code == 201
        assert response.json()["name"] == "Test Legumes"

    def test_list_categories(self, auth_client, category):
        """Authenticated user can list categories (200)."""
        response = auth_client.get(self.list_url)

        assert response.status_code == 200
        assert response.json()["count"] >= 1

    def test_retrieve_category(self, auth_client, category):
        """Authenticated user can retrieve a single category."""
        url = reverse("category-detail", args=[category.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        assert response.json()["name"] == category.name

    def test_update_category(self, auth_client, category):
        """Authenticated user can update a category."""
        url = reverse("category-detail", args=[category.id])
        payload = {"name": "Updated Cereals", "description": "Updated description."}
        response = auth_client.put(url, payload, format="json")

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Cereals"

    def test_delete_category(self, auth_client, category):
        """Authenticated user can delete a category."""
        url = reverse("category-detail", args=[category.id])
        response = auth_client.delete(url)

        assert response.status_code == 204
        assert not CropCategory.objects.filter(id=category.id).exists()

    def test_unauthenticated_list_categories(self, api_client, category):
        """Unauthenticated access to categories returns 401."""
        response = api_client.get(self.list_url)

        assert response.status_code == 401


@pytest.mark.django_db
class TestCropEndpoints:
    """Tests for /api/crops/crops/."""

    list_url = reverse("crop-list")

    def test_create_crop(self, auth_client, category):
        """Authenticated user can create a crop (201)."""
        payload = {
            "name": "Test Rice",
            "scientific_name": "Oryza test",
            "category_id": category.id,
            "description": "A major food crop.",
            "growth_duration_days": 150,
            "water_requirements": "high",
        }
        response = auth_client.post(self.list_url, payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Rice"
        assert data["category"]["name"] == category.name

    def test_list_crops_paginated(self, auth_client, crop):
        """Listing crops returns paginated results."""
        response = auth_client.get(self.list_url)

        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert len(data["results"]) >= 1

    def test_crop_detail_nested_category(self, auth_client, crop):
        """Crop detail includes nested category data."""
        url = reverse("crop-detail", args=[crop.id])
        response = auth_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["category"], dict)
        assert data["category"]["name"] == crop.category.name

    def test_update_crop(self, auth_client, crop):
        """Authenticated user can update a crop."""
        url = reverse("crop-detail", args=[crop.id])
        payload = {
            "name": "Winter Wheat",
            "scientific_name": crop.scientific_name,
            "category_id": crop.category.id,
            "growth_duration_days": 130,
            "water_requirements": "medium",
        }
        response = auth_client.put(url, payload, format="json")

        assert response.status_code == 200
        assert response.json()["name"] == "Winter Wheat"

    def test_delete_crop(self, auth_client, crop):
        """Authenticated user can delete a crop."""
        url = reverse("crop-detail", args=[crop.id])
        response = auth_client.delete(url)

        assert response.status_code == 204
        assert not Crop.objects.filter(id=crop.id).exists()

    def test_unauthenticated_create_crop(self, api_client, category):
        """Unauthenticated crop creation returns 401."""
        payload = {
            "name": "Test Corn",
            "scientific_name": "Zea test",
            "category_id": category.id,
            "growth_duration_days": 90,
            "water_requirements": "medium",
        }
        response = api_client.post(self.list_url, payload, format="json")

        assert response.status_code == 401

    def test_filter_by_water_requirements(self, auth_client, category):
        """Filter crops by water_requirements returns correct results."""
        Crop.objects.create(
            name="FilterHigh Crop",
            scientific_name="Filterhigh testus",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )
        Crop.objects.create(
            name="FilterLow Crop",
            scientific_name="Filterlow testus",
            category=category,
            growth_duration_days=70,
            water_requirements="low",
        )

        response = auth_client.get(self.list_url, {"water_requirements": "high"})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] >= 1
        assert all(r["water_requirements"] == "high" for r in data["results"])

    def test_search_by_name(self, auth_client, crop):
        """Search crops by name using the search query parameter."""
        response = auth_client.get(self.list_url, {"search": "Test Wheat"})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] >= 1
        assert any("Test Wheat" in r["name"] for r in data["results"])

    def test_export_crops_excel(self, auth_client, crop):
        """Export endpoint returns an Excel file."""
        url = reverse("crop-export-crops")
        response = auth_client.get(url)

        assert response.status_code == 200
        assert (
            response["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "crops_export_" in response["Content-Disposition"]
        assert response["Content-Disposition"].endswith('.xlsx"')

    def test_filter_by_category(self, auth_client, category):
        """Filter crops by category ID returns only matching crops."""
        other_category = CropCategory.objects.create(name="Test Filter Legumes")
        Crop.objects.create(
            name="Cat Filter Rice",
            scientific_name="Oryza catfilter",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )
        Crop.objects.create(
            name="Cat Filter Lentil",
            scientific_name="Lens catfilter",
            category=other_category,
            growth_duration_days=100,
            water_requirements="low",
        )

        response = auth_client.get(self.list_url, {"category": category.id})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] >= 1
        assert all(r["category"] == category.id for r in data["results"])

    def test_ordering_by_growth_duration(self, auth_client, category):
        """Crops can be ordered by growth_duration_days."""
        Crop.objects.create(
            name="Order Millet",
            scientific_name="Panicum ordertest",
            category=category,
            growth_duration_days=70,
            water_requirements="low",
        )
        Crop.objects.create(
            name="Order Rice",
            scientific_name="Oryza ordertest",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )

        response = auth_client.get(
            self.list_url,
            {"ordering": "growth_duration_days", "category": category.id},
        )
        data = response.json()

        assert response.status_code == 200
        names = [r["name"] for r in data["results"]]
        assert names.index("Order Millet") < names.index("Order Rice")

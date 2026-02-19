import pytest
from django.urls import reverse

from crops.models import Crop, CropCategory


@pytest.mark.django_db
class TestCropCategoryEndpoints:
    """Tests for /api/crops/categories/."""

    list_url = reverse("category-list")

    def test_create_category(self, auth_client):
        """Authenticated user can create a category (201)."""
        payload = {"name": "Legumes", "description": "Legume crops."}
        response = auth_client.post(self.list_url, payload, format="json")

        assert response.status_code == 201
        assert response.json()["name"] == "Legumes"

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
        assert CropCategory.objects.count() == 0

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
            "name": "Rice",
            "scientific_name": "Oryza sativa",
            "category_id": category.id,
            "description": "A major food crop.",
            "growth_duration_days": 150,
            "water_requirements": "high",
        }
        response = auth_client.post(self.list_url, payload, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Rice"
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
        assert Crop.objects.count() == 0

    def test_unauthenticated_create_crop(self, api_client, category):
        """Unauthenticated crop creation returns 401."""
        payload = {
            "name": "Corn",
            "scientific_name": "Zea mays",
            "category_id": category.id,
            "growth_duration_days": 90,
            "water_requirements": "medium",
        }
        response = api_client.post(self.list_url, payload, format="json")

        assert response.status_code == 401

    def test_filter_by_water_requirements(self, auth_client, category):
        """Filter crops by water_requirements returns correct results."""
        Crop.objects.create(
            name="Rice",
            scientific_name="Oryza sativa",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )
        Crop.objects.create(
            name="Millet",
            scientific_name="Panicum miliaceum",
            category=category,
            growth_duration_days=70,
            water_requirements="low",
        )

        response = auth_client.get(self.list_url, {"water_requirements": "high"})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Rice"

    def test_search_by_name(self, auth_client, crop):
        """Search crops by name using the search query parameter."""
        response = auth_client.get(self.list_url, {"search": "Wheat"})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] >= 1
        assert any("Wheat" in r["name"] for r in data["results"])

    def test_export_crops_excel(self, auth_client, crop):
        """Export endpoint returns an Excel file."""
        url = reverse("crop-export-crops")
        response = auth_client.get(url)

        assert response.status_code == 200
        assert (
            response["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert 'filename="crops_export.xlsx"' in response["Content-Disposition"]

    def test_filter_by_category(self, auth_client, category):
        """Filter crops by category ID returns only matching crops."""
        other_category = CropCategory.objects.create(name="Legumes")
        Crop.objects.create(
            name="Rice",
            scientific_name="Oryza sativa",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )
        Crop.objects.create(
            name="Lentil",
            scientific_name="Lens culinaris",
            category=other_category,
            growth_duration_days=100,
            water_requirements="low",
        )

        response = auth_client.get(self.list_url, {"category": category.id})
        data = response.json()

        assert response.status_code == 200
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Rice"

    def test_ordering_by_growth_duration(self, auth_client, category):
        """Crops can be ordered by growth_duration_days."""
        Crop.objects.create(
            name="Millet",
            scientific_name="Panicum miliaceum",
            category=category,
            growth_duration_days=70,
            water_requirements="low",
        )
        Crop.objects.create(
            name="Rice",
            scientific_name="Oryza sativa",
            category=category,
            growth_duration_days=150,
            water_requirements="high",
        )

        response = auth_client.get(self.list_url, {"ordering": "growth_duration_days"})
        data = response.json()

        assert response.status_code == 200
        names = [r["name"] for r in data["results"]]
        assert names.index("Millet") < names.index("Rice")


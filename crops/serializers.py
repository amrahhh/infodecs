from rest_framework import serializers

from .models import Crop, CropCategory


class CropCategorySerializer(serializers.ModelSerializer):
    """Serializer for CropCategory model — used for both list and detail views."""

    class Meta:
        model = CropCategory
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class CropListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing crops (category as ID)."""

    class Meta:
        model = Crop
        fields = [
            "id",
            "name",
            "scientific_name",
            "category",
            "water_requirements",
            "growth_duration_days",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CropDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for a single crop — includes nested category data."""

    category = CropCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CropCategory.objects.all(),
        source="category",
        write_only=True,
        help_text="ID of the category this crop belongs to.",
    )

    class Meta:
        model = Crop
        fields = [
            "id",
            "name",
            "scientific_name",
            "category",
            "category_id",
            "description",
            "water_requirements",
            "growth_duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

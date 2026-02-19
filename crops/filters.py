"""
Django-filter FilterSet for the Crop model.
"""

import django_filters

from .models import Crop


class CropFilter(django_filters.FilterSet):
    """Allows filtering crops by category and water_requirements."""

    category = django_filters.NumberFilter(
        field_name="category__id",
        help_text="Filter by category ID.",
    )
    water_requirements = django_filters.CharFilter(
        field_name="water_requirements",
        help_text="Filter by water requirement level (low, medium, high).",
    )

    class Meta:
        model = Crop
        fields = ["category", "water_requirements"]

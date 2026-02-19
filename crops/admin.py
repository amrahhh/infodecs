"""
Admin configuration for the crops application.
"""

from django.contrib import admin

from .models import Crop, CropCategory


@admin.register(CropCategory)
class CropCategoryAdmin(admin.ModelAdmin):
    """Admin view for CropCategory."""

    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    """Admin view for Crop."""

    list_display = ("name", "scientific_name", "category", "water_requirements", "growth_duration_days")
    list_filter = ("category", "water_requirements")
    search_fields = ("name", "scientific_name")

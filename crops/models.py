"""
Models for the crops application.

Defines CropCategory and Crop models for managing agricultural crop data.
"""

from django.db import models


class CropCategory(models.Model):
    """Represents a category for grouping crops (e.g., Cereals, Legumes, Vegetables)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., Cereals, Legumes).",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional description of the category.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "crop categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="idx_category_name"),
        ]

    def __str__(self):
        """Return the category name."""
        return self.name


class Crop(models.Model):
    """Represents an individual crop with scientific and growing information."""

    class WaterRequirement(models.TextChoices):
        """Choices for crop water requirement levels."""

        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    name = models.CharField(
        max_length=100,
        help_text="Common name of the crop.",
    )
    scientific_name = models.CharField(
        max_length=150,
        help_text="Scientific (Latin) name of the crop.",
    )
    category = models.ForeignKey(
        CropCategory,
        on_delete=models.CASCADE,
        related_name="crops",
        help_text="Category this crop belongs to.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional description of the crop.",
    )
    growth_duration_days = models.PositiveIntegerField(
        help_text="Number of days from planting to harvest.",
    )
    water_requirements = models.CharField(
        max_length=10,
        choices=WaterRequirement.choices,
        help_text="Water requirement level: low, medium, or high.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="idx_crop_name"),
            models.Index(fields=["scientific_name"], name="idx_crop_sci_name"),
            models.Index(fields=["category"], name="idx_crop_category"),
        ]

    def __str__(self):
        """Return the crop's common and scientific name."""
        return f"{self.name} ({self.scientific_name})"

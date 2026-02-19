"""
Views for the crops application.

Provides ViewSets for CropCategory and Crop resources, plus an Excel export action.
"""

from io import BytesIO

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from openpyxl import Workbook
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CropFilter
from .models import Crop, CropCategory
from .serializers import CropCategorySerializer, CropDetailSerializer, CropListSerializer


@extend_schema_view(
    list=extend_schema(description="List all crop categories."),
    create=extend_schema(description="Create a new crop category."),
    retrieve=extend_schema(description="Retrieve a crop category by ID."),
    update=extend_schema(description="Update a crop category."),
    partial_update=extend_schema(description="Partially update a crop category."),
    destroy=extend_schema(description="Delete a crop category."),
)
class CropCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing crop categories.

    Provides list, create, retrieve, update, and delete operations.
    """

    queryset = CropCategory.objects.all()
    serializer_class = CropCategorySerializer


@extend_schema_view(
    list=extend_schema(description="List all crops with filtering, search, and pagination."),
    create=extend_schema(description="Create a new crop."),
    retrieve=extend_schema(description="Retrieve a crop by ID with nested category data."),
    update=extend_schema(description="Update a crop."),
    partial_update=extend_schema(description="Partially update a crop."),
    destroy=extend_schema(description="Delete a crop."),
)
class CropViewSet(viewsets.ModelViewSet):
    """ViewSet for managing crops.

    Supports filtering by category and water_requirements, searching
    by name and scientific_name, and ordering by name, created_at,
    and growth_duration_days.
    """

    filterset_class = CropFilter
    search_fields = ["name", "scientific_name"]
    ordering_fields = ["name", "created_at", "growth_duration_days"]
    ordering = ["name"]

    def get_queryset(self):
        """Return crops with optimized category prefetch."""
        return Crop.objects.select_related("category").all()

    def get_serializer_class(self):
        """Use compact serializer for list, detailed serializer otherwise."""
        if self.action == "list":
            return CropListSerializer
        return CropDetailSerializer

    @extend_schema(
        description="Export all crops to an Excel (.xlsx) file.",
        responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): bytes},
    )
    @action(detail=False, methods=["get"], url_path="export")
    def export_crops(self, request):
        """Export the full list of crops as an Excel spreadsheet."""
        crops = Crop.objects.select_related("category").all()

        wb = Workbook()
        ws = wb.active
        ws.title = "Crops"

        # Header row
        headers = [
            "ID",
            "Name",
            "Scientific Name",
            "Category",
            "Description",
            "Growth Duration (days)",
            "Water Requirements",
            "Created At",
            "Updated At",
        ]
        ws.append(headers)

        # Data rows
        for crop in crops:
            ws.append(
                [
                    crop.id,
                    crop.name,
                    crop.scientific_name,
                    crop.category.name,
                    crop.description,
                    crop.growth_duration_days,
                    crop.water_requirements,
                    crop.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    crop.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="crops_export.xlsx"'
        return response

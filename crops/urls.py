from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CropCategoryViewSet, CropViewSet

router = DefaultRouter()
router.register(r"categories", CropCategoryViewSet, basename="category")
router.register(r"crops", CropViewSet, basename="crop")

urlpatterns = [
    path("", include(router.urls)),
]

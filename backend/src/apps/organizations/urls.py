from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet

app_name = "organizations"

router = DefaultRouter()
router.register("", OrganizationViewSet, basename="organization")

urlpatterns = router.urls

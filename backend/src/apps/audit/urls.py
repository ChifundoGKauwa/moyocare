from rest_framework.routers import DefaultRouter

from .views import AuditEventViewSet

app_name = "audit"

router = DefaultRouter()
router.register("events", AuditEventViewSet, basename="audit-event")

urlpatterns = router.urls

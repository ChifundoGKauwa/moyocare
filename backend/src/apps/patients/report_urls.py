from rest_framework.routers import DefaultRouter

from .views import PatientReportViewSet

app_name = "patient_reports"

router = DefaultRouter()
router.register("", PatientReportViewSet, basename="patient-report")

urlpatterns = router.urls

from django.urls import path

from .views import ReportSummaryView

app_name = "reporting"

urlpatterns = [
    path("summary/", ReportSummaryView.as_view(), name="summary"),
]

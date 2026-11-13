from django.urls import path

from .views import SyncBatchDetailView, SyncBatchView

app_name = "synchronization"

urlpatterns = [
    path("batches/", SyncBatchView.as_view(), name="batch-create"),
    path(
        "batches/<uuid:client_batch_id>/",
        SyncBatchDetailView.as_view(),
        name="batch-detail",
    ),
]

import uuid

from django.conf import settings
from django.db import models

from apps.patients.models import PatientReport


class SyncBatch(models.Model):
    class Status(models.TextChoices):
        COMPLETE = "complete", "Complete"
        PARTIAL = "partial", "Partial"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_batch_id = models.UUIDField(unique=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sync_batches",
    )
    payload_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.FAILED)
    item_count = models.PositiveSmallIntegerField(default=0)
    success_count = models.PositiveSmallIntegerField(default=0)
    rejected_count = models.PositiveSmallIntegerField(default=0)
    received_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-received_at",)

    def __str__(self):
        return f"Sync batch {self.client_batch_id} ({self.status})"


class SyncItem(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        DUPLICATE = "duplicate", "Duplicate"
        REJECTED = "rejected", "Rejected"
        CONFLICT = "conflict", "Conflict"

    batch = models.ForeignKey(SyncBatch, on_delete=models.CASCADE, related_name="items")
    position = models.PositiveSmallIntegerField()
    client_id = models.UUIDField(null=True, blank=True)
    report = models.ForeignKey(
        PatientReport,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sync_items",
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    errors = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("position",)
        constraints = (
            models.UniqueConstraint(fields=("batch", "position"), name="unique_sync_batch_position"),
        )

    def __str__(self):
        return f"{self.batch.client_batch_id} item {self.position} ({self.status})"

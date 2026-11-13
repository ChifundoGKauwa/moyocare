import hashlib
import json
import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.patients.serializers import PatientReportSerializer
from apps.patients.services import ReportConflict, submit_patient_report

from .models import SyncBatch, SyncItem
from .serializers import SyncBatchRequestSerializer, SyncBatchResultSerializer


class SyncBatchConflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This batch identifier was already used for a different submission."
    default_code = "sync_batch_conflict"


def _payload_hash(data):
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _client_report_id(payload):
    if not isinstance(payload, dict) or not payload.get("client_id"):
        return None
    try:
        return uuid.UUID(str(payload["client_id"]))
    except (ValueError, TypeError, AttributeError):
        return None


def _json_errors(errors):
    return json.loads(json.dumps(errors, default=str))


class SyncBatchView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        input_serializer = SyncBatchRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        payload_hash = _payload_hash(request.data)
        batch_id = input_serializer.validated_data["client_batch_id"]
        payloads = input_serializer.validated_data["reports"]

        with transaction.atomic():
            batch, created = SyncBatch.objects.get_or_create(
                client_batch_id=batch_id,
                defaults={
                    "submitted_by": request.user,
                    "payload_hash": payload_hash,
                    "item_count": len(payloads),
                },
            )
            if not created:
                if batch.submitted_by_id != request.user.pk or batch.payload_hash != payload_hash:
                    raise SyncBatchConflict()
                output = SyncBatchResultSerializer(batch)
                return Response(output.data, status=status.HTTP_200_OK)

            successful = 0
            rejected = 0
            for position, payload in enumerate(payloads, start=1):
                item_client_id = _client_report_id(payload)
                if not isinstance(payload, dict):
                    SyncItem.objects.create(
                        batch=batch,
                        position=position,
                        status=SyncItem.Status.REJECTED,
                        errors={"detail": "Each report must be a JSON object."},
                    )
                    rejected += 1
                    continue

                report_serializer = PatientReportSerializer(
                    data=payload,
                    context={"request": request},
                )
                if not report_serializer.is_valid():
                    SyncItem.objects.create(
                        batch=batch,
                        position=position,
                        client_id=item_client_id,
                        status=SyncItem.Status.REJECTED,
                        errors=_json_errors(report_serializer.errors),
                    )
                    rejected += 1
                    continue

                try:
                    report, report_created = submit_patient_report(
                        validated_data=report_serializer.validated_data,
                        actor=request.user,
                    )
                except ReportConflict:
                    SyncItem.objects.create(
                        batch=batch,
                        position=position,
                        client_id=item_client_id,
                        status=SyncItem.Status.CONFLICT,
                        errors={"client_id": ["Identifier already exists with different report data."]},
                    )
                    rejected += 1
                    continue

                SyncItem.objects.create(
                    batch=batch,
                    position=position,
                    client_id=report.client_id,
                    report=report,
                    status=SyncItem.Status.CREATED if report_created else SyncItem.Status.DUPLICATE,
                )
                successful += 1

            batch.success_count = successful
            batch.rejected_count = rejected
            batch.status = (
                SyncBatch.Status.COMPLETE
                if rejected == 0
                else SyncBatch.Status.PARTIAL
                if successful
                else SyncBatch.Status.FAILED
            )
            batch.completed_at = timezone.now()
            batch.save(
                update_fields=("success_count", "rejected_count", "status", "completed_at")
            )
            record_event(
                actor=request.user,
                action="process",
                resource_type="sync_batch",
                resource_id=batch.pk,
                metadata={
                    "status": batch.status,
                    "item_count": batch.item_count,
                    "success_count": batch.success_count,
                    "rejected_count": batch.rejected_count,
                },
            )

        batch.refresh_from_db()
        output = SyncBatchResultSerializer(batch)
        return Response(output.data, status=status.HTTP_201_CREATED)


class SyncBatchDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, client_batch_id):
        batches = SyncBatch.objects.prefetch_related("items")
        if not request.user.is_staff:
            batches = batches.filter(submitted_by=request.user)
        batch = batches.filter(client_batch_id=client_batch_id).first()
        if batch is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SyncBatchResultSerializer(batch).data)

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from apps.audit.services import AuditedViewSetMixin

from .filters import PatientFilter
from .models import Patient, PatientReport
from .serializers import PatientReportSerializer, PatientSerializer
from .services import ReportConflict, submit_patient_report


class PatientViewSet(AuditedViewSetMixin, viewsets.ModelViewSet):
    """Limit identifiable patient records to staff and assigned facility members."""

    audit_resource_type = "patient"
    http_method_names = ("get", "post", "put", "patch", "head", "options")
    serializer_class = PatientSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_class = PatientFilter
    search_fields = ("first_name", "last_name", "village", "facility__name")
    ordering_fields = ("first_name", "last_name", "age", "created_at", "updated_at")
    ordering = ("last_name", "first_name")

    def get_queryset(self):
        queryset = Patient.objects.select_related("facility", "facility__organization")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(
            facility__memberships__user=self.request.user,
            facility__memberships__is_active=True,
            facility__is_active=True,
        ).distinct()

class PatientReportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PatientReportSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ("patient", "patient__facility")
    search_fields = ("patient__first_name", "patient__last_name", "action_taken")
    ordering_fields = ("created_at", "patient__last_name")
    ordering = ("-created_at",)

    def get_queryset(self):
        queryset = PatientReport.objects.select_related("patient", "reported_by", "patient__facility")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(
            patient__facility__memberships__user=self.request.user,
            patient__facility__memberships__is_active=True,
            patient__facility__is_active=True,
        ).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            report, created = submit_patient_report(
                validated_data=serializer.validated_data,
                actor=request.user,
            )
        except ReportConflict:
            return Response(
                {"client_id": ["This identifier was already used for a different report."]},
                status=status.HTTP_409_CONFLICT,
            )

        output = self.get_serializer(report)
        headers = self.get_success_headers(output.data) if created else {}
        return Response(
            output.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            headers=headers,
        )

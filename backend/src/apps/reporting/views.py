from collections import Counter
from datetime import datetime, time, timedelta

from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import record_event
from apps.patients.models import PatientReport


class ReportSummaryQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    facility = serializers.UUIDField(required=False)
    symptom = serializers.ChoiceField(choices=PatientReport.Symptom.choices, required=False)

    def validate(self, attrs):
        end_date = attrs.get("end_date", timezone.localdate())
        start_date = attrs.get("start_date", end_date - timedelta(days=29))
        if start_date > end_date:
            raise serializers.ValidationError({"start_date": "Must be on or before end_date."})
        if (end_date - start_date).days > 365:
            raise serializers.ValidationError("Date range cannot exceed 366 days.")
        attrs["start_date"] = start_date
        attrs["end_date"] = end_date
        return attrs


class ReportSummaryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query_serializer = ReportSummaryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data
        start = timezone.make_aware(datetime.combine(filters["start_date"], time.min))
        end = timezone.make_aware(
            datetime.combine(filters["end_date"] + timedelta(days=1), time.min)
        )
        reports = PatientReport.objects.filter(occurred_at__gte=start, occurred_at__lt=end)
        if filters.get("facility"):
            reports = reports.filter(patient__facility_id=filters["facility"])
        if not request.user.is_staff:
            reports = reports.filter(
                patient__facility__memberships__user=request.user,
                patient__facility__memberships__is_active=True,
                patient__facility__is_active=True,
            )

        symptom_filter = filters.get("symptom")
        total = 0
        actions_recorded = 0
        daily_counts = Counter()
        symptom_counts = Counter()
        facility_counts = {}

        rows = reports.select_related("patient__facility").values_list(
            "occurred_at",
            "symptoms",
            "action_taken",
            "patient__facility_id",
            "patient__facility__name",
            "patient__facility__district",
        )
        for occurred_at, symptoms, action_taken, facility_id, name, district in rows.iterator(
            chunk_size=1000
        ):
            if symptom_filter and symptom_filter not in symptoms:
                continue
            total += 1
            local_date = timezone.localtime(occurred_at).date()
            daily_counts[local_date.isoformat()] += 1
            if action_taken.strip():
                actions_recorded += 1
            for symptom in symptoms:
                symptom_counts[symptom] += 1
            key = str(facility_id)
            if key not in facility_counts:
                facility_counts[key] = {"id": key, "name": name, "district": district, "reports": 0}
            facility_counts[key]["reports"] += 1

        record_event(
            actor=request.user,
            action="view_summary",
            resource_type="reporting_summary",
            metadata={
                "start_date": filters["start_date"].isoformat(),
                "end_date": filters["end_date"].isoformat(),
                "facility": str(filters["facility"]) if filters.get("facility") else None,
                "symptom": symptom_filter,
            },
        )
        return Response(
            {
                "start_date": filters["start_date"],
                "end_date": filters["end_date"],
                "symptom": symptom_filter,
                "total_reports": total,
                "actions_recorded": actions_recorded,
                "symptom_counts": dict(sorted(symptom_counts.items())),
                "daily_counts": dict(sorted(daily_counts.items())),
                "facility_counts": sorted(
                    facility_counts.values(), key=lambda row: (-row["reports"], row["name"])
                ),
            }
        )

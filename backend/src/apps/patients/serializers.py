import uuid
from collections.abc import Mapping
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from apps.facilities.models import Facility

from .models import Patient, PatientReport


class RejectUnknownFieldsMixin:
    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            writable = {name for name, field in self.fields.items() if not field.read_only}
            unknown = set(data) - writable
            if unknown:
                raise serializers.ValidationError(
                    {name: ["Unknown or read-only field."] for name in sorted(unknown)}
                )
        return super().to_internal_value(data)


class PatientSerializer(RejectUnknownFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(source="sex", choices=Patient.Sex.choices, required=False)

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "facility",
            "first_name",
            "last_name",
            "age",
            "gender",
            "village",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_name(self, patient):
        return patient.name

    def validate_facility(self, facility):
        if not facility.is_active:
            raise serializers.ValidationError("Patients can only be registered at active facilities.")
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and not request.user.is_staff
            and not facility.memberships.filter(user=request.user, is_active=True).exists()
        ):
            raise serializers.ValidationError("You are not assigned to this facility.")
        return facility

class PatientIdentitySerializer(RejectUnknownFieldsMixin, serializers.Serializer):
    id = serializers.UUIDField()
    facility = serializers.PrimaryKeyRelatedField(queryset=Facility.objects.all())
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    village = serializers.CharField(max_length=120, required=False, allow_blank=True)

    @staticmethod
    def _has_membership(user, facility):
        return user.is_staff or facility.memberships.filter(user=user, is_active=True).exists()

    def validate(self, attrs):
        request = self.context.get("request")
        existing = Patient.objects.filter(pk=attrs["id"]).first()
        if existing:
            if request and request.user.is_authenticated and not self._has_membership(
                request.user, existing.facility
            ):
                raise serializers.ValidationError("Patient is not available to this account.")
            if (
                existing.facility_id != attrs["facility"].pk
                or existing.first_name != attrs["first_name"]
                or existing.last_name != attrs["last_name"]
                or "village" in attrs and existing.village != attrs["village"]
            ):
                raise serializers.ValidationError("Patient identity does not match.")
            return existing

        if (
            request
            and request.user.is_authenticated
            and not self._has_membership(request.user, attrs["facility"])
        ):
            raise serializers.ValidationError("Patient is not available to this account.")
        if not attrs["facility"].is_active:
            raise serializers.ValidationError({"facility": "New patients require an active facility."})

        return attrs


class PatientReferenceField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            serializer = PatientIdentitySerializer(data=data, context=self.context)
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data
        patient_id = serializers.UUIDField().run_validation(data)
        patient = Patient.objects.select_related("facility").filter(pk=patient_id).first()
        request = self.context.get("request")
        if patient is None or (
            request
            and request.user.is_authenticated
            and not PatientIdentitySerializer._has_membership(request.user, patient.facility)
        ):
            raise serializers.ValidationError("Patient is not available to this account.")
        return patient

    def to_representation(self, value):
        return str(value.pk)


class PatientReportSerializer(RejectUnknownFieldsMixin, serializers.ModelSerializer):
    client_id = serializers.UUIDField()
    patient = PatientReferenceField()
    name = serializers.CharField(source="patient.name", read_only=True)
    patient_name = serializers.CharField(max_length=301, write_only=True, required=False)
    age = serializers.IntegerField(
        source="age_at_report",
        required=True,
        allow_null=True,
        min_value=0,
        max_value=120,
    )
    gender = serializers.ChoiceField(
        source="gender_at_report",
        choices=Patient.Sex.choices,
        required=True,
    )
    symptoms = serializers.ListField(
        child=serializers.ChoiceField(choices=PatientReport.Symptom.choices),
        max_length=len(PatientReport.Symptom.choices),
    )
    action_taken = serializers.CharField(max_length=2000, allow_blank=True, required=False)
    occurred_at = serializers.DateTimeField(required=False)

    class Meta:
        model = PatientReport
        fields = (
            "id",
            "client_id",
            "patient",
            "name",
            "patient_name",
            "age",
            "gender",
            "symptoms",
            "action_taken",
            "occurred_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def _is_existing_submission(self, patient):
        try:
            client_id = uuid.UUID(str(self.initial_data.get("client_id", "")))
        except (ValueError, TypeError, AttributeError):
            return False
        return PatientReport.objects.filter(
            client_id=client_id,
            patient_id=patient.pk,
        ).exists()

    def validate_patient(self, patient):
        if isinstance(patient, dict):
            return patient
        is_retry = self._is_existing_submission(patient)
        if not patient.is_active and not is_retry:
            raise serializers.ValidationError("Reports cannot be submitted for inactive patients.")
        if not patient.facility.is_active and not is_retry:
            raise serializers.ValidationError("Reports cannot be submitted for an inactive facility.")

        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and not request.user.is_staff
            and not patient.facility.memberships.filter(user=request.user, is_active=True).exists()
        ):
            raise serializers.ValidationError("You are not assigned to this patient's facility.")
        return patient

    def validate_symptoms(self, symptoms):
        if len(symptoms) != len(set(symptoms)):
            raise serializers.ValidationError("A symptom can only be selected once.")
        return symptoms

    def validate_occurred_at(self, occurred_at):
        if occurred_at and occurred_at > timezone.now() + timedelta(hours=24):
            raise serializers.ValidationError("Encounter time cannot be more than 24 hours in the future.")
        return occurred_at

    def validate(self, attrs):
        patient = attrs["patient"]
        submitted_name = attrs.pop("patient_name", None)
        patient_name = (
            " ".join((patient["first_name"], patient["last_name"]))
            if isinstance(patient, dict)
            else patient.name
        )
        if submitted_name and " ".join(submitted_name.split()).casefold() != patient_name.casefold():
            raise serializers.ValidationError(
                {"patient_name": "The submitted name does not match the selected patient."}
            )
        return attrs

from rest_framework import serializers

from .models import Patient, PatientReport


class PatientSerializer(serializers.ModelSerializer):
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

class PatientReportSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField()
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    name = serializers.CharField(source="patient.name", read_only=True)
    patient_name = serializers.CharField(max_length=301, write_only=True, required=False)
    age = serializers.IntegerField(
        source="age_at_report",
        required=False,
        allow_null=True,
        min_value=0,
        max_value=120,
    )
    gender = serializers.ChoiceField(
        source="gender_at_report",
        choices=Patient.Sex.choices,
        required=False,
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
            "reported_by",
            "created_at",
        )
        read_only_fields = ("id", "patient_name", "reported_by", "created_at")

    def validate_patient(self, patient):
        if not patient.is_active:
            raise serializers.ValidationError("Reports cannot be submitted for inactive patients.")
        if not patient.facility.is_active:
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

    def validate(self, attrs):
        patient = attrs["patient"]
        submitted_name = attrs.pop("patient_name", None)
        if submitted_name and " ".join(submitted_name.split()).casefold() != patient.name.casefold():
            raise serializers.ValidationError(
                {"patient_name": "The submitted name does not match the selected patient."}
            )
        attrs.setdefault("age_at_report", patient.age)
        attrs.setdefault("gender_at_report", patient.sex)
        return attrs

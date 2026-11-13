from django.db import transaction

from apps.audit.services import record_event

from .models import Patient, PatientReport


class ReportConflict(Exception):
    """A client id was reused with content that differs from its stored report."""


@transaction.atomic
def submit_patient_report(*, validated_data, actor):
    values = dict(validated_data)
    client_id = values.pop("client_id")
    patient_data = values["patient"]
    if isinstance(patient_data, dict):
        patient, patient_created = Patient.objects.get_or_create(
            pk=patient_data["id"],
            defaults={
                "facility": patient_data["facility"],
                "first_name": patient_data["first_name"],
                "last_name": patient_data["last_name"],
                "age": values["age_at_report"],
                "sex": values["gender_at_report"],
                "village": patient_data.get("village", ""),
            },
        )
        if (
            patient.facility_id != patient_data["facility"].pk
            or patient.first_name != patient_data["first_name"]
            or patient.last_name != patient_data["last_name"]
            or "village" in patient_data and patient.village != patient_data["village"]
        ):
            raise ReportConflict
        values["patient"] = patient
        if patient_created:
            record_event(
                actor=actor,
                action="create",
                resource_type="patient",
                resource_id=patient.pk,
            )

    report, created = PatientReport.objects.get_or_create(
        client_id=client_id,
        defaults={**values, "reported_by": actor},
    )

    if not created and any(
        (
            report.patient_id != values["patient"].pk,
            report.age_at_report != values["age_at_report"],
            report.gender_at_report != values["gender_at_report"],
            report.symptoms != values["symptoms"],
            report.action_taken != values.get("action_taken", ""),
            "occurred_at" in values and report.occurred_at != values["occurred_at"],
        )
    ):
        raise ReportConflict

    if created:
        record_event(
            actor=actor,
            action="submit",
            resource_type="patient_report",
            resource_id=report.pk,
        )
    return report, created

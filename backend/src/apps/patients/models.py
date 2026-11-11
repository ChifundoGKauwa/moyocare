import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """A person registered for community health reporting."""

    class Sex(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        OTHER = "other", "Other"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="patients",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(null=True, blank=True, validators=(MaxValueValidator(120),))
    sex = models.CharField(max_length=10, choices=Sex.choices, default=Sex.UNKNOWN)
    village = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("last_name", "first_name")
        indexes = (
            models.Index(fields=("facility", "last_name", "first_name")),
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def name(self):
        return str(self)

class PatientReport(models.Model):
    """A symptom and action record for one patient encounter."""

    class Symptom(models.TextChoices):
        FEVER = "fever", "Fever"
        COUGH = "cough", "Cough"
        DIARRHEA = "diarrhea", "Diarrhea"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="reports")
    age_at_report = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=(MaxValueValidator(120),),
    )
    gender_at_report = models.CharField(
        max_length=10,
        choices=Patient.Sex.choices,
        default=Patient.Sex.UNKNOWN,
    )
    symptoms = models.JSONField(default=list)
    action_taken = models.CharField(max_length=2000, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    reported_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="patient_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = (models.Index(fields=("patient", "created_at")),)

    def __str__(self):
        return f"Report for {self.patient} at {self.created_at}"

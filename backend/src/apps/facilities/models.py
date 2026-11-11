import uuid

from django.conf import settings
from django.db import models


class Facility(models.Model):
    """A health service delivery site operated by an organization."""

    class FacilityType(models.TextChoices):
        HOSPITAL = "hospital", "Hospital"
        HEALTH_CENTRE = "health_centre", "Health centre"
        CLINIC = "clinic", "Clinic"
        DISPENSARY = "dispensary", "Dispensary"
        COMMUNITY = "community", "Community site"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="facilities",
    )
    name = models.CharField(max_length=255)
    code = models.SlugField(max_length=50, unique=True)
    facility_type = models.CharField(
        max_length=20,
        choices=FacilityType.choices,
        default=FacilityType.OTHER,
    )
    district = models.CharField(max_length=120, blank=True)
    community = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "facility"
        verbose_name_plural = "facilities"

    def __str__(self):
        return f"{self.name} ({self.code})"


class FacilityMembership(models.Model):
    """Grant a user access to records belonging to one facility."""

    class Role(models.TextChoices):
        HEALTH_WORKER = "health_worker", "Health worker"
        SUPERVISOR = "supervisor", "Supervisor"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="facility_memberships",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.HEALTH_WORKER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("facility__name", "user__email")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "facility"),
                name="unique_user_facility_membership",
            ),
        )

    def __str__(self):
        return f"{self.user} at {self.facility} ({self.role})"

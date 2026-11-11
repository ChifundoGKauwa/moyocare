import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Organization(models.Model):
    """An organization in the health system's reporting hierarchy."""

    class OrganizationType(models.TextChoices):
        MINISTRY = "ministry", "Ministry"
        DISTRICT = "district", "District"
        PARTNER = "partner", "Partner"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.SlugField(max_length=50, unique=True)
    organization_type = models.CharField(
        max_length=20,
        choices=OrganizationType.choices,
        default=OrganizationType.OTHER,
    )
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "organization"
        verbose_name_plural = "organizations"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        ancestor = self.parent
        while ancestor is not None:
            if ancestor.pk == self.pk:
                raise ValidationError({"parent": "An organization cannot be its own ancestor."})
            ancestor = ancestor.parent

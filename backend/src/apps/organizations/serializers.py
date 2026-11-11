from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "code",
            "organization_type",
            "description",
            "parent",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_parent(self, parent):
        instance = self.instance
        ancestor = parent
        while ancestor is not None:
            if instance is not None and ancestor.pk == instance.pk:
                raise serializers.ValidationError(
                    "An organization cannot be its own ancestor."
                )
            ancestor = ancestor.parent
        return parent

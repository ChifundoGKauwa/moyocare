from rest_framework import serializers

from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)
    actor_id = serializers.CharField(source="actor_identifier", read_only=True)

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "actor",
            "actor_id",
            "actor_email",
            "action",
            "resource_type",
            "resource_id",
            "metadata",
            "created_at",
        )

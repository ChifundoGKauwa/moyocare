from collections.abc import Mapping

from rest_framework import serializers

from .models import SyncBatch, SyncItem


class SyncBatchRequestSerializer(serializers.Serializer):
    client_batch_id = serializers.UUIDField()
    reports = serializers.ListField(
        child=serializers.JSONField(allow_null=True),
        min_length=1,
        max_length=100,
    )

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {name: ["Unknown field."] for name in sorted(unknown)}
                )
        return super().to_internal_value(data)


class SyncItemResultSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source="report.pk", read_only=True, allow_null=True)

    class Meta:
        model = SyncItem
        fields = ("position", "client_id", "status", "report_id", "errors")


class SyncBatchResultSerializer(serializers.ModelSerializer):
    items = SyncItemResultSerializer(many=True, read_only=True)

    class Meta:
        model = SyncBatch
        fields = (
            "id",
            "client_batch_id",
            "status",
            "item_count",
            "success_count",
            "rejected_count",
            "received_at",
            "completed_at",
            "items",
        )

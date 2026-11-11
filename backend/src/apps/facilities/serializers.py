from rest_framework import serializers

from .models import Facility


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = (
            "id",
            "organization",
            "name",
            "code",
            "facility_type",
            "district",
            "community",
            "address",
            "phone_number",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

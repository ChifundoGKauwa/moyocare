
from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):


    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "date_joined",
        )


class ChangePasswordSerializer(serializers.Serializer):
    

    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "The current password is incorrect."
            )

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user

        password_validation.validate_password(value, user)

        return value

    def validate(self, attrs):
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": (
                    "The new password must differ from the current password."
                )
            })

        return attrs

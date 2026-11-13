
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from apps.audit.services import record_event

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    CreateStaffUserSerializer,
    UserSerializer,
)


class UserProfileView(APIView):


    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        record_event(
            actor=request.user,
            action="profile_update",
            resource_type="user",
            resource_id=request.user.pk,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CreateStaffUserView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    @transaction.atomic
    def post(self, request):
        serializer = CreateStaffUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name", ""),
            last_name=serializer.validated_data.get("last_name", ""),
            is_active=serializer.validated_data.get("is_active", True),
            is_staff=serializer.validated_data.get("is_staff", True),
        )

        record_event(
            actor=request.user,
            action="create",
            resource_type="user",
            resource_id=user.pk,
            metadata={"created_by_admin": True},
        )

        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
            },
            status=status.HTTP_201_CREATED,
        )


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=("password",))
        record_event(
            actor=request.user,
            action="password_change",
            resource_type="user",
            resource_id=request.user.pk,
        )
        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

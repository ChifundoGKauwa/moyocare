
from django.contrib.auth import update_session_auth_hash
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .serializers import ChangePasswordSerializer, UserSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


class UserProfileView(APIView):
    

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )



class ChangePasswordView(APIView):


    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        
        request.user.set_password(
            serializer.validated_data["new_password"]
        )
        request.user.save(update_fields=["password"])

        # Revoke all outstanding refresh tokens for this user.
        outstanding_tokens = OutstandingToken.objects.filter(
            user=request.user
        )

        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(
                token=outstanding_token
            )

        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )

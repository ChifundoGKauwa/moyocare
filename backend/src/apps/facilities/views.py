from django.db.models.deletion import ProtectedError
from rest_framework import permissions, viewsets
from rest_framework.exceptions import APIException

from .models import Facility
from .serializers import FacilitySerializer


class ResourceInUse(APIException):
    status_code = 409
    default_detail = "This facility has assigned users or patients and cannot be deleted. Deactivate it instead."
    default_code = "resource_in_use"


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class FacilityViewSet(viewsets.ModelViewSet):
    serializer_class = FacilitySerializer
    permission_classes = (IsStaffOrReadOnly,)
    filterset_fields = ("organization", "facility_type", "district", "community", "is_active")
    search_fields = ("name", "code", "district", "community", "address")
    ordering_fields = ("name", "code", "district", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        queryset = Facility.objects.select_related("organization")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True,
        ).distinct()

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as exc:
            raise ResourceInUse() from exc

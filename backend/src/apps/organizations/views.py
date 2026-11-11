from django.db.models.deletion import ProtectedError
from rest_framework import permissions, viewsets
from rest_framework.exceptions import APIException

from .models import Organization
from .serializers import OrganizationSerializer


class ResourceInUse(APIException):
    status_code = 409
    default_detail = "This organization has child organizations or facilities and cannot be deleted."
    default_code = "resource_in_use"


class IsStaffOrReadOnly(permissions.BasePermission):


    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("parent").all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsStaffOrReadOnly,)
    filterset_fields = ("organization_type", "parent", "is_active")
    search_fields = ("name", "code", "description")
    ordering_fields = ("name", "code", "created_at", "updated_at")
    ordering = ("name",)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as exc:
            raise ResourceInUse() from exc

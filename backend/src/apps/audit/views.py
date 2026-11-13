from rest_framework import permissions, viewsets

from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditEvent.objects.select_related("actor").all()
    serializer_class = AuditEventSerializer
    permission_classes = (permissions.IsAdminUser,)
    filterset_fields = ("actor", "action", "resource_type", "resource_id")
    search_fields = ("resource_id", "actor__email")
    ordering_fields = ("created_at", "action", "resource_type")
    ordering = ("-created_at",)

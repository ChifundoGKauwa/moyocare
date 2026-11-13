from django.db import transaction

from .models import AuditEvent


def record_event(*, actor, action, resource_type, resource_id="", metadata=None):
    
    return AuditEvent.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        actor_identifier=(
            str(actor.pk) if getattr(actor, "is_authenticated", False) else ""
        ),
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else "",
        metadata=metadata or {},
    )


class AuditedViewSetMixin:
    

    audit_resource_type = None

    @transaction.atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        record_event(
            actor=self.request.user,
            action="create",
            resource_type=self.audit_resource_type,
            resource_id=instance.pk,
        )

    @transaction.atomic
    def perform_update(self, serializer):
        was_active = getattr(serializer.instance, "is_active", None)
        instance = serializer.save()
        is_inactive = was_active is True and getattr(instance, "is_active", True) is False
        record_event(
            actor=self.request.user,
            action="deactivate" if is_inactive else "update",
            resource_type=self.audit_resource_type,
            resource_id=instance.pk,
        )

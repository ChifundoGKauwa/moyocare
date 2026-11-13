from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor_identifier", "actor", "action", "resource_type", "resource_id")
    list_filter = ("action", "resource_type", "created_at")
    search_fields = ("resource_id", "actor_identifier", "actor__email")
    list_select_related = ("actor",)
    readonly_fields = (
        "id",
        "actor",
        "actor_identifier",
        "action",
        "resource_type",
        "resource_id",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

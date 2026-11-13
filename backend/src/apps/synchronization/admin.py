from django.contrib import admin

from .models import SyncBatch, SyncItem


class SyncItemInline(admin.TabularInline):
    model = SyncItem
    extra = 0
    can_delete = False
    readonly_fields = ("position", "client_id", "report", "status", "errors")


@admin.register(SyncBatch)
class SyncBatchAdmin(admin.ModelAdmin):
    list_display = (
        "client_batch_id",
        "submitted_by",
        "status",
        "item_count",
        "success_count",
        "rejected_count",
        "received_at",
    )
    list_filter = ("status", "received_at")
    search_fields = ("client_batch_id", "submitted_by__email")
    list_select_related = ("submitted_by",)
    readonly_fields = (
        "id",
        "client_batch_id",
        "submitted_by",
        "payload_hash",
        "status",
        "item_count",
        "success_count",
        "rejected_count",
        "received_at",
        "completed_at",
    )
    inlines = (SyncItemInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

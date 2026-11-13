from typing import ClassVar

from django.contrib import admin

from apps.audit.services import record_event

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization_type", "parent", "is_active")
    list_filter = ("organization_type", "is_active")
    search_fields = ("name", "code")
    list_select_related = ("parent",)
    prepopulated_fields: ClassVar[dict] = {"code": ("name",)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_event(
            actor=request.user,
            action="update" if change else "create",
            resource_type="organization",
            resource_id=obj.pk,
        )

    def delete_model(self, request, obj):
        record_event(
            actor=request.user,
            action="delete",
            resource_type="organization",
            resource_id=obj.pk,
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            record_event(
                actor=request.user,
                action="delete",
                resource_type="organization",
                resource_id=obj.pk,
            )
        super().delete_queryset(request, queryset)

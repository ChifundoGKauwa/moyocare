from typing import ClassVar

from django.contrib import admin

from apps.audit.services import record_event

from .models import Facility, FacilityMembership


class FacilityMembershipInline(admin.TabularInline):
    model = FacilityMembership
    extra = 0
    autocomplete_fields = ("user",)


def _membership_metadata(membership):
    return {
        "user_id": str(membership.user_id),
        "facility_id": str(membership.facility_id),
        "role": membership.role,
        "is_active": membership.is_active,
    }


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "facility_type", "organization", "district", "is_active")
    list_filter = ("facility_type", "organization", "district", "is_active")
    search_fields = ("name", "code", "district", "community")
    list_select_related = ("organization",)
    prepopulated_fields: ClassVar[dict] = {"code": ("name",)}
    inlines = (FacilityMembershipInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_event(
            actor=request.user,
            action="update" if change else "create",
            resource_type="facility",
            resource_id=obj.pk,
        )

    def delete_model(self, request, obj):
        record_event(
            actor=request.user,
            action="delete",
            resource_type="facility",
            resource_id=obj.pk,
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            record_event(
                actor=request.user,
                action="delete",
                resource_type="facility",
                resource_id=obj.pk,
            )
        super().delete_queryset(request, queryset)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        for membership in formset.new_objects:
            record_event(
                actor=request.user,
                action="assign",
                resource_type="facility_membership",
                resource_id=membership.pk,
                metadata=_membership_metadata(membership),
            )
        for membership, _changed_fields in formset.changed_objects:
            record_event(
                actor=request.user,
                action="update",
                resource_type="facility_membership",
                resource_id=membership.pk,
                metadata={
                    **_membership_metadata(membership),
                    "changed_fields": list(_changed_fields),
                },
            )
        for membership in formset.deleted_objects:
            record_event(
                actor=request.user,
                action="remove",
                resource_type="facility_membership",
                resource_id=membership.pk,
                metadata=_membership_metadata(membership),
            )


@admin.register(FacilityMembership)
class FacilityMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "role", "is_active")
    list_filter = ("role", "is_active", "facility")
    search_fields = ("user__email", "facility__name", "facility__code")
    list_select_related = ("user", "facility")
    autocomplete_fields = ("user", "facility")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        record_event(
            actor=request.user,
            action="update" if change else "assign",
            resource_type="facility_membership",
            resource_id=obj.pk,
            metadata=_membership_metadata(obj),
        )

    def delete_model(self, request, obj):
        record_event(
            actor=request.user,
            action="remove",
            resource_type="facility_membership",
            resource_id=obj.pk,
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for membership in queryset:
            record_event(
                actor=request.user,
                action="remove",
                resource_type="facility_membership",
                resource_id=membership.pk,
                metadata=_membership_metadata(membership),
            )
        super().delete_queryset(request, queryset)

from typing import ClassVar

from django.contrib import admin

from .models import Facility, FacilityMembership


class FacilityMembershipInline(admin.TabularInline):
    model = FacilityMembership
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "facility_type", "organization", "district", "is_active")
    list_filter = ("facility_type", "organization", "district", "is_active")
    search_fields = ("name", "code", "district", "community")
    list_select_related = ("organization",)
    prepopulated_fields: ClassVar[dict] = {"code": ("name",)}
    inlines = (FacilityMembershipInline,)


@admin.register(FacilityMembership)
class FacilityMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "role", "is_active")
    list_filter = ("role", "is_active", "facility")
    search_fields = ("user__email", "facility__name", "facility__code")
    list_select_related = ("user", "facility")
    autocomplete_fields = ("user", "facility")

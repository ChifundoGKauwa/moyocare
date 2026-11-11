from typing import ClassVar

from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization_type", "parent", "is_active")
    list_filter = ("organization_type", "is_active")
    search_fields = ("name", "code")
    list_select_related = ("parent",)
    prepopulated_fields: ClassVar[dict] = {"code": ("name",)}

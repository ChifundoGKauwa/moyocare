from django.contrib import admin

from .models import Patient, PatientReport


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "facility", "age", "sex", "village", "is_active")
    list_filter = ("sex", "facility", "is_active")
    search_fields = ("first_name", "last_name", "village", "facility__name")
    list_select_related = ("facility",)
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PatientReport)
class PatientReportAdmin(admin.ModelAdmin):
    list_display = ("client_id", "patient", "reported_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("client_id", "patient__first_name", "patient__last_name", "action_taken")
    list_select_related = ("patient", "reported_by")
    readonly_fields = (
        "id",
        "client_id",
        "patient",
        "age_at_report",
        "gender_at_report",
        "symptoms",
        "action_taken",
        "occurred_at",
        "reported_by",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

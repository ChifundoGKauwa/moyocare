
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.audit.services import record_event

from .forms import UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    readonly_fields = ("id", "date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal information", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        previous_permissions = None
        if change:
            previous = self.model.objects.filter(pk=obj.pk).values(
                "is_active", "is_staff", "is_superuser"
            ).first()
            previous_permissions = previous
        super().save_model(request, obj, form, change)
        record_event(
            actor=request.user,
            action="privilege_update" if change else "create",
            resource_type="user",
            resource_id=obj.pk,
            metadata={
                "before": previous_permissions,
                "after": {
                    "is_active": obj.is_active,
                    "is_staff": obj.is_staff,
                    "is_superuser": obj.is_superuser,
                },
            },
        )

    def delete_model(self, request, obj):
        record_event(
            actor=request.user,
            action="delete",
            resource_type="user",
            resource_id=obj.pk,
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for user in queryset:
            record_event(
                actor=request.user,
                action="delete",
                resource_type="user",
                resource_id=user.pk,
            )
        super().delete_queryset(request, queryset)

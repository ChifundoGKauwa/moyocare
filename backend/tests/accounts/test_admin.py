
import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserAdmin:

    def test_user_model_is_registered(self):
        assert User in admin.site._registry

    def test_admin_uses_custom_user_admin(self):
        user_admin = admin.site._registry[User]

        assert user_admin.model is User

    def test_admin_search_fields(self):
        user_admin = admin.site._registry[User]

        assert "email" in user_admin.search_fields
        assert "first_name" in user_admin.search_fields
        assert "last_name" in user_admin.search_fields

    def test_admin_list_display(self):
        user_admin = admin.site._registry[User]

        assert "email" in user_admin.list_display
        assert "is_active" in user_admin.list_display
        assert "is_staff" in user_admin.list_display

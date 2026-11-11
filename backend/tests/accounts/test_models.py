
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


@pytest.mark.django_db
class TestUserManager:

    def test_create_user(self):
        user = User.objects.create_user(
            email="hsa@example.com",
            password="StrongPassword123!",
        )

        assert user.email == "hsa@example.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_email_normalization(self):
        user = User.objects.create_user(
            email="HSA@EXAMPLE.COM",
            password="StrongPassword123!",
        )

        assert user.email == "hsa@example.com"

    def test_email_is_required(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="")

    def test_password_is_hashed(self):
        password = "StrongPassword123!"

        user = User.objects.create_user(
            email="hsa@example.com",
            password=password,
        )

        assert user.password != password
        assert user.check_password(password)

    def test_user_without_password_has_unusable_password(self):
        user = User.objects.create_user(
            email="hsa@example.com",
        )

        assert not user.has_usable_password()

    def test_user_has_uuid_primary_key(self):
        user = User.objects.create_user(
            email="hsa@example.com",
            password="StrongPassword123!",
        )

        assert isinstance(user.pk, uuid.UUID)

    def test_email_uniqueness(self):
        User.objects.create_user(
            email="hsa@example.com",
            password="StrongPassword123!",
        )

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="hsa@example.com",
                password="AnotherPassword123!",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
        )

        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_superuser_requires_staff(self):
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="StrongPassword123!",
                is_staff=False,
            )

    def test_superuser_requires_superuser_status(self):
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="StrongPassword123!",
                is_superuser=False,
            )

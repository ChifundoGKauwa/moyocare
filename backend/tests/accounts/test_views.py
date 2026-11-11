
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="hsa@example.com",
        password="StrongPassword123!",
        first_name="John",
        last_name="Banda",
    )


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestUserProfileView:

    def test_authenticated_user_can_retrieve_profile(
        self, authenticated_client, user
    ):
        response = authenticated_client.get("/api/v1/auth/me/")

        assert response.status_code == 200
        assert response.data["id"] == str(user.id)
        assert response.data["email"] == user.email
        assert response.data["first_name"] == "John"

    def test_unauthenticated_user_cannot_retrieve_profile(self):
        response = APIClient().get("/api/v1/auth/me/")

        assert response.status_code == 401

    def test_authenticated_user_can_update_profile(
        self, authenticated_client, user
    ):
        response = authenticated_client.patch(
            "/api/v1/auth/me/",
            {
                "first_name": "Peter",
                "last_name": "Phiri",
            },
        )

        assert response.status_code == 200

        user.refresh_from_db()

        assert user.first_name == "Peter"
        assert user.last_name == "Phiri"

    def test_user_cannot_update_email(
        self, authenticated_client, user
    ):
        response = authenticated_client.patch(
            "/api/v1/auth/me/",
            {"email": "another@example.com"},
        )

        assert response.status_code == 200

        user.refresh_from_db()

        assert user.email == "hsa@example.com"


@pytest.mark.django_db
class TestChangePasswordView:

    def test_user_can_change_password(
        self, authenticated_client, user
    ):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "StrongPassword123!",
                "new_password": "AnotherStrongPassword456!",
            },
        )

        assert response.status_code == 200

        user.refresh_from_db()

        assert user.check_password("AnotherStrongPassword456!")

    def test_incorrect_current_password_is_rejected(
        self, authenticated_client
    ):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "WrongPassword123!",
                "new_password": "AnotherStrongPassword456!",
            },
        )

        assert response.status_code == 400

    def test_weak_new_password_is_rejected(
        self, authenticated_client
    ):
        response = authenticated_client.post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "StrongPassword123!",
                "new_password": "123",
            },
        )

        assert response.status_code == 400

    def test_unauthenticated_user_cannot_change_password(self):
        response = APIClient().post(
            "/api/v1/auth/change-password/",
            {
                "current_password": "StrongPassword123!",
                "new_password": "AnotherStrongPassword456!",
            },
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestJWTAuthentication:

    def test_user_can_obtain_jwt_tokens(self, user):
        response = APIClient().post(
            "/api/v1/auth/token/",
            {
                "email": user.email,
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_invalid_credentials_are_rejected(self, user):
        response = APIClient().post(
            "/api/v1/auth/token/",
            {
                "email": user.email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    def test_user_can_refresh_access_token(self, user):
        refresh_token = RefreshToken.for_user(user)

        response = APIClient().post(
            "/api/v1/auth/token/refresh/",
            {"refresh": str(refresh_token)},
        )

        assert response.status_code == 200
        assert "access" in response.data

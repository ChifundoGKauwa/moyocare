
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ChangePasswordView, UserProfileView


app_name = "accounts"

urlpatterns = [
    # Authentication
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token-obtain",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # User profile
    path(
        "me/",
        UserProfileView.as_view(),
        name="user-profile",
    ),

    # Password management
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
]

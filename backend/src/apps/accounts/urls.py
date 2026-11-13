
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    ChangePasswordView,
    CreateStaffUserView,
    UserProfileView,
)

app_name = "accounts"

urlpatterns = [
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
    path(
        "register/",
        CreateStaffUserView.as_view(),
        name="user-register",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
]

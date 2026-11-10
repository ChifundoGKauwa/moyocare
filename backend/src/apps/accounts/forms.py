
from django.contrib.auth.forms import (
    UserChangeForm as BaseUserChangeForm,
    UserCreationForm as BaseUserCreationForm,
)

from .models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

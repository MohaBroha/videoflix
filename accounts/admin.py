from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the custom user model."""

    ordering = ("email",)
    list_display = ("email", "is_active", "is_staff", "date_joined")

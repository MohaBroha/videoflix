from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Administrative settings for the video model."""

    list_display = (
        "id",
        "title",
        "category",
        "created_at",
    )

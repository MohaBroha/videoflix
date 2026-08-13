from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Application configuration for the videos app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "videos"

    def ready(self):
        """Import the app task registrations when Django starts."""

        from . import tasks  # noqa: F401

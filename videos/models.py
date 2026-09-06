import shutil
from pathlib import Path

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Video(models.Model):
    """Store metadata for a video and its uploaded assets."""

    class Meta:
        ordering = ["title"]

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    video_file = models.FileField(upload_to="videos/")
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the video's title as the model string representation."""

        return self.title


def delete_video_related_files(instance):
    """Remove only the files and HLS folder belonging to this specific video."""

    if instance.video_file:
        try:
            instance.video_file.delete(save=False)
        except FileNotFoundError:
            pass

    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except FileNotFoundError:
            pass

    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(instance.pk)
    if hls_dir.exists():
        shutil.rmtree(hls_dir, ignore_errors=True)


@receiver(post_delete, sender=Video)
def remove_video_media_on_delete(sender, instance, **kwargs):
    """Delete the media files and generated HLS directory for the removed video."""

    delete_video_related_files(instance)

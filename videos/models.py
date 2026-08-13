from django.db import models


class Video(models.Model):
    """Store metadata for a video and its uploaded assets."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")
    video_file = models.FileField(upload_to="videos/")
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the video's title as the model string representation."""

        return self.title

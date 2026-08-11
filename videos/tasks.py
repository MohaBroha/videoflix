from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import job

from videos.functions import convert_video
from videos.models import Video


@job
def process_video(video_id, video_path):
    convert_video(video_path, video_id)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        process_video.delay(
            instance.id,
            instance.video_file.path,
        )

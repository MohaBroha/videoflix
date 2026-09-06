import shutil
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from videos.models import Video


@override_settings(MEDIA_ROOT="/tmp/videoflix_test_media")
class VideoCleanupTests(TestCase):
    def setUp(self):
        media_root = Path("/tmp/videoflix_test_media")
        if media_root.exists():
            shutil.rmtree(media_root)
        media_root.mkdir(parents=True, exist_ok=True)

        self.video = Video.objects.create(
            title="Alpha",
            description="Test video",
            category="Test",
            video_file=SimpleUploadedFile("alpha.mp4", b"video-bytes", content_type="video/mp4"),
            thumbnail=SimpleUploadedFile("alpha.jpg", b"thumb-bytes", content_type="image/jpeg"),
        )

        self.hls_dir = media_root / "hls" / str(self.video.pk)
        self.hls_dir.mkdir(parents=True, exist_ok=True)
        (self.hls_dir / "index.m3u8").write_bytes(b"#EXTM3U")

    def tearDown(self):
        media_root = Path("/tmp/videoflix_test_media")
        if media_root.exists():
            shutil.rmtree(media_root)

    def test_delete_removes_video_media_and_hls_directory(self):
        self.assertTrue(self.video.video_file.storage.exists(self.video.video_file.name))
        self.assertTrue(self.video.thumbnail.storage.exists(self.video.thumbnail.name))
        self.assertTrue((Path("/tmp/videoflix_test_media") / "hls" / str(self.video.pk)).exists())

        self.video.delete()

        self.assertFalse((Path("/tmp/videoflix_test_media") / "hls" / str(self.video.pk)).exists())
        self.assertFalse(self.video.video_file.storage.exists(self.video.video_file.name))
        self.assertFalse(self.video.thumbnail.storage.exists(self.video.thumbnail.name))

    def test_video_queryset_orders_by_title(self):
        Video.objects.create(
            title="Zulu",
            description="Later title",
            category="Test",
            video_file=SimpleUploadedFile("zulu.mp4", b"video-bytes", content_type="video/mp4"),
            thumbnail=SimpleUploadedFile("zulu.jpg", b"thumb-bytes", content_type="image/jpeg"),
        )
        Video.objects.create(
            title="Alpha",
            description="First title",
            category="Test",
            video_file=SimpleUploadedFile("alpha2.mp4", b"video-bytes", content_type="video/mp4"),
            thumbnail=SimpleUploadedFile("alpha2.jpg", b"thumb-bytes", content_type="image/jpeg"),
        )

        titles = list(Video.objects.order_by("title").values_list("title", flat=True))
        self.assertEqual(titles, ["Alpha", "Alpha", "Zulu"]) 

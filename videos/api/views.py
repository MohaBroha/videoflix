import os

from django.conf import settings
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from videos.models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)

        return Response(serializer.data)


class VideoManifestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        try:
            Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found."},
                status=404,
            )

        manifest_path = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(movie_id),
            resolution,
            "index.m3u8",
        )

        if not os.path.exists(manifest_path):
            return Response(
                {"detail": "Manifest not found."},
                status=404,
            )

        return FileResponse(
            open(manifest_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )

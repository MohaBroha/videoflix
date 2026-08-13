import os

from django.conf import settings
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from videos.models import Video
from .serializers import VideoSerializer


class VideoListView(APIView):
    """Return the list of videos for authenticated users."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch all videos and serialize them for the client."""

        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)

        return Response(serializer.data)


class VideoManifestView(APIView):
    """Serve the HLS manifest file for a specific video and resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Return the manifest for the requested movie and resolution."""

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


class VideoSegmentView(APIView):
    """Serve a single video segment from the HLS output directory."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Return the requested MPEG-TS segment for the video."""

        try:
            Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            return Response(
                {"detail": "Video not found."},
                status=404,
            )

        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(movie_id),
            resolution,
            segment,
        )

        if not os.path.exists(segment_path):
            return Response(
                {"detail": "Segment not found."},
                status=404,
            )

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T",
        )

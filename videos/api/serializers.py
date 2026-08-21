from rest_framework import serializers

from videos.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata and the generated thumbnail URL."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Configure the fields returned by the serializer."""

        model = Video
        fields = [
            "id",
            "created_at",
            "title",
            "description",
            "thumbnail_url",
            "category",
        ]

    def get_thumbnail_url(self, obj):
        """Return the absolute URL of the video's thumbnail."""

        request = self.context.get("request")

        if not obj.thumbnail:
            return None

        url = obj.thumbnail.url

        if request:
            return request.build_absolute_uri(url)

        return url

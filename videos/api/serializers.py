from rest_framework import serializers

from videos.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata and the generated thumbnail URL."""

    thumbnail_url = serializers.ImageField(
        source="thumbnail",
        read_only=True,
    )

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

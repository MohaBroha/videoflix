import os
import subprocess

from django.conf import settings


def convert_video(video_path, video_id):
    resolutions = {
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
    }

    for resolution, height in resolutions.items():
        output_dir = os.path.join(
            settings.MEDIA_ROOT,
            "hls",
            str(video_id),
            resolution,
        )
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "index.m3u8")

        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-vf",
                f"scale=-2:{height}",
                "-c:v",
                "libx264",
                "-f",
                "hls",
                "-hls_time",
                "6",
                "-hls_playlist_type",
                "vod",
                output_path,
            ],
            check=True,
        )

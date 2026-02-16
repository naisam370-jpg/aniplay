import subprocess
import os
from pathlib import Path


class ThumbnailManager:
    def __init__(self, cache_dir=".cache/thumbnails"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate_for_episode(self, video_path, file_hash):
        """Generates a thumbnail for a specific video file using its hash."""
        output_path = self.cache_dir / f"{file_hash}.jpg"

        # If thumbnail already exists, don't recreate it
        if output_path.exists():
            return str(output_path)

        # FFmpeg command:
        # -ss 00:00:20 (Seek to 20 seconds to avoid going past NCOP lengths of some files)
        # -i (input file)
        # -frames:v 1 (capture 1 frame)
        # -q:v 2 (high quality)
        cmd = [
            'ffmpeg', '-ss', '00:00:20', '-i', str(video_path),
            '-frames:v', '1', '-q:v', '2', str(output_path),
            '-y', '-loglevel', 'quiet'  # Overwrite and stay silent
        ]

        try:
            subprocess.run(cmd, check=True)
            return str(output_path)
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
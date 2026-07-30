"""Storage and file handling services."""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
from PIL import Image

STORAGE_BASE = Path("/Users/dilippottigari/Documents/aura/storage/uploads")
PROJECTS_BASE = Path("/Users/dilippottigari/Documents/aura/storage/projects")

# Create directories if they don't exist
STORAGE_BASE.mkdir(parents=True, exist_ok=True)
PROJECTS_BASE.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB


class StorageService:
    """File storage service."""

    @staticmethod
    async def save_video(project_id: str, file_content: bytes, filename: str) -> Tuple[str, int]:
        """Save video file and return storage path and size."""
        # Validate extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {file_ext}")

        # Validate size
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum of 5GB")

        # Create project storage directory
        project_dir = STORAGE_BASE / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = project_dir / filename
        async with aiofiles.open(str(file_path), "wb") as f:
            await f.write(file_content)

        return str(file_path), len(file_content)

    @staticmethod
    def get_video_metadata(video_path: str) -> dict:
        """Extract video metadata using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return {}

            import json
            data = json.loads(result.stdout)

            # Extract relevant metadata
            format_data = data.get("format", {})
            streams = data.get("streams", [])

            duration = None
            if "duration" in format_data:
                duration = int(float(format_data["duration"]))

            resolution = None
            codec = None
            fps = None

            for stream in streams:
                if stream.get("codec_type") == "video":
                    width = stream.get("width")
                    height = stream.get("height")
                    if width and height:
                        resolution = f"{width}x{height}"
                    codec = stream.get("codec_name")
                    fps = stream.get("r_frame_rate")
                    if fps:
                        try:
                            parts = fps.split("/")
                            fps = int(float(parts[0]) / float(parts[1]))
                        except Exception:
                            fps = None
                    break

            return {
                "duration": duration,
                "resolution": resolution,
                "codec": codec,
                "fps": fps,
            }
        except Exception:
            return {}

    @staticmethod
    async def generate_thumbnail(video_path: str, thumbnail_path: str) -> Optional[str]:
        """Generate video thumbnail."""
        try:
            # Create thumbnail directory
            thumb_dir = Path(thumbnail_path).parent
            thumb_dir.mkdir(parents=True, exist_ok=True)

            # Use ffmpeg to extract first frame
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", "00:00:01",
                "-vframes", "1",
                "-vf", "scale=320:-1",
                "-q:v", "2",
                "-y",
                thumbnail_path,
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0 and Path(thumbnail_path).exists():
                return thumbnail_path

            return None
        except Exception:
            return None

    @staticmethod
    async def delete_video(storage_path: str) -> bool:
        """Delete video file."""
        try:
            path = Path(storage_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    async def delete_thumbnail(thumbnail_path: str) -> bool:
        """Delete thumbnail file."""
        try:
            path = Path(thumbnail_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False

"""Frame and audio extraction from video files.

Stateless extraction services that produce provider-agnostic results.
Results are immediately mapped to Observation objects by callers.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class ExtractedFrame:
    """Frame extracted from video"""
    frame_number: int
    timestamp_seconds: float
    is_keyframe: bool
    image_data: Optional[bytes] = None  # PNG/JPEG encoded
    width: int = 0
    height: int = 0


@dataclass(frozen=True)
class ExtractedAudioSegment:
    """Audio segment extracted from video"""
    start_timestamp: float
    end_timestamp: float
    audio_data: bytes  # PCM or compressed audio
    sample_rate: int
    channels: int


class FrameExtractionService:
    """Extract frames from video file.

    Stateless service - takes video metadata, returns frames.
    Does NOT know about sessions, timelines, or observations.
    """

    async def extract_frames(
        self,
        file_path: str,
        extract_keyframes: bool = True,
        extract_interval_frames: bool = True,
        fps_interval: float = 1.0,  # Extract 1 frame per second
        metadata_fps: float = 30.0,  # Metadata FPS
        metadata_duration: float = 60.0,  # Video duration
    ) -> List[ExtractedFrame]:
        """Extract frames from video.

        Args:
            file_path: Path to video file
            extract_keyframes: Extract keyframes
            extract_interval_frames: Extract interval frames
            fps_interval: Frames per second to extract
            metadata_fps: FPS from video metadata
            metadata_duration: Duration from video metadata

        Returns:
            List of ExtractedFrame objects
        """
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Use FFmpeg to extract frames
        # 2. Decode to image data
        # 3. Return frame list with timestamps and keyframe flags
        #
        # For now: return realistic stub frames

        frames = []
        total_frames = int(metadata_fps * metadata_duration)
        interval = int(metadata_fps / fps_interval)

        for i in range(0, total_frames, interval):
            timestamp = i / metadata_fps
            frames.append(ExtractedFrame(
                frame_number=i,
                timestamp_seconds=timestamp,
                is_keyframe=(i % (interval * 2) == 0),
                image_data=None,  # Would contain PNG data
                width=1920,
                height=1080,
            ))

        return frames


class AudioExtractionService:
    """Extract audio from video file.

    Stateless service - takes video path, returns audio segments.
    """

    async def extract_audio(
        self,
        file_path: str,
        metadata_duration: float = 60.0,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> List[ExtractedAudioSegment]:
        """Extract audio from video.

        Args:
            file_path: Path to video file
            metadata_duration: Video duration
            sample_rate: Target sample rate
            channels: Target channels (1=mono, 2=stereo)

        Returns:
            List of ExtractedAudioSegment objects
        """
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Use FFmpeg to extract audio
        # 2. Decode to PCM or compressed format
        # 3. Return audio segments
        #
        # For now: return single stub segment

        return [
            ExtractedAudioSegment(
                start_timestamp=0.0,
                end_timestamp=metadata_duration,
                audio_data=b"",  # Would contain PCM data
                sample_rate=sample_rate,
                channels=channels,
            )
        ]

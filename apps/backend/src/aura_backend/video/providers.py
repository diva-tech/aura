"""Provider interfaces for video analysis.

All external libraries (FFmpeg, Whisper, Tesseract, OpenCV) are isolated
behind these interfaces. No third-party objects leak into the domain layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aura_backend.video.models import (
    AudioCodec,
    Observation,
    ObservationType,
    TranscriptSegment,
    Video,
    VideoCodec,
    VideoMetadata,
)


# ============================================================================
# PROVIDER INTERFACES (Abstract)
# ============================================================================


class VideoProvider(ABC):
    """Interface for video metadata extraction"""

    @abstractmethod
    async def extract_metadata(self, file_path: str) -> VideoMetadata:
        """Extract video metadata from file"""
        pass

    @abstractmethod
    async def is_supported(self, file_path: str) -> bool:
        """Check if provider can handle this file"""
        pass


class SpeechProvider(ABC):
    """Interface for speech transcription"""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> List[TranscriptSegment]:
        """Transcribe audio to text with timestamps"""
        pass

    @abstractmethod
    async def supports_language(self, language: str) -> bool:
        """Check if provider supports this language"""
        pass


class OCRProvider(ABC):
    """Interface for optical character recognition"""

    @abstractmethod
    async def detect_text(
        self,
        image_data: bytes,
    ) -> List[Dict[str, Any]]:
        """Detect text in image.

        Returns list of:
        {
            "text": str,
            "confidence": float,
            "bbox": {"x": int, "y": int, "w": int, "h": int},
        }
        """
        pass

    @abstractmethod
    async def supports_language(self, language: str) -> bool:
        """Check if provider supports this language"""
        pass


class VisionProvider(ABC):
    """Interface for object/face detection"""

    @abstractmethod
    async def detect_objects(
        self,
        image_data: bytes,
    ) -> List[Dict[str, Any]]:
        """Detect objects in image.

        Returns list of:
        {
            "class": str,
            "confidence": float,
            "bbox": {"x": int, "y": int, "w": int, "h": int},
        }
        """
        pass

    @abstractmethod
    async def detect_faces(
        self,
        image_data: bytes,
    ) -> List[Dict[str, Any]]:
        """Detect faces in image.

        Returns list of:
        {
            "confidence": float,
            "bbox": {"x": int, "y": int, "w": int, "h": int},
        }
        """
        pass


# ============================================================================
# REFERENCE IMPLEMENTATIONS (Minimal working implementations)
# ============================================================================


class FFmpegVideoProvider(VideoProvider):
    """Reference implementation using FFmpeg"""

    async def extract_metadata(self, file_path: str) -> VideoMetadata:
        """Extract metadata using FFprobe (FFmpeg tool)"""
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Call ffprobe to get video information
        # 2. Parse JSON output
        # 3. Convert to VideoMetadata
        # 4. Return immutable VideoMetadata object
        #
        # For now: return stub with realistic values
        import os
        from pathlib import Path

        file_size = os.path.getsize(file_path)

        # Stub implementation - in production would parse ffprobe output
        return VideoMetadata(
            duration_seconds=60.0,
            fps=30.0,
            width=1920,
            height=1080,
            video_codec=VideoCodec.H264,
            audio_codec=AudioCodec.AAC,
            bitrate_kbps=5000,
            frame_count=1800,
            audio_streams=1,
            subtitle_streams=0,
            file_format=Path(file_path).suffix.lstrip("."),
            file_size_bytes=file_size,
        )

    async def is_supported(self, file_path: str) -> bool:
        """Check if FFmpeg can handle this file"""
        supported = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
        from pathlib import Path

        return Path(file_path).suffix.lower() in supported


class WhisperSpeechProvider(SpeechProvider):
    """Reference implementation using Whisper"""

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> List[TranscriptSegment]:
        """Transcribe using Whisper model"""
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Load Whisper model
        # 2. Feed audio_data bytes to model
        # 3. Parse model output (text + timestamps)
        # 4. Convert each segment to immutable TranscriptSegment
        # 5. Return list of TranscriptSegment objects
        #
        # For now: return stub with realistic structure
        return [
            TranscriptSegment(
                video_id="",
                start_timestamp=0.0,
                end_timestamp=3.0,
                text="This is a sample transcript.",
                confidence=0.95,
                language=language,
            ),
        ]

    async def supports_language(self, language: str) -> bool:
        """Whisper supports 99+ languages"""
        return True


class TesseractOCRProvider(OCRProvider):
    """Reference implementation using Tesseract"""

    async def detect_text(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect text using Tesseract"""
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Load image_data bytes
        # 2. Call Tesseract OCR
        # 3. Parse results with bounding boxes and confidence
        # 4. Return as list of dicts (NOT Tesseract objects)
        #
        # For now: return stub with realistic structure
        return [
            {
                "text": "SAMPLE TEXT",
                "confidence": 0.92,
                "bbox": {"x": 100, "y": 50, "w": 200, "h": 60},
            },
        ]

    async def supports_language(self, language: str) -> bool:
        """Tesseract supports 100+ languages"""
        return True


class OpenCVVisionProvider(VisionProvider):
    """Reference implementation using OpenCV + YOLO"""

    async def detect_objects(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect objects using YOLO"""
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Load image_data bytes
        # 2. Run YOLO inference
        # 3. Parse results
        # 4. Return as list of dicts (NOT YOLO objects)
        #
        # For now: return stub with realistic structure
        return [
            {
                "class": "person",
                "confidence": 0.95,
                "bbox": {"x": 100, "y": 150, "w": 200, "h": 400},
            },
            {
                "class": "chair",
                "confidence": 0.87,
                "bbox": {"x": 350, "y": 400, "w": 150, "h": 200},
            },
        ]

    async def detect_faces(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect faces using cascade classifier or DNN"""
        # IMPLEMENTATION NOTE: In production, this would:
        # 1. Load image_data bytes
        # 2. Run face detection (cascade or DNN model)
        # 3. Parse results
        # 4. Return as list of dicts (NOT OpenCV objects)
        #
        # For now: return stub with realistic structure
        return [
            {
                "confidence": 0.99,
                "bbox": {"x": 150, "y": 200, "w": 100, "h": 120},
            },
        ]


# ============================================================================
# PROVIDER REGISTRY
# ============================================================================


class ProviderRegistry:
    """Registry for available providers"""

    def __init__(self):
        self._video_providers: Dict[str, VideoProvider] = {}
        self._speech_providers: Dict[str, SpeechProvider] = {}
        self._ocr_providers: Dict[str, OCRProvider] = {}
        self._vision_providers: Dict[str, VisionProvider] = {}

    def register_video_provider(self, name: str, provider: VideoProvider) -> None:
        """Register a video provider"""
        self._video_providers[name] = provider

    def register_speech_provider(self, name: str, provider: SpeechProvider) -> None:
        """Register a speech provider"""
        self._speech_providers[name] = provider

    def register_ocr_provider(self, name: str, provider: OCRProvider) -> None:
        """Register an OCR provider"""
        self._ocr_providers[name] = provider

    def register_vision_provider(self, name: str, provider: VisionProvider) -> None:
        """Register a vision provider"""
        self._vision_providers[name] = provider

    def get_video_provider(self, name: str) -> Optional[VideoProvider]:
        """Get a video provider by name"""
        return self._video_providers.get(name)

    def get_speech_provider(self, name: str) -> Optional[SpeechProvider]:
        """Get a speech provider by name"""
        return self._speech_providers.get(name)

    def get_ocr_provider(self, name: str) -> Optional[OCRProvider]:
        """Get an OCR provider by name"""
        return self._ocr_providers.get(name)

    def get_vision_provider(self, name: str) -> Optional[VisionProvider]:
        """Get a vision provider by name"""
        return self._vision_providers.get(name)

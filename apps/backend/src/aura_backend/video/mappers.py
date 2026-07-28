"""Mappers: Convert provider results to immutable Observation objects.

This is the critical boundary where third-party library results are
converted to the unified Observation model. No provider objects leak
outside these mappers.
"""

from typing import Any, Dict, List

from aura_backend.video.models import (
    Observation,
    ObservationType,
    TranscriptSegment,
)


class SpeechMapper:
    """Convert Whisper results to Observations"""

    @staticmethod
    def from_transcript_segments(
        video_id: str,
        segments: List[TranscriptSegment],
    ) -> List[Observation]:
        """Convert TranscriptSegment list to Observation list"""
        observations = []

        for segment in segments:
            obs = Observation(
                video_id=video_id,
                observation_type=ObservationType.SPEECH,
                source_agent="SpeechAgent",
                start_timestamp=segment.start_timestamp,
                end_timestamp=segment.end_timestamp,
                confidence=segment.confidence,
                payload={
                    "text": segment.text,
                    "speaker": segment.speaker,
                    "language": segment.language,
                },
                metadata={
                    "source_provider": "whisper",
                    "segment_id": segment.id,
                },
            )
            observations.append(obs)

        return observations


class OCRMapper:
    """Convert Tesseract results to Observations"""

    @staticmethod
    def from_detections(
        video_id: str,
        start_timestamp: float,
        end_timestamp: float,
        detections: List[Dict[str, Any]],
    ) -> List[Observation]:
        """Convert OCR detection list to Observation list"""
        observations = []

        for detection in detections:
            obs = Observation(
                video_id=video_id,
                observation_type=ObservationType.OCR,
                source_agent="OCRAgent",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                confidence=detection.get("confidence", 0.0),
                payload={
                    "text": detection.get("text", ""),
                    "bbox": detection.get("bbox", {}),
                },
                metadata={
                    "source_provider": "tesseract",
                },
            )
            observations.append(obs)

        return observations


class VisionMapper:
    """Convert OpenCV/YOLO results to Observations"""

    @staticmethod
    def from_object_detections(
        video_id: str,
        start_timestamp: float,
        end_timestamp: float,
        detections: List[Dict[str, Any]],
    ) -> List[Observation]:
        """Convert object detection list to Observation list"""
        observations = []

        for detection in detections:
            obs = Observation(
                video_id=video_id,
                observation_type=ObservationType.OBJECT,
                source_agent="ObjectAnalysisAgent",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                confidence=detection.get("confidence", 0.0),
                payload={
                    "class": detection.get("class", "unknown"),
                    "bbox": detection.get("bbox", {}),
                },
                metadata={
                    "source_provider": "yolo",
                },
            )
            observations.append(obs)

        return observations

    @staticmethod
    def from_face_detections(
        video_id: str,
        start_timestamp: float,
        end_timestamp: float,
        detections: List[Dict[str, Any]],
    ) -> List[Observation]:
        """Convert face detection list to Observation list"""
        observations = []

        for idx, detection in enumerate(detections):
            obs = Observation(
                video_id=video_id,
                observation_type=ObservationType.FACE,
                source_agent="FaceAnalysisAgent",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                confidence=detection.get("confidence", 0.0),
                payload={
                    "face_index": idx,
                    "bbox": detection.get("bbox", {}),
                },
                metadata={
                    "source_provider": "opencv_cascade",
                },
            )
            observations.append(obs)

        return observations

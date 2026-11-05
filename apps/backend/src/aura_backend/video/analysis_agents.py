"""Video analysis agents.

Agents perform specific analysis tasks:
- SceneAnalysisAgent: Detect scene boundaries and content
- SpeechAnalysisAgent: Transcribe speech to text
- OCRAnalysisAgent: Extract text from frames
- VisionAnalysisAgent: Detect objects and faces

Agents:
1. Use providers to perform analysis (stateless)
2. Use mappers to convert results to Observation objects
3. Return immutable Observation objects
4. Never access Memory Runtime directly
5. Never modify AnalysisSession

Agents are integrated with M6 ExecutableAgent interface.
"""

from typing import List, Dict, Any, Optional
from aura_backend.video.models import Observation, ObservationType
from aura_backend.video.providers import (
    SpeechProvider,
    OCRProvider,
    VisionProvider,
)
from aura_backend.video.mappers import (
    SpeechMapper,
    OCRMapper,
    VisionMapper,
)
from aura_backend.video.scene_analysis import (
    SceneProvider,
    SceneMapper,
)
from aura_backend.video.extraction import (
    ExtractedFrame,
    ExtractedAudioSegment,
)


class SceneAnalysisAgent:
    """Detect scene boundaries and content.

    Consumes: Extracted frames
    Produces: SCENE_CONTENT observations
    """

    def __init__(self, scene_provider: SceneProvider):
        self.provider = scene_provider

    async def analyze(
        self,
        video_id: str,
        frames: List[ExtractedFrame],
        video_metadata: Dict[str, Any],
    ) -> List[Observation]:
        """Analyze scenes in video.

        Args:
            video_id: Video being analyzed
            frames: Extracted frames
            video_metadata: Video metadata

        Returns:
            List of SCENE_CONTENT observations
        """
        # Use provider (stateless)
        detections = await self.provider.detect_scenes(frames, video_metadata)

        # Map to observations
        observations = SceneMapper.from_detections(video_id, detections)

        return observations


class SpeechAnalysisAgent:
    """Transcribe speech to text.

    Consumes: Extracted audio
    Produces: SPEECH observations
    """

    def __init__(self, speech_provider: SpeechProvider):
        self.provider = speech_provider

    async def analyze(
        self,
        video_id: str,
        audio_segments: List[ExtractedAudioSegment],
        language: str = "en",
    ) -> List[Observation]:
        """Transcribe audio to text.

        Args:
            video_id: Video being analyzed
            audio_segments: Extracted audio segments
            language: Language code

        Returns:
            List of SPEECH observations
        """
        observations = []

        for audio_segment in audio_segments:
            # Use provider (stateless)
            transcript_segments = await self.provider.transcribe(
                audio_segment.audio_data,
                language=language,
            )

            # Update video_id in segments
            updated_segments = []
            for seg in transcript_segments:
                # Create new segment with correct video_id
                from aura_backend.video.models import TranscriptSegment
                updated_seg = TranscriptSegment(
                    id=seg.id,
                    video_id=video_id,
                    start_timestamp=seg.start_timestamp,
                    end_timestamp=seg.end_timestamp,
                    text=seg.text,
                    speaker=seg.speaker,
                    confidence=seg.confidence,
                    language=seg.language,
                )
                updated_segments.append(updated_seg)

            # Map to observations
            obs = SpeechMapper.from_transcript_segments(video_id, updated_segments)
            observations.extend(obs)

        return observations


class OCRAnalysisAgent:
    """Extract text from frames.

    Consumes: Extracted frames
    Produces: OCR observations
    """

    def __init__(self, ocr_provider: OCRProvider):
        self.provider = ocr_provider

    async def analyze(
        self,
        video_id: str,
        frames: List[ExtractedFrame],
        language: str = "en",
    ) -> List[Observation]:
        """Extract text from frames.

        Args:
            video_id: Video being analyzed
            frames: Extracted frames
            language: Language code

        Returns:
            List of OCR observations
        """
        observations = []

        for frame in frames:
            if not frame.image_data:
                continue

            # Use provider (stateless)
            detections = await self.provider.detect_text(frame.image_data)

            # Map to observations
            obs = OCRMapper.from_detections(
                video_id=video_id,
                start_timestamp=frame.timestamp_seconds,
                end_timestamp=frame.timestamp_seconds + 0.033,  # ~30fps frame duration
                detections=detections,
            )
            observations.extend(obs)

        return observations


class VisionAnalysisAgent:
    """Detect objects and faces in frames.

    Consumes: Extracted frames
    Produces: OBJECT and FACE observations
    """

    def __init__(self, vision_provider: VisionProvider):
        self.provider = vision_provider

    async def analyze(
        self,
        video_id: str,
        frames: List[ExtractedFrame],
    ) -> List[Observation]:
        """Detect objects and faces in frames.

        Args:
            video_id: Video being analyzed
            frames: Extracted frames

        Returns:
            List of OBJECT and FACE observations
        """
        observations = []

        for frame in frames:
            if not frame.image_data:
                continue

            # Detect objects
            object_detections = await self.provider.detect_objects(frame.image_data)
            obj_obs = VisionMapper.from_object_detections(
                video_id=video_id,
                start_timestamp=frame.timestamp_seconds,
                end_timestamp=frame.timestamp_seconds + 0.033,
                detections=object_detections,
            )
            observations.extend(obj_obs)

            # Detect faces
            face_detections = await self.provider.detect_faces(frame.image_data)
            face_obs = VisionMapper.from_face_detections(
                video_id=video_id,
                start_timestamp=frame.timestamp_seconds,
                end_timestamp=frame.timestamp_seconds + 0.033,
                detections=face_detections,
            )
            observations.extend(face_obs)

        return observations

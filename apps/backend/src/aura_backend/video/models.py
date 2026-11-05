"""Immutable domain models for video intelligence.

All models are frozen (immutable) dataclasses.
All models are fully typed.
All discoveries become Observation objects.
Timeline is the canonical execution model.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class VideoCodec(str, Enum):
    """Video codec types"""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"
    UNKNOWN = "unknown"


class AudioCodec(str, Enum):
    """Audio codec types"""
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    VORBIS = "vorbis"
    UNKNOWN = "unknown"


class ObservationType(str, Enum):
    """Types of observations discovered in video"""
    SCENE_BOUNDARY = "scene_boundary"
    SCENE_CONTENT = "scene_content"
    SPEECH = "speech"
    SILENCE = "silence"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    OCR = "ocr"
    FACE = "face"
    OBJECT = "object"
    LOGO = "logo"
    TEXT = "text"
    ACTIVITY = "activity"


class TimelineEventType(str, Enum):
    """Types of timeline events"""
    VIDEO_IMPORTED = "video_imported"
    FRAMES_EXTRACTED = "frames_extracted"
    SCENE_DETECTED = "scene_detected"
    AUDIO_EXTRACTED = "audio_extracted"
    TRANSCRIPT_GENERATED = "transcript_generated"
    OCR_COMPLETED = "ocr_completed"
    FACE_DETECTED = "face_detected"
    OBJECT_DETECTED = "object_detected"
    OBSERVATION_CREATED = "observation_created"


@dataclass(frozen=True)
class VideoMetadata:
    """Immutable video metadata"""
    duration_seconds: float
    fps: float
    width: int
    height: int
    video_codec: VideoCodec
    audio_codec: AudioCodec
    bitrate_kbps: int
    frame_count: int
    audio_streams: int
    subtitle_streams: int
    file_format: str
    file_size_bytes: int
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration_seconds": self.duration_seconds,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "video_codec": self.video_codec.value,
            "audio_codec": self.audio_codec.value,
            "bitrate_kbps": self.bitrate_kbps,
            "frame_count": self.frame_count,
            "audio_streams": self.audio_streams,
            "subtitle_streams": self.subtitle_streams,
            "file_format": self.file_format,
            "file_size_bytes": self.file_size_bytes,
        }


@dataclass(frozen=True)
class Video:
    """Immutable video object"""
    id: str = field(default_factory=lambda: str(uuid4()))
    file_path: str = ""
    metadata: Optional[VideoMetadata] = None
    imported_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "imported_at": self.imported_at.isoformat(),
        }


@dataclass(frozen=True)
class Frame:
    """Immutable video frame"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    frame_number: int = 0
    timestamp_seconds: float = 0.0
    is_keyframe: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "frame_number": self.frame_number,
            "timestamp_seconds": self.timestamp_seconds,
            "is_keyframe": self.is_keyframe,
        }


@dataclass(frozen=True)
class Scene:
    """Immutable scene in video"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    start_frame: int = 0
    end_frame: int = 0
    description: str = ""
    confidence: float = 1.0

    @property
    def duration_seconds(self) -> float:
        return self.end_timestamp - self.start_timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "description": self.description,
            "confidence": self.confidence,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class AudioSegment:
    """Immutable audio segment"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    audio_type: str = ""  # "speech", "music", "silence", "sound_effect"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "audio_type": self.audio_type,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class TranscriptSegment:
    """Immutable transcript segment"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    text: str = ""
    speaker: Optional[str] = None
    confidence: float = 1.0
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "text": self.text,
            "speaker": self.speaker,
            "confidence": self.confidence,
            "language": self.language,
        }


@dataclass(frozen=True)
class Observation:
    """Immutable observation - universal model for all discoveries.

    Every discovery from every analysis agent becomes an Observation.
    This is the universal language of the video intelligence runtime.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    observation_type: ObservationType = ObservationType.SCENE_CONTENT
    source_agent: str = ""  # e.g., "SceneAnalysisAgent", "SpeechAgent"
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    confidence: float = 1.0
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def duration_seconds(self) -> float:
        return self.end_timestamp - self.start_timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "observation_type": self.observation_type.value,
            "source_agent": self.source_agent,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "confidence": self.confidence,
            "duration_seconds": self.duration_seconds,
            "payload": self.payload,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class TimelineEvent:
    """Immutable timeline event"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    event_type: TimelineEventType = TimelineEventType.VIDEO_IMPORTED
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""  # e.g., "VideoIngestionPipeline", "SpeechAgent"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
        }


@dataclass(frozen=True)
class Timeline:
    """Immutable timeline - canonical execution model.

    Everything discovered in the video becomes timeline events.
    Timeline is the source of truth for video analysis.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    events: List[TimelineEvent] = field(default_factory=list)
    observations: List[Observation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get_events_by_type(self, event_type: TimelineEventType) -> List[TimelineEvent]:
        """Get events of specific type"""
        return [e for e in self.events if e.event_type == event_type]

    def get_observations_by_type(self, obs_type: ObservationType) -> List[Observation]:
        """Get observations of specific type"""
        return [o for o in self.observations if o.observation_type == obs_type]

    def get_observations_in_range(
        self,
        start_timestamp: float,
        end_timestamp: float,
    ) -> List[Observation]:
        """Get observations within timestamp range"""
        return [
            o for o in self.observations
            if not (o.end_timestamp < start_timestamp or o.start_timestamp > end_timestamp)
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "event_count": len(self.events),
            "observation_count": len(self.observations),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class KnowledgeNode:
    """Immutable knowledge node - represents a fact or relationship"""
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    node_type: str = ""  # e.g., "person", "object", "location", "event"
    label: str = ""
    observations: List[str] = field(default_factory=list)  # Observation IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "node_type": self.node_type,
            "label": self.label,
            "observation_count": len(self.observations),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class AnalysisSession:
    """Immutable analysis session - groups one complete analysis run.

    Tracks:
    - Which video was analyzed
    - When analysis started/completed
    - Session status (pending, in_progress, completed, failed)
    - Timeline and observations produced
    - Metrics from the analysis
    - Knowledge graph created

    Only the ingestion pipeline persists sessions into Memory Runtime.
    Providers remain stateless and never directly access sessions.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    video_id: str = ""
    session_type: str = ""  # e.g., "initial", "refinement", "comparison"
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    # Analysis results
    timeline_id: Optional[str] = None  # Reference to Timeline
    observation_ids: List[str] = field(default_factory=list)
    knowledge_node_ids: List[str] = field(default_factory=list)
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    # Extensibility
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Duration from start to completion"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_active(self) -> bool:
        """Whether session is currently processing"""
        return self.status == "in_progress"

    @property
    def is_complete(self) -> bool:
        """Whether session finished successfully"""
        return self.status == "completed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "session_type": self.session_type,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeline_id": self.timeline_id,
            "observation_count": len(self.observation_ids),
            "knowledge_node_count": len(self.knowledge_node_ids),
            "duration_seconds": self.duration_seconds,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }

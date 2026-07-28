"""Immutable content intelligence domain models.

All models are frozen dataclasses representing semantic content discoveries.
Every model references Observations and AnalysisSession for traceability.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class StoryPhase(StrEnum):
    """Story narrative phases"""

    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    UNKNOWN = "unknown"


class HookType(StrEnum):
    """Types of story hooks"""

    QUESTION = "question"
    CONFLICT = "conflict"
    SURPRISE = "surprise"
    EMOTION = "emotion"
    STATEMENT = "statement"
    VISUAL = "visual"
    CURIOSITY = "curiosity"


class RecommendationType(StrEnum):
    """Types of content recommendations"""

    YOUTUBE_SHORT = "youtube_short"
    PODCAST_CLIP = "podcast_clip"
    INSTAGRAM_REEL = "instagram_reel"
    LINKEDIN_CLIP = "linkedin_clip"
    STRONG_CTA = "strong_cta"
    TRIM_SILENCE = "trim_silence"
    SPLIT_CHAPTER = "split_chapter"
    THUMBNAIL = "thumbnail"
    TITLE = "title"
    SUBTITLE = "subtitle"


@dataclass(frozen=True)
class StorySegment:
    """Immutable segment of a story"""

    id: str = field(default_factory=lambda: str(uuid4()))
    story_id: str = ""
    session_id: str = ""
    video_id: str = ""

    phase: StoryPhase = StoryPhase.UNKNOWN
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    description: str = ""
    summary: str = ""

    importance: float = 0.5  # 0-1 score
    confidence: float = 0.5  # 0-1 score

    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "story_id": self.story_id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "phase": self.phase.value,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "description": self.description,
            "summary": self.summary,
            "importance": self.importance,
            "confidence": self.confidence,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Story:
    """Immutable story object representing complete narrative"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    title: str = ""
    summary: str = ""

    # Narrative structure
    segments: list[StorySegment] = field(default_factory=list)

    # Metrics
    story_score: float = 0.5  # 0-1 overall quality
    average_confidence: float = 0.5
    coverage_percentage: float = 0.0  # % of video covered

    # Analysis metadata
    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "title": self.title,
            "summary": self.summary,
            "segment_count": len(self.segments),
            "story_score": self.story_score,
            "average_confidence": self.average_confidence,
            "coverage_percentage": self.coverage_percentage,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Highlight:
    """Immutable highlight (key moment in video)"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""
    story_id: str = ""

    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    title: str = ""
    description: str = ""
    reason: str = ""  # Why this is a highlight

    # Scoring
    importance: float = 0.5
    emotion: float = 0.5
    visual_quality: float = 0.5
    confidence: float = 0.5

    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "story_id": self.story_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "title": self.title,
            "description": self.description,
            "reason": self.reason,
            "importance": self.importance,
            "emotion": self.emotion,
            "visual_quality": self.visual_quality,
            "confidence": self.confidence,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Hook:
    """Immutable story hook (opening/attention-grabber)"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    hook_type: HookType = HookType.QUESTION
    title: str = ""
    description: str = ""

    hook_score: float = 0.5  # 0-1 effectiveness
    confidence: float = 0.5
    rank: int = 0  # Position in ranked list

    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "hook_type": self.hook_type.value,
            "title": self.title,
            "description": self.description,
            "hook_score": self.hook_score,
            "confidence": self.confidence,
            "rank": self.rank,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Chapter:
    """Immutable video chapter"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""
    story_id: str = ""

    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    title: str = ""
    summary: str = ""

    importance: float = 0.5
    topic_ids: list[str] = field(default_factory=list)
    observation_ids: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "story_id": self.story_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "title": self.title,
            "summary": self.summary,
            "importance": self.importance,
            "topic_count": len(self.topic_ids),
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Topic:
    """Immutable semantic topic"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    label: str = ""
    description: str = ""

    # Strength of topic in content
    strength: float = 0.5  # 0-1
    confidence: float = 0.5

    # Associated content
    observation_ids: list[str] = field(default_factory=list)
    chapter_ids: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "label": self.label,
            "description": self.description,
            "strength": self.strength,
            "confidence": self.confidence,
            "observation_count": len(self.observation_ids),
            "chapter_count": len(self.chapter_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Quote:
    """Immutable extracted quote"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    text: str = ""
    speaker: str | None = None
    quote_type: str = ""  # opinion, definition, statistic, cta, memorable

    relevance: float = 0.5
    confidence: float = 0.5

    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "text": self.text,
            "speaker": self.speaker,
            "quote_type": self.quote_type,
            "relevance": self.relevance,
            "confidence": self.confidence,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Recommendation:
    """Immutable content recommendation"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    rec_type: RecommendationType = RecommendationType.YOUTUBE_SHORT
    title: str = ""
    description: str = ""

    # Rationale
    reason: str = ""

    # Confidence in recommendation
    score: float = 0.5
    confidence: float = 0.5

    # What it applies to
    start_timestamp: float | None = None
    end_timestamp: float | None = None

    observation_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "rec_type": self.rec_type.value,
            "title": self.title,
            "description": self.description,
            "reason": self.reason,
            "score": self.score,
            "confidence": self.confidence,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class StoryGraph:
    """Immutable story graph connecting all intelligence components"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Core content
    story_id: str = ""
    chapter_ids: list[str] = field(default_factory=list)
    highlight_ids: list[str] = field(default_factory=list)
    hook_ids: list[str] = field(default_factory=list)
    topic_ids: list[str] = field(default_factory=list)
    quote_ids: list[str] = field(default_factory=list)
    recommendation_ids: list[str] = field(default_factory=list)

    # Relationships
    relationships: dict[str, list[str]] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "story_id": self.story_id,
            "chapter_count": len(self.chapter_ids),
            "highlight_count": len(self.highlight_ids),
            "hook_count": len(self.hook_ids),
            "topic_count": len(self.topic_ids),
            "quote_count": len(self.quote_ids),
            "recommendation_count": len(self.recommendation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ContentMetrics:
    """Immutable metrics from content intelligence pipeline"""

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Processing metrics
    processing_duration_seconds: float = 0.0

    # Content metrics
    story_score: float = 0.5
    average_confidence: float = 0.5
    coverage_percentage: float = 0.0

    # Component counts
    highlight_count: int = 0
    hook_count: int = 0
    chapter_count: int = 0
    topic_count: int = 0
    quote_count: int = 0
    recommendation_count: int = 0

    # Engagement
    engagement_score: float = 0.5  # 0-100

    # Quality indicators
    observation_count: int = 0
    observation_types_used: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "processing_duration_seconds": self.processing_duration_seconds,
            "story_score": self.story_score,
            "average_confidence": self.average_confidence,
            "coverage_percentage": self.coverage_percentage,
            "highlight_count": self.highlight_count,
            "hook_count": self.hook_count,
            "chapter_count": self.chapter_count,
            "topic_count": self.topic_count,
            "quote_count": self.quote_count,
            "recommendation_count": self.recommendation_count,
            "engagement_score": self.engagement_score,
            "observation_count": self.observation_count,
            "created_at": self.created_at.isoformat(),
        }

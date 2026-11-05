"""M14 Phase 1: Learning Foundation – Creator and Audience Profiles.

Immutable profiles representing learned creator behavior and audience preferences.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class VideoLengthPreference(StrEnum):
    """Video length preferences."""

    SHORT = "short"  # <1 min
    MEDIUM = "medium"  # 1-10 min
    LONG = "long"  # 10-30 min
    VERY_LONG = "very_long"  # >30 min
    VARIED = "varied"


class StyleCategory(StrEnum):
    """Style categories for learning."""

    FORMAL = "formal"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    MIXED = "mixed"


class EditingStyle(StrEnum):
    """Editing styles."""

    MINIMAL = "minimal"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CINEMATIC = "cinematic"
    ENERGETIC = "energetic"


@dataclass(frozen=True)
class CreatorPreference:
    """Creator preferences learned from past performance."""

    preference_type: str = ""
    values: tuple[str, ...] = None
    confidence: float = 0.0
    samples_count: int = 0
    last_updated: datetime = None

    def __post_init__(self):
        if self.values is None:
            object.__setattr__(self, "values", ())
        if not self.last_updated:
            object.__setattr__(self, "last_updated", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "preference_type": self.preference_type,
            "values": list(self.values) if self.values else [],
            "confidence": self.confidence,
            "samples_count": self.samples_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


@dataclass(frozen=True)
class CreatorProfile:
    """Long-term learned creator profile."""

    id: str = ""
    creator_id: str = ""
    learning_version: int = 1
    preferred_video_length: VideoLengthPreference = VideoLengthPreference.MEDIUM
    preferred_topics: tuple[str, ...] = None
    preferred_platforms: tuple[str, ...] = None
    preferred_languages: tuple[str, ...] = None
    thumbnail_style: str = ""
    title_style: StyleCategory = StyleCategory.CASUAL
    description_style: StyleCategory = StyleCategory.CASUAL
    hashtag_style: str = ""
    intro_style: str = ""
    outro_style: str = ""
    editing_style: EditingStyle = EditingStyle.MODERATE
    best_posting_times: tuple[str, ...] = None
    audience_segments: tuple[str, ...] = None
    optimization_preferences: tuple[str, ...] = None
    content_pillars: tuple[str, ...] = None
    tone_of_voice: str = ""
    avg_videos_per_week: float = 0.0
    last_learning_time: datetime = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.preferred_topics is None:
            object.__setattr__(self, "preferred_topics", ())
        if self.preferred_platforms is None:
            object.__setattr__(self, "preferred_platforms", ())
        if self.preferred_languages is None:
            object.__setattr__(self, "preferred_languages", ())
        if self.best_posting_times is None:
            object.__setattr__(self, "best_posting_times", ())
        if self.audience_segments is None:
            object.__setattr__(self, "audience_segments", ())
        if self.optimization_preferences is None:
            object.__setattr__(self, "optimization_preferences", ())
        if self.content_pillars is None:
            object.__setattr__(self, "content_pillars", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", datetime.utcnow())
        if not self.last_learning_time:
            object.__setattr__(self, "last_learning_time", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "learning_version": self.learning_version,
            "preferred_video_length": self.preferred_video_length.value,
            "preferred_topics": list(self.preferred_topics) if self.preferred_topics else [],
            "preferred_platforms": (
                list(self.preferred_platforms) if self.preferred_platforms else []
            ),
            "preferred_languages": (
                list(self.preferred_languages) if self.preferred_languages else []
            ),
            "thumbnail_style": self.thumbnail_style,
            "title_style": self.title_style.value,
            "description_style": self.description_style.value,
            "hashtag_style": self.hashtag_style,
            "intro_style": self.intro_style,
            "outro_style": self.outro_style,
            "editing_style": self.editing_style.value,
            "best_posting_times": list(self.best_posting_times) if self.best_posting_times else [],
            "audience_segments": list(self.audience_segments) if self.audience_segments else [],
            "optimization_preferences": (
                list(self.optimization_preferences) if self.optimization_preferences else []
            ),
            "content_pillars": list(self.content_pillars) if self.content_pillars else [],
            "tone_of_voice": self.tone_of_voice,
            "avg_videos_per_week": self.avg_videos_per_week,
            "last_learning_time": (
                self.last_learning_time.isoformat() if self.last_learning_time else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================================================
# AUDIENCE MODELS
# ============================================================================


@dataclass(frozen=True)
class AudienceSegment:
    """A specific segment of the audience."""

    id: str = ""
    segment_name: str = ""
    age_group: str = ""
    geography: tuple[str, ...] = None
    languages: tuple[str, ...] = None
    interests: tuple[str, ...] = None
    devices: tuple[str, ...] = None
    traffic_sources: tuple[str, ...] = None
    size_percent: float = 0.0
    growth_rate: float = 0.0
    engagement_score: float = 0.0
    retention_rate: float = 0.0
    conversion_rate: float = 0.0
    created_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.geography is None:
            object.__setattr__(self, "geography", ())
        if self.languages is None:
            object.__setattr__(self, "languages", ())
        if self.interests is None:
            object.__setattr__(self, "interests", ())
        if self.devices is None:
            object.__setattr__(self, "devices", ())
        if self.traffic_sources is None:
            object.__setattr__(self, "traffic_sources", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "segment_name": self.segment_name,
            "age_group": self.age_group,
            "geography": list(self.geography) if self.geography else [],
            "languages": list(self.languages) if self.languages else [],
            "interests": list(self.interests) if self.interests else [],
            "devices": list(self.devices) if self.devices else [],
            "traffic_sources": list(self.traffic_sources) if self.traffic_sources else [],
            "size_percent": self.size_percent,
            "growth_rate": self.growth_rate,
            "engagement_score": self.engagement_score,
            "retention_rate": self.retention_rate,
            "conversion_rate": self.conversion_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass(frozen=True)
class AudienceProfile:
    """Overall audience profile for a creator."""

    id: str = ""
    creator_id: str = ""
    total_subscribers: int = 0
    returning_viewer_rate: float = 0.0
    subscriber_ratio: float = 0.0
    avg_watch_time_minutes: float = 0.0
    engagement_rate: float = 0.0
    growth_rate: float = 0.0
    segments: tuple[AudienceSegment, ...] = None
    top_geographies: tuple[str, ...] = None
    top_interests: tuple[str, ...] = None
    top_devices: tuple[str, ...] = None
    top_traffic_sources: tuple[str, ...] = None
    gender_split: dict = None
    age_distribution: dict = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.segments is None:
            object.__setattr__(self, "segments", ())
        if self.top_geographies is None:
            object.__setattr__(self, "top_geographies", ())
        if self.top_interests is None:
            object.__setattr__(self, "top_interests", ())
        if self.top_devices is None:
            object.__setattr__(self, "top_devices", ())
        if self.top_traffic_sources is None:
            object.__setattr__(self, "top_traffic_sources", ())
        if self.gender_split is None:
            object.__setattr__(self, "gender_split", {})
        if self.age_distribution is None:
            object.__setattr__(self, "age_distribution", {})
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "total_subscribers": self.total_subscribers,
            "returning_viewer_rate": self.returning_viewer_rate,
            "subscriber_ratio": self.subscriber_ratio,
            "avg_watch_time_minutes": self.avg_watch_time_minutes,
            "engagement_rate": self.engagement_rate,
            "growth_rate": self.growth_rate,
            "segments": [s.to_dict() for s in self.segments] if self.segments else [],
            "top_geographies": list(self.top_geographies) if self.top_geographies else [],
            "top_interests": list(self.top_interests) if self.top_interests else [],
            "top_devices": list(self.top_devices) if self.top_devices else [],
            "top_traffic_sources": (
                list(self.top_traffic_sources) if self.top_traffic_sources else []
            ),
            "gender_split": self.gender_split or {},
            "age_distribution": self.age_distribution or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

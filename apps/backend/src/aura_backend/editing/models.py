"""M11: Intelligent Video Editing Engine - Domain Models.

Immutable editing plan domain models that transform semantic understanding
into executable editing blueprints. No video rendering - data only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class TransitionType(StrEnum):
    """Video transition types"""
    CUT = "cut"
    FADE = "fade"
    CROSS_DISSOLVE = "cross_dissolve"
    SLIDE = "slide"
    ZOOM_TRANSITION = "zoom_transition"
    WIPE = "wipe"
    DIP = "dip"


class SubtitleStyle(StrEnum):
    """Subtitle styling options"""
    BURNED = "burned"  # Hardcoded into video
    SRT = "srt"  # Separate subtitle file
    LIVE = "live"  # Real-time generation
    AUTO = "auto"  # Platform-specific


class OverlayType(StrEnum):
    """Overlay types"""
    STATISTIC = "statistic"
    LOWER_THIRD = "lower_third"
    SPEAKER_NAME = "speaker_name"
    CALLOUT = "callout"
    CTA = "cta"
    PROGRESS_BAR = "progress_bar"
    WATERMARK = "watermark"
    TIMER = "timer"


class ZoomActionType(StrEnum):
    """Zoom/pan action types"""
    PUNCH_IN = "punch_in"  # Zoom to face
    PUNCH_OUT = "punch_out"  # Zoom out
    FACE_TRACKING = "face_tracking"  # Follow face
    FOCUS_SHIFT = "focus_shift"  # Pan to focus
    KEN_BURNS = "ken_burns"  # Pan and zoom combination


class MusicMood(StrEnum):
    """Music mood/tempo"""
    ENERGETIC = "energetic"
    CALM = "calm"
    DRAMATIC = "dramatic"
    UPLIFTING = "uplifting"
    MYSTERIOUS = "mysterious"
    HUMOROUS = "humorous"
    TENSE = "tense"
    INSPIRATIONAL = "inspirational"


class ClipSource(StrEnum):
    """What each clip is sourced from"""
    HIGHLIGHT = "highlight"
    HOOK = "hook"
    QUOTE = "quote"
    TOPIC = "topic"
    CHAPTER = "chapter"
    B_ROLL = "b_roll"
    TRANSITION = "transition"


@dataclass(frozen=True)
class Clip:
    """Immutable video clip definition"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    duration: float = 0.0  # Computed: end - start

    # Content
    title: str = ""
    description: str = ""

    # Source tracking
    source_type: ClipSource = ClipSource.HIGHLIGHT
    source_id: str = ""  # ID of highlight, quote, etc.

    # Quality
    clip_score: float = 0.5  # 0-1 quality
    confidence: float = 0.5

    # Context
    narrative_purpose: str = ""  # Why this clip
    observation_ids: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration": self.duration,
            "title": self.title,
            "source_type": self.source_type.value,
            "clip_score": self.clip_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Cut:
    """Immutable cut definition"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Position in timeline
    clip_id: str = ""
    position_in_timeline: float = 0.0  # Time when cut occurs

    # What to trim
    trim_start: float = 0.0  # Remove from start
    trim_end: float = 0.0  # Remove from end

    cut_type: str = ""  # "hard_cut", "jump_cut", "montage", "reaction"

    # Quality
    cut_score: float = 0.5
    confidence: float = 0.5

    reasoning: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "clip_id": self.clip_id,
            "position_in_timeline": self.position_in_timeline,
            "trim_start": self.trim_start,
            "trim_end": self.trim_end,
            "cut_type": self.cut_type,
            "cut_score": self.cut_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Transition:
    """Immutable transition definition"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Position in timeline
    from_clip_id: str = ""
    to_clip_id: str = ""
    position_in_timeline: float = 0.0

    transition_type: TransitionType = TransitionType.CUT
    duration_seconds: float = 0.0  # Length of transition (0 for cut)

    # Quality
    transition_score: float = 0.5
    confidence: float = 0.5

    reasoning: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_clip_id": self.from_clip_id,
            "to_clip_id": self.to_clip_id,
            "transition_type": self.transition_type.value,
            "duration_seconds": self.duration_seconds,
            "transition_score": self.transition_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class SubtitleSegment:
    """Immutable subtitle segment"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Content
    text: str = ""
    speaker: Optional[str] = None

    # Styling
    style: SubtitleStyle = SubtitleStyle.AUTO
    highlighted_words: List[str] = field(default_factory=list)
    emoji_suggestions: List[str] = field(default_factory=list)

    # Quality
    confidence: float = 0.5
    readability_score: float = 0.5

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "text": self.text,
            "speaker": self.speaker,
            "style": self.style.value,
            "highlighted_words": len(self.highlighted_words),
            "emoji_suggestions": self.emoji_suggestions,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class Overlay:
    """Immutable overlay definition"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Content
    overlay_type: OverlayType = OverlayType.STATISTIC
    title: str = ""
    content: str = ""

    # Positioning
    position: str = "center"  # "top_left", "center", "bottom_right", etc.
    size: str = "medium"  # "small", "medium", "large"

    # Quality
    relevance_score: float = 0.5
    confidence: float = 0.5

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "overlay_type": self.overlay_type.value,
            "title": self.title,
            "position": self.position,
            "relevance_score": self.relevance_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ZoomAction:
    """Immutable zoom/pan action"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    duration: float = 0.0

    # Action
    zoom_type: ZoomActionType = ZoomActionType.PUNCH_IN
    target_x: Optional[float] = None  # x coordinate to zoom to
    target_y: Optional[float] = None  # y coordinate to zoom to

    # Intensity
    zoom_intensity: float = 0.5  # 0-1: subtle to extreme
    easing: str = "ease_in_out"  # Animation easing

    # Quality
    effectiveness_score: float = 0.5
    confidence: float = 0.5

    reasoning: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "zoom_type": self.zoom_type.value,
            "zoom_intensity": self.zoom_intensity,
            "effectiveness_score": self.effectiveness_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class BrollSuggestion:
    """Immutable B-roll suggestion"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Content
    description: str = ""
    search_keywords: List[str] = field(default_factory=list)

    # Media suggestions
    stock_footage_categories: List[str] = field(default_factory=list)
    image_suggestions: List[str] = field(default_factory=list)
    animation_suggestions: List[str] = field(default_factory=list)

    # Context
    purpose: str = ""  # Why this B-roll
    mood: str = ""

    # Quality
    relevance_score: float = 0.5
    confidence: float = 0.5

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "description": self.description,
            "keywords": self.search_keywords,
            "categories": self.stock_footage_categories,
            "relevance_score": self.relevance_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class MusicCue:
    """Immutable music cue"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0

    # Music spec
    mood: MusicMood = MusicMood.ENERGETIC
    intensity: float = 0.5  # 0-1: quiet to loud
    tempo_bpm: Optional[int] = None

    # Fade
    fade_in_seconds: float = 0.0
    fade_out_seconds: float = 0.0

    # Timing
    beat_emphasis: bool = False  # Sync to beat

    # Quality
    fit_score: float = 0.5
    confidence: float = 0.5

    reasoning: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "mood": self.mood.value,
            "intensity": self.intensity,
            "fade_in": self.fade_in_seconds,
            "fade_out": self.fade_out_seconds,
            "fit_score": self.fit_score,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class SilenceRemoval:
    """Immutable silence removal suggestion"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Timing
    start_timestamp: float = 0.0
    end_timestamp: float = 0.0
    duration: float = 0.0

    # Action
    action: str = "remove"  # "remove" or "shorten"
    shorten_to_seconds: Optional[float] = None

    # Quality
    confidence: float = 0.5

    reasoning: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration": self.duration,
            "action": self.action,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class EditTimeline:
    """Master editing timeline"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Content
    clip_ids: List[str] = field(default_factory=list)  # In order
    cut_ids: List[str] = field(default_factory=list)
    transition_ids: List[str] = field(default_factory=list)
    subtitle_ids: List[str] = field(default_factory=list)
    overlay_ids: List[str] = field(default_factory=list)
    zoom_ids: List[str] = field(default_factory=list)
    music_ids: List[str] = field(default_factory=list)
    broll_ids: List[str] = field(default_factory=list)
    silence_removal_ids: List[str] = field(default_factory=list)

    # Quality
    timeline_score: float = 0.5
    narrative_flow: float = 0.5
    visual_rhythm: float = 0.5
    average_confidence: float = 0.5

    # Metadata
    total_duration: float = 0.0
    clip_count: int = 0
    average_clip_length: float = 0.0

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "clip_count": self.clip_count,
            "total_duration": self.total_duration,
            "average_clip_length": self.average_clip_length,
            "timeline_score": self.timeline_score,
            "narrative_flow": self.narrative_flow,
            "visual_rhythm": self.visual_rhythm,
            "transition_count": len(self.transition_ids),
            "subtitle_count": len(self.subtitle_ids),
            "overlay_count": len(self.overlay_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class EditingRecommendation:
    """Overall editing recommendation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Recommendation
    title: str = ""
    description: str = ""

    # Context
    target_platform: str = ""  # YouTube, TikTok, etc.
    target_duration: float = 0.0

    # What to do
    recommended_clips: List[str] = field(default_factory=list)
    recommended_music: List[str] = field(default_factory=list)
    recommended_overlays: List[str] = field(default_factory=list)

    # Quality
    suitability_score: float = 0.5
    engagement_potential: float = 0.5
    confidence: float = 0.5

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "target_platform": self.target_platform,
            "target_duration": self.target_duration,
            "suitability_score": self.suitability_score,
            "engagement_potential": self.engagement_potential,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class EditingMetrics:
    """Immutable editing metrics"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Counts
    clip_count: int = 0
    cut_count: int = 0
    transition_count: int = 0
    subtitle_count: int = 0
    overlay_count: int = 0
    zoom_count: int = 0
    silence_removed_seconds: float = 0.0

    # Scores
    editing_quality: float = 0.5
    narrative_cohesion: float = 0.5
    visual_variety: float = 0.5
    pacing_score: float = 0.5
    estimated_viewer_retention: float = 0.5

    # Platform suitability
    youtube_suitability: float = 0.5
    tiktok_suitability: float = 0.5
    instagram_suitability: float = 0.5
    linkedin_suitability: float = 0.5

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "clip_count": self.clip_count,
            "cut_count": self.cut_count,
            "transition_count": self.transition_count,
            "subtitle_count": self.subtitle_count,
            "overlay_count": self.overlay_count,
            "editing_quality": self.editing_quality,
            "narrative_cohesion": self.narrative_cohesion,
            "visual_variety": self.visual_variety,
            "pacing_score": self.pacing_score,
            "estimated_viewer_retention": self.estimated_viewer_retention,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class EditGraph:
    """Complete edit graph connecting all elements"""
    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Components
    timeline_id: str = ""
    clip_ids: List[str] = field(default_factory=list)
    cut_ids: List[str] = field(default_factory=list)
    transition_ids: List[str] = field(default_factory=list)
    subtitle_ids: List[str] = field(default_factory=list)
    overlay_ids: List[str] = field(default_factory=list)
    zoom_ids: List[str] = field(default_factory=list)
    music_ids: List[str] = field(default_factory=list)
    broll_ids: List[str] = field(default_factory=list)
    silence_ids: List[str] = field(default_factory=list)

    # Relationships
    relationships: Dict[str, List[str]] = field(default_factory=dict)

    # Metrics
    metrics_id: str = ""

    observation_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "timeline_id": self.timeline_id,
            "component_count": (
                len(self.clip_ids)
                + len(self.transition_ids)
                + len(self.subtitle_ids)
                + len(self.overlay_ids)
            ),
            "created_at": self.created_at.isoformat(),
        }

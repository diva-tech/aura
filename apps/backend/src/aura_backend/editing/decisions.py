"""M11 Phase 2: Editing Decisions and Strategies.

Every editing suggestion is represented as an EditDecision before becoming timeline objects.
Strategies guide engine behavior based on content type and creator goals.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class DecisionType(StrEnum):
    """Types of editing decisions"""

    CLIP_SELECTION = "clip_selection"
    SEQUENCE = "sequence"
    CUT = "cut"
    TRANSITION = "transition"
    SUBTITLE = "subtitle"
    OVERLAY = "overlay"
    ZOOM = "zoom"
    BROLL = "broll"
    MUSIC = "music"
    SILENCE_REMOVAL = "silence_removal"
    TIMING = "timing"
    PACING = "pacing"


class EditStrategy(StrEnum):
    """Editing strategy types guiding engine decisions"""

    YOUTUBE_DOCUMENTARY = "youtube_documentary"  # Long-form, narrative
    FAST_SHORTS = "fast_shorts"  # TikTok/Shorts, quick cuts
    EDUCATIONAL = "educational"  # Clear, structured, overlays
    CORPORATE = "corporate"  # Professional, branded
    GAMING = "gaming"  # Fast pacing, reactions
    INTERVIEW = "interview"  # Focus on speaker, minimal cuts
    PODCAST = "podcast"  # Audio-first, waveforms, minimal video
    VLOG = "vlog"  # Personal, varied pacing
    MUSIC_VIDEO = "music_video"  # Beat-synchronized
    HIGHLIGHTS_REEL = "highlights_reel"  # Short, intense


@dataclass(frozen=True)
class EditDecision:
    """Immutable editing decision backing all editing suggestions.

    Every engine produces EditDecisions that become timeline objects.
    Decisions are immutable and trace back to content evidence.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Decision attributes
    decision_type: DecisionType = DecisionType.CLIP_SELECTION
    reason: str = ""  # Why this decision

    # Quality metrics
    confidence: float = 0.5  # 0-1 confidence in decision
    score: float = 0.5  # 0-1 decision quality

    # Timing
    affected_time_range: tuple[float, float] = (0.0, 0.0)  # (start, end)

    # Context
    platform: str = ""  # YouTube, TikTok, etc.
    strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY

    # Dependencies
    dependencies: list[str] = field(default_factory=list)  # IDs of decisions this depends on

    # Traceability
    content_evidence: dict[str, Any] = field(default_factory=dict)  # What evidence supports this
    scorecard: dict[str, float] = field(default_factory=dict)  # Scoring breakdown
    observation_ids: list[str] = field(default_factory=list)  # M9 observations

    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "decision_type": self.decision_type.value,
            "reason": self.reason,
            "confidence": self.confidence,
            "score": self.score,
            "affected_time_range": self.affected_time_range,
            "platform": self.platform,
            "strategy": self.strategy.value,
            "dependencies": len(self.dependencies),
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class StrategyConfig:
    """Configuration for an editing strategy.

    Guides engine parameters and decision-making.
    """

    strategy: EditStrategy
    target_platform: str
    target_duration_seconds: float
    max_clips: int
    min_clip_length_seconds: float
    max_clip_length_seconds: float
    prefer_hard_cuts: bool
    subtitle_enabled: bool
    music_required: bool
    broll_enabled: bool
    zoom_frequency: float  # 0-1: how often to suggest zoom
    overlay_frequency: float  # 0-1: how often to suggest overlays
    silence_tolerance_seconds: float  # How much silence is acceptable
    narrative_flow_weight: float  # 0-1: emphasis on narrative vs engagement
    viewer_retention_weight: float  # 0-1: emphasis on retention

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy.value,
            "target_platform": self.target_platform,
            "target_duration_seconds": self.target_duration_seconds,
            "max_clips": self.max_clips,
            "min_clip_length_seconds": self.min_clip_length_seconds,
            "max_clip_length_seconds": self.max_clip_length_seconds,
            "prefer_hard_cuts": self.prefer_hard_cuts,
            "subtitle_enabled": self.subtitle_enabled,
            "music_required": self.music_required,
        }

"""M11 Phase 3: Edit Plan and Graph Models.

Immutable models representing the complete editing plan and its semantic graph.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from .models import (
    Clip,
    Cut,
    EditGraph,
    EditTimeline,
    EditingMetrics,
    MusicCue,
    Overlay,
    SilenceRemoval,
    SubtitleSegment,
    Transition,
    ZoomAction,
    BrollSuggestion,
)
from .decisions import EditStrategy, EditDecision
from .orchestration import ReviewFinding, TimelineConstraint


@dataclass(frozen=True)
class EditPlan:
    """Immutable complete editing plan ready for Phase 4 rendering.

    Bundles all editing suggestions into a single unit of work.
    """

    plan_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # Core editing elements
    strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY
    constraint: Optional[TimelineConstraint] = None

    # All editing decisions (immutable, ordered)
    edit_decisions: List[EditDecision] = field(default_factory=list)

    # Timeline and structure
    clips: List[Clip] = field(default_factory=list)
    timeline: Optional[EditTimeline] = None
    cuts: List[Cut] = field(default_factory=list)
    transitions: List[Transition] = field(default_factory=list)

    # Content elements
    subtitles: List[SubtitleSegment] = field(default_factory=list)
    overlays: List[Overlay] = field(default_factory=list)
    zoom_actions: List[ZoomAction] = field(default_factory=list)

    # Media suggestions
    broll_suggestions: List[BrollSuggestion] = field(default_factory=list)
    music_suggestions: List[MusicCue] = field(default_factory=list)
    silence_removals: List[SilenceRemoval] = field(default_factory=list)

    # Semantic graph linking all elements
    edit_graph: Optional[EditGraph] = None

    # Quality metrics
    metrics: Optional[EditingMetrics] = None

    # Quality review findings
    review_findings: List[ReviewFinding] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    observation_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "strategy": self.strategy.value,
            "clip_count": len(self.clips),
            "transition_count": len(self.transitions),
            "subtitle_count": len(self.subtitles),
            "overlay_count": len(self.overlays),
            "zoom_count": len(self.zoom_actions),
            "broll_count": len(self.broll_suggestions),
            "music_count": len(self.music_suggestions),
            "silence_removal_count": len(self.silence_removals),
            "review_findings_count": len(self.review_findings),
            "created_at": self.created_at.isoformat(),
        }

    @property
    def total_duration_seconds(self) -> float:
        """Total duration of edited video in seconds."""
        if not self.clips:
            return 0.0
        return sum(c.duration_seconds for c in self.clips)

    @property
    def is_valid(self) -> bool:
        """Check if plan is valid (has minimum required components)."""
        return len(self.clips) > 0 and self.timeline is not None

    @property
    def quality_score(self) -> float:
        """Overall quality score based on metrics."""
        if not self.metrics:
            return 0.5
        return self.metrics.overall_quality_score


@dataclass(frozen=True)
class EditPlanBuilder:
    """Builder for constructing EditPlan from individual components.

    Ensures proper ordering and validation of all editing elements.
    """

    plan_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""
    strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY
    constraint: Optional[TimelineConstraint] = None

    def add_clips(self, clips: List[Clip]) -> "EditPlanBuilder":
        """Add clips to the plan."""
        return EditPlanBuilder(
            plan_id=self.plan_id,
            session_id=self.session_id,
            video_id=self.video_id,
            strategy=self.strategy,
            constraint=self.constraint,
        )

    def build(
        self,
        clips: List[Clip] = None,
        timeline: Optional[EditTimeline] = None,
        transitions: List[Transition] = None,
        subtitles: List[SubtitleSegment] = None,
        overlays: List[Overlay] = None,
        zoom_actions: List[ZoomAction] = None,
        broll_suggestions: List[BrollSuggestion] = None,
        music_suggestions: List[MusicCue] = None,
        silence_removals: List[SilenceRemoval] = None,
        edit_graph: Optional[EditGraph] = None,
        metrics: Optional[EditingMetrics] = None,
        review_findings: List[ReviewFinding] = None,
        edit_decisions: List[EditDecision] = None,
        observation_ids: List[str] = None,
    ) -> EditPlan:
        """Build the final EditPlan from all components."""
        return EditPlan(
            plan_id=self.plan_id,
            session_id=self.session_id,
            video_id=self.video_id,
            strategy=self.strategy,
            constraint=self.constraint,
            clips=clips or [],
            timeline=timeline,
            transitions=transitions or [],
            subtitles=subtitles or [],
            overlays=overlays or [],
            zoom_actions=zoom_actions or [],
            broll_suggestions=broll_suggestions or [],
            music_suggestions=music_suggestions or [],
            silence_removals=silence_removals or [],
            edit_graph=edit_graph,
            metrics=metrics,
            review_findings=review_findings or [],
            edit_decisions=edit_decisions or [],
            observation_ids=observation_ids or [],
        )

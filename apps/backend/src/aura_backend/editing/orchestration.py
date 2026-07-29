"""M11 Phase 3: Editing Orchestration and Planning.

EditingPlanner converts M10 semantic artifacts into M8 Task Graphs.
Event models for editing lifecycle.
Constraint and review models for quality tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from aura_backend.orchestration.models import Capability, ExecutionStatus, Skill, Task, ToolRequirement
from aura_backend.content import Story, Highlight, Hook, Quote, Topic, Recommendation

from .decisions import EditStrategy, StrategyConfig, DecisionType
from .models import EditingMetrics


# ============================================================================
# CONSTRAINT MODELS
# ============================================================================


@dataclass(frozen=True)
class TimelineConstraint:
    """Constraints for editing based on platform and format."""

    platform: str  # youtube, tiktok, instagram, linkedin
    target_duration_seconds: float
    min_clips: int
    max_clips: int
    min_clip_length_seconds: float
    max_clip_length_seconds: float
    transition_type_preferences: List[str] = field(default_factory=list)
    require_subtitles: bool = False
    require_music: bool = False
    require_overlays: bool = False
    zoom_frequency_target: float = 0.0  # 0-1
    silence_tolerance_seconds: float = 0.5
    aspect_ratio: str = "16:9"
    color_grading_required: bool = False
    captions_requirement: str = "optional"  # optional, required, auto

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "target_duration_seconds": self.target_duration_seconds,
            "min_clips": self.min_clips,
            "max_clips": self.max_clips,
            "require_subtitles": self.require_subtitles,
            "require_music": self.require_music,
            "silence_tolerance_seconds": self.silence_tolerance_seconds,
        }


@dataclass(frozen=True)
class ReviewFinding:
    """Structured quality review finding."""

    finding_id: str = field(default_factory=lambda: str(uuid4()))
    category: str = ""  # narrative_flow, pacing, visual_variety, engagement, etc.
    severity: str = ""  # info, warning, error
    message: str = ""
    affected_components: List[str] = field(default_factory=list)
    suggested_fix: str = ""
    confidence_score: float = 0.7
    observation_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "affected_components": len(self.affected_components),
            "suggested_fix": self.suggested_fix,
            "confidence_score": self.confidence_score,
        }


# ============================================================================
# EDITING EVENTS
# ============================================================================


@dataclass(frozen=True)
class EditingEvent:
    """Base class for editing lifecycle events."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    session_id: str = ""
    video_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class EditPlanCreated(EditingEvent):
    """Event fired when editing plan is created."""

    event_type: str = "edit_plan_created"
    clip_count: int = 0
    strategy: str = ""
    constraint_set: str = ""


@dataclass(frozen=True)
class TimelineBuilt(EditingEvent):
    """Event fired when timeline is sequenced."""

    event_type: str = "timeline_built"
    clip_count: int = 0
    total_duration_seconds: float = 0.0
    narrative_flow_score: float = 0.0
    visual_rhythm_score: float = 0.0


@dataclass(frozen=True)
class SubtitleGenerated(EditingEvent):
    """Event fired when subtitle timeline is created."""

    event_type: str = "subtitle_generated"
    subtitle_count: int = 0
    coverage_percentage: float = 0.0


@dataclass(frozen=True)
class OverlayGenerated(EditingEvent):
    """Event fired when overlays are planned."""

    event_type: str = "overlay_generated"
    overlay_count: int = 0
    overlay_types: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TransitionPlanned(EditingEvent):
    """Event fired when transitions are suggested."""

    event_type: str = "transition_planned"
    transition_count: int = 0
    transition_types: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EditingCompleted(EditingEvent):
    """Event fired when editing plan is finalized."""

    event_type: str = "editing_completed"
    quality_score: float = 0.0
    platform_suitability_scores: Dict[str, float] = field(default_factory=dict)
    review_findings_count: int = 0


# ============================================================================
# EDITING PLANNER
# ============================================================================


class EditingPlanner:
    """Converts M10 semantic artifacts into M8 Task Graphs.

    Takes Story, Highlights, Recommendations and produces a task graph
    that can be executed through M8 orchestration.
    """

    def __init__(self, strategy: EditStrategy = EditStrategy.YOUTUBE_DOCUMENTARY):
        self.strategy = strategy
        self.constraint = self._create_constraint_for_strategy(strategy)

    def create_task_graph(
        self,
        session_id: str,
        video_id: str,
        story: Optional[Story] = None,
        highlights: Optional[List[Highlight]] = None,
        hooks: Optional[List[Hook]] = None,
        quotes: Optional[List[Quote]] = None,
        topics: Optional[List[Topic]] = None,
        recommendations: Optional[List[Recommendation]] = None,
    ) -> List[Task]:
        """Convert M10 artifacts into M8 task graph.

        Returns tasks ordered for execution (with dependencies).
        """
        tasks = []
        highlights = highlights or []

        # Task 1: Extract clips (parallel)
        if highlights:
            clip_task = Task(
                goal="Extract clips from highlights",
                description=f"Create {len(highlights)} clips with platform scoring",
                priority=100,
                required_capabilities={Capability.ANALYSIS, Capability.DATA_PROCESSING},
                metadata={
                    "engine_type": "clip",
                    "session_id": session_id,
                    "video_id": video_id,
                    "inputs": {
                        "highlights": highlights,
                        "story": story,
                        "strategy": self.strategy,
                    },
                },
            )
            tasks.append(clip_task)

        # Task 2: Build timeline (depends on clips)
        timeline_task = Task(
            goal="Sequence clips into timeline",
            description="Order clips and calculate narrative flow metrics",
            priority=90,
            required_capabilities={Capability.ANALYSIS},
            metadata={
                "engine_type": "timeline",
                "session_id": session_id,
                "video_id": video_id,
                "depends_on": ["clips"],
                "inputs": {
                    "highlights": highlights,
                    "story": story,
                },
            },
        )
        tasks.append(timeline_task)

        # Task 3: Suggest cuts (parallel with transitions)
        if highlights:
            cut_task = Task(
                goal="Suggest cuts and trims",
                description="Identify cut points for engagement",
                priority=80,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "cut",
                    "session_id": session_id,
                    "video_id": video_id,
                    "depends_on": ["clips"],
                    "inputs": {
                        "highlights": highlights,
                        "story": story,
                    },
                },
            )
            tasks.append(cut_task)

        # Task 4: Plan transitions
        transition_task = Task(
            goal="Plan transitions between clips",
            description="Choose transition types and timing",
            priority=80,
            required_capabilities={Capability.ANALYSIS},
            metadata={
                "engine_type": "transition",
                "session_id": session_id,
                "video_id": video_id,
                "depends_on": ["timeline"],
                "inputs": {
                    "highlights": highlights,
                    "story": story,
                },
            },
        )
        tasks.append(transition_task)

        # Task 5: Create subtitles (parallel if quotes available)
        if quotes:
            subtitle_task = Task(
                goal="Create subtitle timeline",
                description=f"Plan subtitles for {len(quotes)} segments",
                priority=70,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "subtitle",
                    "session_id": session_id,
                    "video_id": video_id,
                    "inputs": {
                        "quotes": quotes,
                        "story": story,
                    },
                },
            )
            tasks.append(subtitle_task)

        # Task 6: Plan overlays (parallel if topics available)
        if topics:
            overlay_task = Task(
                goal="Plan overlays",
                description=f"Suggest overlays for {len(topics)} topics",
                priority=70,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "overlay",
                    "session_id": session_id,
                    "video_id": video_id,
                    "inputs": {
                        "topics": topics,
                        "highlights": highlights,
                        "recommendations": recommendations,
                    },
                },
            )
            tasks.append(overlay_task)

        # Task 7: Suggest zoom actions (parallel)
        if highlights:
            zoom_task = Task(
                goal="Plan zoom and pan actions",
                description="Suggest camera movements for engagement",
                priority=70,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "zoom",
                    "session_id": session_id,
                    "video_id": video_id,
                    "depends_on": ["clips"],
                    "inputs": {
                        "highlights": highlights,
                        "recommendations": recommendations,
                    },
                },
            )
            tasks.append(zoom_task)

        # Task 8: Plan B-roll (parallel if topics available)
        if topics:
            broll_task = Task(
                goal="Suggest B-roll",
                description="Generate search keywords for B-roll",
                priority=65,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "broll",
                    "session_id": session_id,
                    "video_id": video_id,
                    "inputs": {
                        "topics": topics,
                        "story": story,
                    },
                },
            )
            tasks.append(broll_task)

        # Task 9: Suggest music
        if highlights:
            music_task = Task(
                goal="Suggest music",
                description="Recommend mood, tempo, and intensity",
                priority=65,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "music",
                    "session_id": session_id,
                    "video_id": video_id,
                    "depends_on": ["timeline"],
                    "inputs": {
                        "highlights": highlights,
                        "story": story,
                    },
                },
            )
            tasks.append(music_task)

        # Task 10: Detect silence
        if highlights:
            silence_task = Task(
                goal="Detect and remove silence",
                description="Identify dead air and suggest removal",
                priority=60,
                required_capabilities={Capability.ANALYSIS},
                metadata={
                    "engine_type": "silence",
                    "session_id": session_id,
                    "video_id": video_id,
                    "depends_on": ["clips"],
                    "inputs": {
                        "highlights": highlights,
                        "story": story,
                    },
                },
            )
            tasks.append(silence_task)

        # Task 11: Review (depends on all)
        review_task = Task(
            goal="Review editing plan",
            description="Validate all editing suggestions",
            priority=50,
            required_capabilities={Capability.ANALYSIS},
            metadata={
                "engine_type": "review",
                "session_id": session_id,
                "video_id": video_id,
                "depends_on": ["all"],
                "inputs": {},
            },
        )
        tasks.append(review_task)

        return tasks

    def _create_constraint_for_strategy(self, strategy: EditStrategy) -> TimelineConstraint:
        """Create platform constraints based on strategy."""
        constraint_map = {
            EditStrategy.YOUTUBE_DOCUMENTARY: TimelineConstraint(
                platform="youtube",
                target_duration_seconds=600.0,  # 10 minutes
                min_clips=10,
                max_clips=100,
                min_clip_length_seconds=5.0,
                max_clip_length_seconds=60.0,
                require_subtitles=False,
                require_music=True,
                zoom_frequency_target=0.3,
            ),
            EditStrategy.FAST_SHORTS: TimelineConstraint(
                platform="tiktok",
                target_duration_seconds=30.0,
                min_clips=5,
                max_clips=20,
                min_clip_length_seconds=1.0,
                max_clip_length_seconds=10.0,
                require_subtitles=True,
                require_music=True,
                zoom_frequency_target=0.7,
            ),
            EditStrategy.EDUCATIONAL: TimelineConstraint(
                platform="youtube",
                target_duration_seconds=300.0,  # 5 minutes
                min_clips=8,
                max_clips=50,
                min_clip_length_seconds=3.0,
                max_clip_length_seconds=30.0,
                require_subtitles=True,
                require_music=True,
                require_overlays=True,
                zoom_frequency_target=0.4,
            ),
            EditStrategy.INTERVIEW: TimelineConstraint(
                platform="youtube",
                target_duration_seconds=1200.0,  # 20 minutes
                min_clips=2,
                max_clips=10,
                min_clip_length_seconds=30.0,
                max_clip_length_seconds=600.0,
                require_subtitles=True,
                require_music=False,
                zoom_frequency_target=0.1,
            ),
        }
        return constraint_map.get(
            strategy,
            TimelineConstraint(
                platform="universal",
                target_duration_seconds=300.0,
                min_clips=5,
                max_clips=50,
                min_clip_length_seconds=2.0,
                max_clip_length_seconds=60.0,
            ),
        )

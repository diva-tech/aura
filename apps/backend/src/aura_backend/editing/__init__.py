"""Milestone 11: Intelligent Video Editing Engine.

Phase 1: Domain models for editing (clips, transitions, subtitles, etc.)
Phase 2: Deterministic editing intelligence engines
Phase 3: M6 agents, M8 task orchestration, event publishing, edit plans
Phase 4: Metrics, dashboard, visualization (coming)
"""

# Agents (Phase 3)
from .agents import (
    BrollAgent,
    ClipAgent,
    CutAgent,
    EditingAgentBase,
    MusicAgent,
    OverlayAgent,
    ReviewAgent,
    SilenceAgent,
    SubtitleAgent,
    TimelineAgent,
    TransitionAgent,
    ZoomAgent,
    create_editing_agent_registry,
    register_editing_agents,
)

# Orchestration and Planning (Phase 3)
from .orchestration import (
    EditPlanCreated,
    EditingCompleted,
    EditingEvent,
    EditingPlanner,
    OverlayGenerated,
    ReviewFinding,
    SubtitleGenerated,
    TimelineBuilt,
    TimelineConstraint,
    TransitionPlanned,
)

# Edit Plan (Phase 3)
from .plan import (
    EditPlan,
    EditPlanBuilder,
)

# Decisions and Strategies (Phase 2)
from .decisions import (
    DecisionType,
    EditDecision,
    EditStrategy,
    StrategyConfig,
)

# Editing Engines (Phase 2)
from .engines import (
    BrollEngine,
    ClipEngine,
    CutEngine,
    EditingEngine,
    EditingEngineRegistry,
    MusicEngine,
    OverlayEngine,
    SilenceEngine,
    SubtitleEngine,
    TimelineEngine,
    TransitionEngine,
    ZoomEngine,
    create_default_editing_registry,
)

# Domain Models (Phase 1)
from .models import (
    BrollSuggestion,
    Clip,
    ClipSource,
    Cut,
    EditGraph,
    EditingMetrics,
    EditingRecommendation,
    EditTimeline,
    MusicCue,
    MusicMood,
    Overlay,
    OverlayType,
    SilenceRemoval,
    SubtitleSegment,
    SubtitleStyle,
    Transition,
    TransitionType,
    ZoomAction,
    ZoomActionType,
)

__all__ = [
    # Agents (Phase 3)
    "BrollAgent",
    "ClipAgent",
    "CutAgent",
    "EditingAgentBase",
    "MusicAgent",
    "OverlayAgent",
    "ReviewAgent",
    "SilenceAgent",
    "SubtitleAgent",
    "TimelineAgent",
    "TransitionAgent",
    "ZoomAgent",
    "create_editing_agent_registry",
    "register_editing_agents",
    # Orchestration (Phase 3)
    "EditPlanCreated",
    "EditingCompleted",
    "EditingEvent",
    "EditingPlanner",
    "OverlayGenerated",
    "ReviewFinding",
    "SubtitleGenerated",
    "TimelineBuilt",
    "TimelineConstraint",
    "TransitionPlanned",
    # Edit Plan (Phase 3)
    "EditPlan",
    "EditPlanBuilder",
    # Decisions
    "DecisionType",
    "EditDecision",
    "EditStrategy",
    "StrategyConfig",
    # Engines
    "ClipEngine",
    "CutEngine",
    "EditingEngine",
    "EditingEngineRegistry",
    "MusicEngine",
    "OverlayEngine",
    "SilenceEngine",
    "SubtitleEngine",
    "TimelineEngine",
    "TransitionEngine",
    "ZoomEngine",
    "BrollEngine",
    "create_default_editing_registry",
    # Models
    "Clip",
    "ClipSource",
    "Cut",
    "EditGraph",
    "EditTimeline",
    "EditingMetrics",
    "EditingRecommendation",
    "MusicCue",
    "MusicMood",
    "Overlay",
    "OverlayType",
    "SilenceRemoval",
    "SubtitleSegment",
    "SubtitleStyle",
    "Transition",
    "TransitionType",
    "ZoomAction",
    "ZoomActionType",
    "BrollSuggestion",
]

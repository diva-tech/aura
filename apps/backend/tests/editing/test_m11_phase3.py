"""M11 Phase 3 Tests: Editing Orchestration and Planning.

Tests for:
1. M6 agent wrappers for all editing engines
2. EditingPlanner and task graph creation
3. Domain models (TimelineConstraint, ReviewFinding, etc.)
4. Event models for editing lifecycle
5. EditPlan and EditPlanBuilder
6. End-to-end orchestration
"""

import pytest

from aura_backend.editing import (
    # Agents (Phase 3)
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
    # Orchestration (Phase 3)
    EditPlanCreated,
    EditingCompleted,
    EditingPlanner,
    OverlayGenerated,
    ReviewFinding,
    SubtitleGenerated,
    TimelineBuilt,
    TimelineConstraint,
    TransitionPlanned,
    # Edit Plan (Phase 3)
    EditPlan,
    EditPlanBuilder,
    # Phase 2 models
    Clip,
    EditTimeline,
)

from aura_backend.content import Story, Highlight, Quote, Topic


# ============================================================================
# CONSTRAINT MODEL TESTS
# ============================================================================


class TestTimelineConstraint:
    """Test timeline constraint domain model"""

    def test_constraint_creation(self):
        """TimelineConstraint can be created"""
        constraint = TimelineConstraint(
            platform="youtube",
            target_duration_seconds=600.0,
            min_clips=10,
            max_clips=100,
            min_clip_length_seconds=5.0,
            max_clip_length_seconds=60.0,
        )

        assert constraint.platform == "youtube"
        assert constraint.target_duration_seconds == 600.0

    def test_constraint_immutable(self):
        """TimelineConstraint is immutable"""
        constraint = TimelineConstraint()

        with pytest.raises(AttributeError):
            constraint.platform = "tiktok"

    def test_constraint_to_dict(self):
        """TimelineConstraint can serialize to dict"""
        constraint = TimelineConstraint(
            platform="youtube",
            target_duration_seconds=600.0,
            min_clips=10,
            max_clips=100,
        )

        d = constraint.to_dict()
        assert d["platform"] == "youtube"
        assert d["target_duration_seconds"] == 600.0


# ============================================================================
# REVIEW FINDING MODEL TESTS
# ============================================================================


class TestReviewFinding:
    """Test quality review finding domain model"""

    def test_finding_creation(self):
        """ReviewFinding can be created"""
        finding = ReviewFinding(
            category="narrative_flow",
            severity="warning",
            message="Narrative flow could be improved",
            confidence_score=0.85,
        )

        assert finding.category == "narrative_flow"
        assert finding.severity == "warning"

    def test_finding_immutable(self):
        """ReviewFinding is immutable"""
        finding = ReviewFinding()

        with pytest.raises(AttributeError):
            finding.severity = "error"

    def test_finding_to_dict(self):
        """ReviewFinding can serialize to dict"""
        finding = ReviewFinding(
            category="pacing",
            severity="info",
            message="Pacing is consistent",
            confidence_score=0.9,
        )

        d = finding.to_dict()
        assert d["category"] == "pacing"
        assert d["confidence_score"] == 0.9


# ============================================================================
# EVENT MODEL TESTS
# ============================================================================


class TestEditingEvents:
    """Test editing lifecycle events"""

    def test_edit_plan_created_event(self):
        """EditPlanCreated event can be created"""
        event = EditPlanCreated(
            session_id="sess-1",
            video_id="v1",
            clip_count=15,
            strategy="youtube_documentary",
        )

        assert event.event_type == "edit_plan_created"
        assert event.clip_count == 15

    def test_timeline_built_event(self):
        """TimelineBuilt event can be created"""
        event = TimelineBuilt(
            session_id="sess-1",
            video_id="v1",
            clip_count=15,
            total_duration_seconds=600.0,
            narrative_flow_score=0.85,
            visual_rhythm_score=0.8,
        )

        assert event.event_type == "timeline_built"
        assert event.total_duration_seconds == 600.0

    def test_subtitle_generated_event(self):
        """SubtitleGenerated event can be created"""
        event = SubtitleGenerated(
            session_id="sess-1",
            video_id="v1",
            subtitle_count=50,
            coverage_percentage=95.0,
        )

        assert event.event_type == "subtitle_generated"
        assert event.subtitle_count == 50

    def test_editing_completed_event(self):
        """EditingCompleted event can be created"""
        event = EditingCompleted(
            session_id="sess-1",
            video_id="v1",
            quality_score=0.85,
            platform_suitability_scores={"youtube": 0.9, "tiktok": 0.7},
            review_findings_count=2,
        )

        assert event.event_type == "editing_completed"
        assert event.quality_score == 0.85


# ============================================================================
# AGENT TESTS
# ============================================================================


class TestEditingAgents:
    """Test M6 agent wrappers"""

    def test_agent_initialization(self):
        """Editing agents can be initialized"""
        agents = [
            ClipAgent(),
            TimelineAgent(),
            CutAgent(),
            TransitionAgent(),
            SubtitleAgent(),
            OverlayAgent(),
            ZoomAgent(),
            BrollAgent(),
            MusicAgent(),
            SilenceAgent(),
            ReviewAgent(),
        ]

        for agent in agents:
            assert agent.id is not None
            assert agent.name is not None

    def test_agent_capabilities(self):
        """Agents have required capabilities"""
        agent = ClipAgent()

        assert "analysis" in str(agent.capabilities).lower()

    def test_agent_execution(self):
        """Agent can execute tasks (stub test)"""
        # Note: Full execution testing requires M8 infrastructure
        agent = ClipAgent()
        assert agent.name == "ClipAgent"

    def test_review_agent(self):
        """ReviewAgent validates editing plans"""
        agent = ReviewAgent()

        assert agent.name == "ReviewAgent"
        assert agent.id is not None


class TestEditingAgentRegistry:
    """Test agent registry creation"""

    def test_registry_creation(self):
        """Agent registry can be created"""
        registry = create_editing_agent_registry()

        assert registry is not None
        assert len(registry) == 11  # 10 engines + review

    def test_registry_has_all_agents(self):
        """Registry has all expected agents"""
        registry = create_editing_agent_registry()

        expected_agents = [
            "clip",
            "timeline",
            "cut",
            "transition",
            "subtitle",
            "overlay",
            "zoom",
            "broll",
            "music",
            "silence",
            "review",
        ]

        for agent_name in expected_agents:
            assert agent_name in registry


# ============================================================================
# EDITING PLANNER TESTS
# ============================================================================


class TestEditingPlanner:
    """Test editing planner and task graph creation"""

    def test_planner_initialization(self):
        """EditingPlanner can be initialized"""
        from aura_backend.editing import EditStrategy

        planner = EditingPlanner(EditStrategy.YOUTUBE_DOCUMENTARY)

        assert planner.strategy is not None
        assert planner.constraint is not None

    def test_planner_creates_task_graph(self):
        """Planner creates task graph from M10 artifacts"""
        from aura_backend.editing import EditStrategy

        highlights = [
            Highlight(
                session_id="s1",
                video_id="v1",
                title="Peak Moment",
                start_timestamp=0.0,
                end_timestamp=5.0,
            ),
            Highlight(
                session_id="s1",
                video_id="v1",
                title="Key Point",
                start_timestamp=10.0,
                end_timestamp=15.0,
            ),
        ]

        planner = EditingPlanner(EditStrategy.YOUTUBE_DOCUMENTARY)
        tasks = planner.create_task_graph(
            session_id="s1",
            video_id="v1",
            highlights=highlights,
        )

        assert len(tasks) > 0
        assert any(t.metadata.get("engine_type") == "clip" for t in tasks)
        assert any(t.metadata.get("engine_type") == "timeline" for t in tasks)

    def test_planner_strategy_constraints(self):
        """Planner creates strategy-specific constraints"""
        from aura_backend.editing import EditStrategy

        yt_planner = EditingPlanner(EditStrategy.YOUTUBE_DOCUMENTARY)
        tiktok_planner = EditingPlanner(EditStrategy.FAST_SHORTS)

        # YouTube should have longer duration target
        assert yt_planner.constraint.target_duration_seconds > tiktok_planner.constraint.target_duration_seconds

        # TikTok should require subtitles
        assert tiktok_planner.constraint.require_subtitles

    def test_planner_task_ordering(self):
        """Planner creates tasks with proper dependencies"""
        from aura_backend.editing import EditStrategy

        quotes = [
            Quote(
                session_id="s1",
                video_id="v1",
                text="Test quote",
                start_timestamp=0.0,
                end_timestamp=3.0,
            ),
        ]

        planner = EditingPlanner()
        tasks = planner.create_task_graph(
            session_id="s1",
            video_id="v1",
            quotes=quotes,
        )

        # Should have subtitle tasks
        subtitle_tasks = [t for t in tasks if t.metadata.get("engine_type") == "subtitle"]
        assert len(subtitle_tasks) > 0


# ============================================================================
# EDIT PLAN TESTS
# ============================================================================


class TestEditPlan:
    """Test EditPlan domain model"""

    def test_plan_creation(self):
        """EditPlan can be created"""
        from aura_backend.editing import EditStrategy

        plan = EditPlan(
            session_id="s1",
            video_id="v1",
            strategy=EditStrategy.YOUTUBE_DOCUMENTARY,
        )

        assert plan.session_id == "s1"
        assert plan.video_id == "v1"

    def test_plan_immutable(self):
        """EditPlan is immutable"""
        plan = EditPlan()

        with pytest.raises(AttributeError):
            plan.session_id = "new-session"

    def test_plan_validation(self):
        """EditPlan can be validated"""
        plan_empty = EditPlan(session_id="s1", video_id="v1")
        assert not plan_empty.is_valid  # No clips or timeline

        plan_with_clips = EditPlan(
            session_id="s1",
            video_id="v1",
            clips=[
                Clip(
                    session_id="s1",
                    video_id="v1",
                    start_timestamp=0.0,
                    end_timestamp=5.0,
                ),
            ],
            timeline=EditTimeline(
                session_id="s1",
                video_id="v1",
            ),
        )
        assert plan_with_clips.is_valid

    def test_plan_duration_calculation(self):
        """EditPlan calculates total duration"""
        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
            Clip(session_id="s1", video_id="v1", start_timestamp=5.0, end_timestamp=10.0),
        ]

        plan = EditPlan(
            session_id="s1",
            video_id="v1",
            clips=clips,
        )

        assert plan.total_duration_seconds == 10.0

    def test_plan_to_dict(self):
        """EditPlan can serialize to dict"""
        from aura_backend.editing import EditStrategy

        plan = EditPlan(
            session_id="s1",
            video_id="v1",
            strategy=EditStrategy.YOUTUBE_DOCUMENTARY,
            clips=[
                Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
            ],
        )

        d = plan.to_dict()
        assert d["session_id"] == "s1"
        assert d["clip_count"] == 1


# ============================================================================
# EDIT PLAN BUILDER TESTS
# ============================================================================


class TestEditPlanBuilder:
    """Test EditPlanBuilder for plan construction"""

    def test_builder_creation(self):
        """EditPlanBuilder can be created"""
        from aura_backend.editing import EditStrategy

        builder = EditPlanBuilder(
            session_id="s1",
            video_id="v1",
            strategy=EditStrategy.YOUTUBE_DOCUMENTARY,
        )

        assert builder.session_id == "s1"

    def test_builder_builds_plan(self):
        """Builder can construct a complete plan"""
        from aura_backend.editing import EditStrategy

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]

        builder = EditPlanBuilder(
            session_id="s1",
            video_id="v1",
            strategy=EditStrategy.YOUTUBE_DOCUMENTARY,
        )

        plan = builder.build(
            clips=clips,
            timeline=EditTimeline(session_id="s1", video_id="v1"),
        )

        assert plan.clips == clips
        assert plan.timeline is not None
        assert plan.is_valid


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase3Integration:
    """Test Phase 3 components working together"""

    def test_end_to_end_orchestration(self):
        """End-to-end: Planner → Tasks → Agents"""
        from aura_backend.editing import EditStrategy

        highlights = [
            Highlight(
                session_id="s1",
                video_id="v1",
                title="Peak",
                start_timestamp=0.0,
                end_timestamp=5.0,
            ),
        ]

        # Create task graph
        planner = EditingPlanner(EditStrategy.YOUTUBE_DOCUMENTARY)
        tasks = planner.create_task_graph(
            session_id="s1",
            video_id="v1",
            highlights=highlights,
        )

        # Verify tasks exist
        assert len(tasks) > 0

        # Get agents
        registry = create_editing_agent_registry()
        assert len(registry) > 0

    def test_complete_plan_creation(self):
        """Test creating complete edit plan from scratch"""
        from aura_backend.editing import EditStrategy

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
            Clip(session_id="s1", video_id="v1", start_timestamp=5.0, end_timestamp=10.0),
        ]

        timeline = EditTimeline(
            session_id="s1",
            video_id="v1",
            clip_ids=[c.id for c in clips],
            clip_count=len(clips),
        )

        builder = EditPlanBuilder(
            session_id="s1",
            video_id="v1",
            strategy=EditStrategy.YOUTUBE_DOCUMENTARY,
        )

        plan = builder.build(
            clips=clips,
            timeline=timeline,
            review_findings=[
                ReviewFinding(
                    category="pacing",
                    severity="info",
                    message="Pacing is good",
                ),
            ],
        )

        assert plan.is_valid
        assert plan.quality_score > 0.0

"""M12 Integration Tests: Full EditPlan → ArtifactBundle Pipeline.

End-to-end rendering pipeline tests with multiple providers,
failure recovery, retry scenarios, and large video rendering.
"""

import pytest

from aura_backend.editing import Clip, EditPlan
from aura_backend.rendering import (
    FFmpegProvider,
    MockRendererProvider,
    RenderContext,
    RenderingPlanner,
)
from aura_backend.rendering.dashboard import DashboardProvider, PerformanceOptimizer
from aura_backend.rendering.metrics import MetricsAggregator
from aura_backend.rendering.stages import RenderFailure, RenderStage, StageType


@pytest.mark.asyncio
class TestEditPlanToPipeline:
    """Test full EditPlan → artifact pipeline"""

    async def test_simple_rendering_pipeline(self):
        """Basic rendering: EditPlan → stages → artifacts"""
        # Create EditPlan
        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
            Clip(session_id="s1", video_id="v1", start_timestamp=5.0, end_timestamp=10.0),
        ]
        plan = EditPlan(clips=clips)

        # Create context and planner
        context = RenderContext(session_id="s1", job_id="j1")
        planner = RenderingPlanner()

        # Generate stages
        stages = planner.create_stage_dag(plan, context)

        assert len(stages) > 0
        assert stages[0].stage_type == StageType.CLIP_RENDER

    async def test_complex_editing_with_all_components(self):
        """Complex rendering: clips + transitions + subtitles + overlays + audio"""
        from aura_backend.editing import (
            MusicCue,
            MusicMood,
            Overlay,
            OverlayType,
            SubtitleSegment,
            Transition,
            TransitionType,
        )

        clips = [
            Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
            Clip(session_id="s1", video_id="v1", start_timestamp=5.0, end_timestamp=10.0),
        ]

        transitions = [
            Transition(
                from_clip_id=clips[0].id,
                to_clip_id=clips[1].id,
                transition_type=TransitionType.FADE,
                duration_seconds=0.5,
            ),
        ]

        subtitles = [
            SubtitleSegment(
                session_id="s1",
                video_id="v1",
                start_timestamp=0.0,
                end_timestamp=2.0,
                text="Opening",
            ),
        ]

        overlays = [
            Overlay(
                session_id="s1",
                video_id="v1",
                overlay_type=OverlayType.LOWER_THIRD,
                content="Title",
            ),
        ]

        music = [
            MusicCue(
                session_id="s1",
                video_id="v1",
                mood=MusicMood.ENERGETIC,
                tempo_bpm=120,
            ),
        ]

        plan = EditPlan(
            clips=clips,
            transitions=transitions,
            subtitles=subtitles,
            overlays=overlays,
            music_suggestions=music,
        )

        context = RenderContext(session_id="s1", job_id="j1")
        planner = RenderingPlanner()

        stages = planner.create_stage_dag(plan, context)

        # Should have more stages for complex edit
        assert len(stages) >= 7  # clip, composite, subtitle, overlay, audio, export, validate

    async def test_multi_provider_execution(self):
        """Execute with multiple providers"""
        mock_provider = MockRendererProvider()
        ffmpeg_provider = FFmpegProvider()

        # Mock provider should always work
        assert await mock_provider.is_available()

        # FFmpeg provider availability
        available = await ffmpeg_provider.is_available()
        assert isinstance(available, bool)

    async def test_failure_recovery(self):
        """Test failure detection and recovery"""
        failure = RenderFailure(
            stage_id="stage-1",
            stage_type=StageType.EXPORT,
            provider_name="ffmpeg",
            error_message="Export failed",
            is_recoverable=True,
            retry_count=1,
            fallback_provider="mock",
            can_use_fallback=True,
        )

        assert failure.is_recoverable
        assert failure.can_use_fallback
        assert failure.fallback_provider == "mock"

    async def test_retry_scenario(self):
        """Test retry handling"""
        failure = RenderFailure(
            stage_id="stage-1",
            stage_type=StageType.COMPOSITE,
            provider_name="ffmpeg",
            error_message="Out of memory",
            is_recoverable=True,
            retry_count=0,
            fallback_provider="mock",
        )

        # Can retry
        assert failure.is_recoverable
        # Can use fallback after retries exhausted
        assert failure.fallback_provider is not None


@pytest.mark.asyncio
class TestLargeVideoRendering:
    """Test rendering large/complex videos"""

    async def test_large_clip_count(self):
        """Render video with many clips"""
        # Create 50 clips
        clips = [
            Clip(
                session_id="s1",
                video_id="v1",
                start_timestamp=float(i * 5),
                end_timestamp=float((i + 1) * 5),
            )
            for i in range(50)
        ]

        plan = EditPlan(clips=clips)
        context = RenderContext(session_id="s1", job_id="j1")
        planner = RenderingPlanner()

        stages = planner.create_stage_dag(plan, context)

        # Should create stages
        assert len(stages) > 0

        # Estimate duration
        duration = PerformanceOptimizer.estimate_total_duration(stages)
        assert duration > 0

    async def test_long_duration_video(self):
        """Render very long video"""
        # 2-hour video
        clips = [
            Clip(
                session_id="s1",
                video_id="v1",
                start_timestamp=0.0,
                end_timestamp=7200.0,  # 2 hours
            ),
        ]

        plan = EditPlan(clips=clips)
        context = RenderContext(session_id="s1", job_id="j1")
        planner = RenderingPlanner()

        stages = planner.create_stage_dag(plan, context)

        assert len(stages) > 0
        # Should estimate reasonable duration
        duration = PerformanceOptimizer.estimate_total_duration(stages)
        assert duration > 0


class TestParallelExecution:
    """Test parallel rendering capability"""

    def test_identify_parallel_stages(self):
        """Identify stages that can execute in parallel"""
        # Create stages with dependencies
        clip_stage = RenderStage(stage_id="s1", stage_type=StageType.CLIP_RENDER)
        composite_stage = RenderStage(
            stage_id="s2",
            stage_type=StageType.COMPOSITE,
            depends_on=["s1"],
        )
        subtitle_stage = RenderStage(
            stage_id="s3",
            stage_type=StageType.SUBTITLE,
            depends_on=["s2"],
        )
        audio_stage = RenderStage(
            stage_id="s4",
            stage_type=StageType.AUDIO,
            depends_on=["s2"],
        )

        stages = [clip_stage, composite_stage, subtitle_stage, audio_stage]

        parallel_groups = PerformanceOptimizer.calculate_parallel_stages(stages)

        # Wave 1: clip (no dependencies)
        assert "wave_1" in parallel_groups
        assert "s1" in parallel_groups["wave_1"]

        # Wave 2: composite (depends on clip)
        assert "wave_2" in parallel_groups
        assert "s2" in parallel_groups["wave_2"]

        # Wave 3: subtitle and audio (both depend on composite, can run parallel)
        assert "wave_3" in parallel_groups
        assert "s3" in parallel_groups["wave_3"]
        assert "s4" in parallel_groups["wave_3"]

    def test_duration_estimation_with_parallelism(self):
        """Estimate duration considering parallel execution"""
        stages = [
            RenderStage(
                stage_id="s1", stage_type=StageType.CLIP_RENDER, estimated_duration_seconds=10.0
            ),
            RenderStage(
                stage_id="s2",
                stage_type=StageType.COMPOSITE,
                depends_on=["s1"],
                estimated_duration_seconds=5.0,
            ),
            RenderStage(
                stage_id="s3",
                stage_type=StageType.SUBTITLE,
                depends_on=["s2"],
                estimated_duration_seconds=2.0,
            ),
            RenderStage(
                stage_id="s4",
                stage_type=StageType.AUDIO,
                depends_on=["s2"],
                estimated_duration_seconds=3.0,
            ),
        ]

        total_duration = PerformanceOptimizer.estimate_total_duration(stages)

        # Total should be: clip(10) + composite(5) + max(subtitle(2), audio(3))
        # = 10 + 5 + 3 = 18 seconds
        assert total_duration == 18.0


class TestMetricsTracking:
    """Test metrics aggregation and analysis"""

    def test_metrics_aggregator_creation(self):
        """MetricsAggregator can be created"""
        aggregator = MetricsAggregator()

        assert aggregator is not None

    def test_throughput_calculation(self):
        """Calculate throughput metrics"""
        from aura_backend.rendering.stages import RenderingMetrics

        aggregator = MetricsAggregator()

        # Add some metrics
        metrics = RenderingMetrics(
            job_id="j1",
            total_duration_seconds=30.0,
            stages_completed=5,
            validation_passed=True,
        )
        aggregator.add_metrics(metrics)

        throughput = aggregator.get_throughput_metrics()

        assert throughput.jobs_completed >= 1

    def test_provider_metrics_comparison(self):
        """Compare metrics across providers"""
        aggregator = MetricsAggregator()

        comparison = aggregator.get_provider_comparison()

        # Should return dict (empty initially)
        assert isinstance(comparison, dict)


class TestDashboard:
    """Test dashboard functionality"""

    def test_dashboard_provider_creation(self):
        """DashboardProvider can be created"""
        aggregator = MetricsAggregator()
        dashboard = DashboardProvider(aggregator)

        assert dashboard is not None

    def test_job_progress_tracking(self):
        """Track job progress"""
        aggregator = MetricsAggregator()
        dashboard = DashboardProvider(aggregator)

        stages = [
            RenderStage(stage_id="s1", stage_type=StageType.CLIP_RENDER),
            RenderStage(stage_id="s2", stage_type=StageType.EXPORT, depends_on=["s1"]),
        ]

        dashboard.register_job("j1", stages)

        progress = dashboard.get_job_progress("j1")

        assert progress.get("job_id") == "j1"
        assert progress.get("total_stages") == 2


class TestPerformanceOptimization:
    """Test performance optimization features"""

    def test_provider_selection(self):
        """Select best provider based on metrics"""

        stage = RenderStage(
            stage_id="s1",
            stage_type=StageType.EXPORT,
            preferred_provider="mock",
        )

        provider_metrics = {}

        # Should return preferred if no metrics
        selected = PerformanceOptimizer.select_best_provider(
            stage,
            {},  # Empty capabilities
            provider_metrics,
        )

        assert selected == stage.preferred_provider

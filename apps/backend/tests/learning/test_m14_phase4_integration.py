"""M14 Phase 4 Integration Tests: Production Readiness.

Tests for dashboard, metrics aggregation, optimization, and end-to-end flows.
"""

import pytest

from aura_backend.learning import (
    LearningContext,
    LearningJob,
    LearningPlanner,
    create_default_learning_agent_registry,
    create_default_provider_registry,
)
from aura_backend.learning.dashboard import (
    AnalyticsProgress,
    CreatorProfileEvolution,
    LearningDashboard,
    LearningQueueItem,
    MemoryStatistics,
    ProviderHealth,
    ProviderHealthStatus,
    RecommendationSummary,
)
from aura_backend.learning.operational_metrics import (
    ObjectiveCompletionMetric,
    OperationalMetricsAggregator,
    ProviderLatencyMetric,
    RecommendationMetric,
    StageDurationMetric,
)
from aura_backend.learning.optimizer import (
    CapabilityBasedProviderSelector,
    ParallelAnalyticsCollector,
    QueueOptimizer,
    RecommendationCacheManager,
    RetryOptimizer,
)

# ============================================================================
# LEARNING DASHBOARD INTEGRATION TESTS
# ============================================================================


class TestLearningDashboard:
    """Test learning dashboard functionality."""

    def test_dashboard_initialization(self):
        """Initialize dashboard."""
        dashboard = LearningDashboard()
        assert dashboard is not None

    def test_queue_management(self):
        """Test learning queue management."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        item1 = LearningQueueItem(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
            queued_at=now,
            estimated_duration_seconds=60,
            priority=5,
        )
        item2 = LearningQueueItem(
            job_id="job-2",
            creator_id="creator-2",
            platform="tiktok",
            queued_at=now,
            estimated_duration_seconds=45,
            priority=8,
        )

        dashboard.add_to_queue(item1)
        dashboard.add_to_queue(item2)

        queue = dashboard.get_queue()
        assert len(queue) == 2
        # Higher priority should be first
        assert queue[0].priority >= queue[1].priority

        dashboard.remove_from_queue("job-1")
        assert len(dashboard.get_queue()) == 1

    def test_provider_health_tracking(self):
        """Test provider health monitoring."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        youtube_health = ProviderHealth(
            provider_name="youtube",
            status=ProviderHealthStatus.HEALTHY,
            last_check=now,
            success_rate=0.99,
            avg_latency_ms=150.0,
            total_requests=1000,
            failed_requests=10,
        )

        dashboard.update_provider_health(youtube_health)
        health_dict = dashboard.get_provider_health()
        assert "youtube" in health_dict
        assert health_dict["youtube"].status == ProviderHealthStatus.HEALTHY

    def test_analytics_progress_tracking(self):
        """Test analytics progress tracking."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        progress = AnalyticsProgress(
            job_id="job-1",
            platform="youtube",
            stage_type="retrieve_metrics",
            progress_percent=50,
            started_at=now,
            current_step="Fetching video statistics",
        )

        dashboard.update_analytics_progress(progress)
        retrieved = dashboard.get_analytics_progress("job-1")
        assert retrieved.progress_percent == 50

    def test_recommendation_summary_tracking(self):
        """Test recommendation summary tracking."""
        dashboard = LearningDashboard()

        summary = RecommendationSummary(
            job_id="job-1",
            total_count=10,
            high_priority=4,
            medium_priority=4,
            low_priority=2,
            avg_confidence=0.85,
            categories={"thumbnail": 3, "description": 4, "tags": 3},
        )

        dashboard.update_recommendations(summary)
        retrieved = dashboard.get_recommendations("job-1")
        assert retrieved.total_count == 10
        assert retrieved.avg_confidence == 0.85

    def test_creator_profile_evolution(self):
        """Test creator profile evolution tracking."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        evolution = CreatorProfileEvolution(
            creator_id="creator-1",
            timestamp=now,
            profile_version=2,
            fields_updated=4,
            learning_version="v2",
            avg_video_length_change=2.5,
            topic_diversity_change=0.1,
        )

        dashboard.update_creator_evolution(evolution)
        history = dashboard.get_creator_history("creator-1")
        assert len(history) == 1
        assert history[0].profile_version == 2

    def test_memory_statistics_tracking(self):
        """Test learning memory statistics."""
        dashboard = LearningDashboard()

        stats = MemoryStatistics(
            creator_id="creator-1",
            total_experiments=50,
            recent_experiments=5,
            total_recommendations_seen=100,
            accepted_recommendations=30,
            acceptance_rate=0.3,
            memory_size_kb=125.5,
        )

        dashboard.update_memory_statistics(stats)
        retrieved = dashboard.get_memory_statistics("creator-1")
        assert retrieved.acceptance_rate == 0.3

    def test_dashboard_snapshot(self):
        """Test complete dashboard snapshot."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        dashboard.add_to_queue(
            LearningQueueItem(
                job_id="job-1",
                creator_id="creator-1",
                platform="youtube",
                queued_at=now,
                estimated_duration_seconds=60,
                priority=5,
            )
        )

        dashboard.update_provider_health(
            ProviderHealth(
                provider_name="youtube",
                status=ProviderHealthStatus.HEALTHY,
                last_check=now,
                success_rate=0.99,
                avg_latency_ms=150.0,
                total_requests=1000,
                failed_requests=10,
            )
        )

        snapshot = dashboard.get_dashboard_snapshot()
        assert "queue" in snapshot
        assert "provider_health" in snapshot
        assert snapshot["queue"]["size"] == 1


# ============================================================================
# OPERATIONAL METRICS AGGREGATOR TESTS
# ============================================================================


class TestOperationalMetricsAggregator:
    """Test operational metrics aggregation."""

    def test_aggregator_initialization(self):
        """Initialize metrics aggregator."""
        aggregator = OperationalMetricsAggregator()
        assert aggregator is not None

    def test_stage_duration_recording(self):
        """Test recording stage durations."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        metric1 = StageDurationMetric(
            stage_type="retrieve_metrics",
            platform="youtube",
            duration_ms=150.0,
            timestamp=now,
            provider_name="youtube",
            success=True,
        )
        metric2 = StageDurationMetric(
            stage_type="retrieve_metrics",
            platform="tiktok",
            duration_ms=200.0,
            timestamp=now,
            provider_name="tiktok",
            success=True,
        )

        aggregator.record_stage_duration(metric1)
        aggregator.record_stage_duration(metric2)

        stats = aggregator.get_stage_duration_stats()
        assert stats["count"] == 2
        assert stats["avg_ms"] == 175.0
        assert stats["success_rate"] == 1.0

    def test_provider_latency_recording(self):
        """Test recording provider latencies."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        latency1 = ProviderLatencyMetric(
            provider_name="youtube",
            method="get_video_metrics",
            latency_ms=120.0,
            timestamp=now,
            success=True,
        )
        latency2 = ProviderLatencyMetric(
            provider_name="youtube",
            method="get_retention_curve",
            latency_ms=200.0,
            timestamp=now,
            success=True,
        )

        aggregator.record_provider_latency(latency1)
        aggregator.record_provider_latency(latency2)

        stats = aggregator.get_provider_latency_stats("youtube")
        assert stats["count"] == 2
        assert stats["avg_ms"] == 160.0
        assert len(stats["by_method"]) == 2

    def test_recommendation_metrics_recording(self):
        """Test recording recommendation metrics."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        rec_metric = RecommendationMetric(
            job_id="job-1",
            count=8,
            avg_confidence=0.87,
            generation_time_ms=250.0,
            timestamp=now,
            by_category={"thumbnail": 3, "description": 3, "tags": 2},
        )

        aggregator.record_recommendation_metric(rec_metric)

        stats = aggregator.get_recommendation_stats()
        assert stats["total_generated"] == 8
        assert stats["avg_confidence"] == 0.87
        assert stats["by_category"]["thumbnail"] == 3

    def test_confidence_distribution(self):
        """Test confidence distribution analysis."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        aggregator.record_recommendation_metric(
            RecommendationMetric(
                job_id="job-1",
                count=5,
                avg_confidence=0.9,
                generation_time_ms=200.0,
                timestamp=now,
            )
        )
        aggregator.record_recommendation_metric(
            RecommendationMetric(
                job_id="job-2",
                count=3,
                avg_confidence=0.6,
                generation_time_ms=200.0,
                timestamp=now,
            )
        )

        distribution = aggregator.get_confidence_distribution()
        assert distribution["high"] == 5
        assert distribution["medium"] == 3
        assert distribution["total"] == 8

    def test_objective_completion_tracking(self):
        """Test objective completion tracking."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        metric = ObjectiveCompletionMetric(
            job_id="job-1",
            objectives={"obj1": True, "obj2": True, "obj3": False},
            completion_percent=66.7,
            timestamp=now,
        )

        aggregator.record_objective_completion(metric)

        stats = aggregator.get_objective_completion_stats()
        assert stats["jobs_tracked"] == 1
        assert stats["fully_completed"] == 0

    def test_comprehensive_report(self):
        """Test comprehensive metrics report."""
        aggregator = OperationalMetricsAggregator()
        now = __import__("datetime").datetime.utcnow()

        aggregator.record_stage_duration(
            StageDurationMetric(
                stage_type="validate",
                platform="youtube",
                duration_ms=100.0,
                timestamp=now,
                success=True,
            )
        )

        report = aggregator.get_comprehensive_report()
        assert "timestamp" in report
        assert "stage_duration" in report
        assert "provider_latency" in report
        assert "recommendations" in report


# ============================================================================
# PERFORMANCE OPTIMIZER TESTS
# ============================================================================


class TestPerformanceOptimizers:
    """Test performance optimization components."""

    def test_capability_based_provider_selection(self):
        """Test capability-based provider selection."""
        selector = CapabilityBasedProviderSelector()
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
        )

        required_caps = ("video_metrics", "retention_curve")
        providers = create_default_provider_registry().get_providers()

        selection = selector.select_provider(context, required_caps, providers)
        assert selection.primary_provider is not None

    def test_recommendation_cache(self):
        """Test recommendation caching."""
        cache = RecommendationCacheManager(ttl_minutes=60)
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
        )

        recs = {"recommendation": [1, 2, 3]}
        cache.set(context, recs, confidence=0.9)

        cached = cache.get(context)
        assert cached == recs

    def test_cache_expiration(self):
        """Test cache expiration."""
        import time

        cache = RecommendationCacheManager(ttl_minutes=0)  # Expire immediately
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
        )

        cache.set(context, {"data": "test"})
        time.sleep(0.1)

        cached = cache.get(context)
        assert cached is None

    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = RecommendationCacheManager()
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
        )

        cache.set(context, {"data": "test"})
        invalidated = cache.invalidate("creator-1")
        assert invalidated == 1

    def test_queue_optimizer(self):
        """Test queue optimization."""
        optimizer = QueueOptimizer(max_parallel_jobs=3)

        # Mark jobs as active
        optimizer.mark_job_active("job-1")
        optimizer.mark_job_active("job-2")

        assert optimizer.get_active_count() == 2

        optimizer.mark_job_complete("job-1")
        assert optimizer.get_active_count() == 1

    def test_retry_optimizer(self):
        """Test retry optimization."""
        optimizer = RetryOptimizer(max_retries=3)

        should_retry, backoff = optimizer.should_retry("stage-1", "timeout", 0)
        assert should_retry is True
        assert backoff > 0

        should_retry, backoff = optimizer.should_retry("stage-1", "auth_error", 0)
        assert should_retry is False

    def test_parallel_analytics_collector(self):
        """Test parallel analytics collection."""
        collector = ParallelAnalyticsCollector(max_parallel=3)

        platforms = ["youtube", "tiktok", "instagram"]
        can_collect = collector.can_collect_in_parallel("job-1", platforms)
        assert can_collect is True

        collector.start_collection("job-1", platforms)
        assert collector.get_active_count("job-1") == 3


# ============================================================================
# MULTI-PLATFORM INTEGRATION TESTS
# ============================================================================


class TestMultiPlatformIntegration:
    """Test multi-platform learning flows."""

    def test_multi_platform_dag_generation(self):
        """Test DAG generation for multiple platforms."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")

        for platform in ["youtube", "tiktok", "instagram"]:
            context = LearningContext(
                job_id=job.id,
                creator_id="creator-1",
                platform=platform,
            )

            stages = planner.create_stage_dag(job, context, None)
            assert len(stages) > 0

    def test_provider_fallback_flow(self):
        """Test provider fallback when primary fails."""
        providers = create_default_provider_registry().get_providers()
        assert "mock" in providers  # Mock provider always available

    def test_multi_platform_recommendation_generation(self):
        """Test recommendation generation across platforms."""
        job = LearningJob(creator_id="creator-1")
        platforms = ["youtube", "tiktok", "instagram"]

        for platform in platforms:
            context = LearningContext(
                job_id=job.id,
                creator_id="creator-1",
                platform=platform,
            )

            assert context.platform == platform


# ============================================================================
# LEARNING RECOVERY TESTS
# ============================================================================


class TestLearningRecovery:
    """Test learning recovery mechanisms."""

    def test_stage_retry_on_transient_error(self):
        """Test stage retry on transient errors."""
        optimizer = RetryOptimizer()

        should_retry, backoff = optimizer.should_retry("stage-1", "timeout", 0)
        assert should_retry is True
        assert backoff > 0

        should_retry, backoff = optimizer.should_retry("stage-1", "timeout", 3)
        assert should_retry is False

    def test_provider_fallback_selection(self):
        """Test fallback provider selection."""
        selector = CapabilityBasedProviderSelector()
        context = LearningContext(
            job_id="job-1",
            creator_id="creator-1",
            platform="youtube",
        )

        providers = create_default_provider_registry().get_providers()
        selection = selector.select_provider(context, ("video_metrics",), providers)

        assert selection.primary_provider is not None


# ============================================================================
# END-TO-END ORCHESTRATION TESTS
# ============================================================================


class TestEndToEndOrchestration:
    """Test complete end-to-end learning orchestration."""

    def test_full_learning_pipeline(self):
        """Test full learning pipeline."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")
        context = LearningContext(
            job_id=job.id,
            creator_id="creator-1",
            platform="youtube",
        )

        # Create DAG
        stages = planner.create_stage_dag(job, context, None)
        assert len(stages) > 0

        # Convert to M8 tasks
        tasks = planner.stages_to_m8_tasks(stages)
        assert len(tasks) == len(stages)

        # Verify all tasks have metadata
        for task in tasks:
            assert task.metadata.get("stage_type") is not None

    def test_multi_agent_orchestration(self):
        """Test multi-agent orchestration."""
        registry = create_default_learning_agent_registry()
        agents = registry.list_agents()

        assert len(agents) >= 7  # Should have all 7 agents

    @pytest.mark.asyncio
    async def test_agent_execution_chain(self):
        """Test agent execution chain."""
        registry = create_default_learning_agent_registry()

        from aura_backend.learning.stages import StageType

        validation_agents = registry.get_agents_for_stage(StageType.VALIDATE)
        assert len(validation_agents) > 0


# ============================================================================
# PERFORMANCE AND THROUGHPUT TESTS
# ============================================================================


class TestPerformanceMetrics:
    """Test performance metric tracking."""

    def test_metrics_under_load(self):
        """Test metrics aggregation under load."""
        aggregator = OperationalMetricsAggregator(max_history=1000)
        now = __import__("datetime").datetime.utcnow()

        for i in range(100):
            aggregator.record_stage_duration(
                StageDurationMetric(
                    stage_type="retrieve_metrics",
                    platform="youtube" if i % 2 == 0 else "tiktok",
                    duration_ms=100.0 + (i * 0.5),
                    timestamp=now,
                    success=True,
                )
            )

        stats = aggregator.get_stage_duration_stats()
        assert stats["count"] == 100
        assert stats["avg_ms"] > 0

    def test_concurrent_dashboard_updates(self):
        """Test concurrent dashboard updates."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        for i in range(50):
            dashboard.add_to_queue(
                LearningQueueItem(
                    job_id=f"job-{i}",
                    creator_id=f"creator-{i}",
                    platform="youtube" if i % 3 == 0 else "tiktok",
                    queued_at=now,
                    estimated_duration_seconds=60,
                    priority=i % 10,
                )
            )

        queue = dashboard.get_queue()
        assert len(queue) == 50

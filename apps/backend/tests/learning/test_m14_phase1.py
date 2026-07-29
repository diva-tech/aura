"""M14 Phase 1 Tests: Learning Foundation.

Tests for domain models, profiles, memory, recommendations, metrics, and manifest.
"""

from datetime import datetime, timedelta

import pytest

from aura_backend.learning import (
    AnalyticsReference,
    AudienceProfile,
    AudienceSegment,
    CategoryRecommendations,
    ConfidenceHistory,
    CreatorMetricsSummary,
    CreatorPreference,
    CreatorProfile,
    CTRMetrics,
    EngagementMetrics,
    ExperimentRecord,
    FeatureImportance,
    LearningConfidence,
    LearningJob,
    LearningManifest,
    LearningMemory,
    LearningObjective,
    LearningPriority,
    LearningReport,
    LearningStatus,
    LearningTask,
    MetricTrend,
    OptimizationHistory,
    OptimizationRecommendation,
    PerformanceComparison,
    PlatformMetrics,
    RecommendationAcceptance,
    RecommendationBatch,
    RecommendationCategory,
    RecommendationPriority,
    RecommendationSummary,
    RetentionCurve,
    RevenueMetrics,
    VideoLengthPreference,
    VideoPerformance,
    WatchTimeMetrics,
)

# ============================================================================
# DOMAIN MODEL TESTS
# ============================================================================


class TestLearningModels:
    """Test core learning domain models."""

    def test_learning_job_creation(self):
        """Create learning job."""
        job = LearningJob(
            creator_id="creator-1",
            job_type="general_learning",
            priority=LearningPriority.HIGH,
        )

        assert job.creator_id == "creator-1"
        assert job.status == LearningStatus.PENDING
        assert job.id is not None

    def test_learning_job_immutable(self):
        """Job is immutable."""
        job = LearningJob()

        with pytest.raises(AttributeError):
            job.creator_id = "new-creator"

    def test_learning_task_creation(self):
        """Create learning task."""
        task = LearningTask(
            learning_job_id="job-1",
            task_type="analyze_performance",
        )

        assert task.learning_job_id == "job-1"
        assert task.status == LearningStatus.PENDING
        assert task.id is not None

    def test_learning_objective_creation(self):
        """Create learning objective."""
        obj = LearningObjective(
            objective_type="increase_ctr",
            weight=1.5,
            target_value=8.5,
        )

        assert obj.objective_type == "increase_ctr"
        assert obj.weight == 1.5
        assert obj.target_value == 8.5


# ============================================================================
# PERFORMANCE METRICS TESTS
# ============================================================================


class TestPerformanceMetrics:
    """Test performance metric models."""

    def test_video_performance_creation(self):
        """Create video performance."""
        perf = VideoPerformance(
            video_id="video-1",
            published_asset_id="asset-1",
            views=1000,
            watch_time_seconds=15000,
            average_view_duration_seconds=15.0,
        )

        assert perf.views == 1000
        assert perf.watch_time_seconds == 15000

    def test_retention_curve_creation(self):
        """Create retention curve."""
        curve = RetentionCurve(
            video_id="video-1",
            timeline_seconds=(0, 30, 60, 90, 120),
            retention_percentages=(100, 85, 70, 60, 50),
            completion_rate=45.0,
        )

        assert curve.timeline_seconds == (0, 30, 60, 90, 120)
        assert curve.completion_rate == 45.0

    def test_watch_time_metrics_creation(self):
        """Create watch time metrics."""
        metrics = WatchTimeMetrics(
            video_id="video-1",
            total_watch_time_seconds=50000,
            average_duration_seconds=25.0,
            repeat_views=150,
        )

        assert metrics.total_watch_time_seconds == 50000
        assert metrics.repeat_views == 150

    def test_ctr_metrics_creation(self):
        """Create CTR metrics."""
        metrics = CTRMetrics(
            video_id="video-1",
            ctr=8.5,
            impressions=1000,
            clicks=85,
        )

        assert metrics.ctr == 8.5
        assert metrics.clicks == 85

    def test_engagement_metrics_creation(self):
        """Create engagement metrics."""
        metrics = EngagementMetrics(
            video_id="video-1",
            likes=500,
            comments=120,
            shares=45,
            engagement_score=6.8,
        )

        assert metrics.likes == 500
        assert metrics.engagement_score == 6.8

    def test_revenue_metrics_creation(self):
        """Create revenue metrics."""
        metrics = RevenueMetrics(
            video_id="video-1",
            revenue=150.50,
            rpm=4.25,
            views=35400,
        )

        assert metrics.revenue == 150.50
        assert metrics.rpm == 4.25


# ============================================================================
# CREATOR PROFILE TESTS
# ============================================================================


class TestCreatorProfiles:
    """Test creator profile models."""

    def test_creator_profile_creation(self):
        """Create creator profile."""
        profile = CreatorProfile(
            creator_id="creator-1",
            preferred_video_length=VideoLengthPreference.MEDIUM,
            preferred_topics=("tech", "productivity"),
            preferred_platforms=("youtube", "tiktok"),
        )

        assert profile.creator_id == "creator-1"
        assert len(profile.preferred_topics) == 2

    def test_creator_profile_immutable(self):
        """Profile is immutable."""
        profile = CreatorProfile()

        with pytest.raises(AttributeError):
            profile.creator_id = "new-id"

    def test_creator_preference_creation(self):
        """Create creator preference."""
        pref = CreatorPreference(
            preference_type="video_length",
            values=("10-15 min", "15-20 min"),
            confidence=0.85,
            samples_count=25,
        )

        assert pref.preference_type == "video_length"
        assert len(pref.values) == 2


# ============================================================================
# AUDIENCE PROFILE TESTS
# ============================================================================


class TestAudienceProfiles:
    """Test audience profile models."""

    def test_audience_segment_creation(self):
        """Create audience segment."""
        segment = AudienceSegment(
            segment_name="Young Professionals",
            age_group="25-35",
            geography=("US", "UK", "Canada"),
            interests=("tech", "career", "finance"),
            size_percent=35.0,
        )

        assert segment.segment_name == "Young Professionals"
        assert len(segment.geography) == 3

    def test_audience_profile_creation(self):
        """Create audience profile."""
        segment = AudienceSegment(segment_name="Segment 1")

        profile = AudienceProfile(
            creator_id="creator-1",
            total_subscribers=50000,
            returning_viewer_rate=0.65,
            segments=(segment,),
            top_geographies=("US", "UK"),
        )

        assert profile.total_subscribers == 50000
        assert len(profile.segments) == 1

    def test_audience_profile_immutable(self):
        """Profile is immutable."""
        profile = AudienceProfile()

        with pytest.raises(AttributeError):
            profile.total_subscribers = 100000


# ============================================================================
# OPTIMIZATION RECOMMENDATION TESTS
# ============================================================================


class TestOptimizationRecommendations:
    """Test recommendation models."""

    def test_optimization_recommendation_creation(self):
        """Create recommendation."""
        rec = OptimizationRecommendation(
            category=RecommendationCategory.THUMBNAIL,
            priority=RecommendationPriority.HIGH,
            confidence=LearningConfidence.HIGH,
            expected_improvement=0.15,
        )

        assert rec.category == RecommendationCategory.THUMBNAIL
        assert rec.id is not None

    def test_recommendation_immutable(self):
        """Recommendation is immutable."""
        rec = OptimizationRecommendation()

        with pytest.raises(AttributeError):
            rec.expected_improvement = 0.25

    def test_recommendation_batch_creation(self):
        """Create recommendation batch."""
        rec1 = OptimizationRecommendation()
        rec2 = OptimizationRecommendation()

        batch = RecommendationBatch(
            video_id="video-1",
            published_asset_id="asset-1",
            recommendations=(rec1, rec2),
            total_expected_improvement=0.25,
        )

        assert len(batch.recommendations) == 2

    def test_category_recommendations_creation(self):
        """Create category recommendations."""
        rec = OptimizationRecommendation(
            category=RecommendationCategory.TITLE,
        )

        cat_recs = CategoryRecommendations(
            category=RecommendationCategory.TITLE,
            recommendations=(rec,),
            count=1,
        )

        assert cat_recs.category == RecommendationCategory.TITLE

    def test_recommendation_summary_creation(self):
        """Create recommendation summary."""
        summary = RecommendationSummary(
            creator_id="creator-1",
            total_recommendations=15,
            high_priority_count=5,
            high_confidence_count=8,
        )

        assert summary.total_recommendations == 15


# ============================================================================
# LEARNING MEMORY TESTS
# ============================================================================


class TestLearningMemory:
    """Test learning memory models."""

    def test_feature_importance_creation(self):
        """Create feature importance."""
        importance = FeatureImportance(
            feature_name="thumbnail",
            importance_score=0.85,
            rank=1,
            confidence=0.90,
        )

        assert importance.feature_name == "thumbnail"
        assert importance.rank == 1

    def test_recommendation_acceptance_creation(self):
        """Create recommendation acceptance record."""
        acceptance = RecommendationAcceptance(
            recommendation_id="rec-1",
            category="thumbnail",
            accepted=True,
            impact_on_performance=0.12,
        )

        assert acceptance.accepted is True
        assert acceptance.impact_on_performance == 0.12

    def test_experiment_record_creation(self):
        """Create experiment record."""
        experiment = ExperimentRecord(
            experiment_id="exp-1",
            category="title",
            hypothesis="Longer titles increase CTR",
            control_videos=("vid-1", "vid-2"),
            variant_videos=("vid-3", "vid-4"),
            metric_tracked="ctr",
            control_performance=5.2,
            variant_performance=6.8,
            improvement_percent=30.8,
        )

        assert experiment.improvement_percent == 30.8

    def test_optimization_history_creation(self):
        """Create optimization history."""
        history = OptimizationHistory(
            category="thumbnail",
            action_taken="Changed to bright colors",
            videos_applied_to=("vid-1", "vid-2"),
            performance_before=0.05,
            performance_after=0.068,
        )

        assert history.improvement_percent == 36.0

    def test_confidence_history_creation(self):
        """Create confidence history."""
        now = datetime.utcnow()
        conf_history = ConfidenceHistory(
            category="thumbnail",
            timeline=(now - timedelta(days=30), now),
            confidence_scores=(0.65, 0.85),
            sample_counts=(10, 25),
        )

        assert len(conf_history.timeline) == 2

    def test_learning_memory_creation(self):
        """Create learning memory."""
        memory = LearningMemory(
            creator_id="creator-1",
            total_videos_analyzed=50,
            total_recommendations_made=100,
            total_recommendations_accepted=75,
            acceptance_rate=0.75,
        )

        assert memory.total_videos_analyzed == 50
        assert memory.acceptance_rate == 0.75

    def test_learning_memory_immutable(self):
        """Memory is immutable."""
        memory = LearningMemory()

        with pytest.raises(AttributeError):
            memory.total_videos_analyzed = 100


# ============================================================================
# METRICS AGGREGATION TESTS
# ============================================================================


class TestMetricsAggregations:
    """Test metrics aggregation models."""

    def test_metric_trend_creation(self):
        """Create metric trend."""
        now = datetime.utcnow()
        trend = MetricTrend(
            metric_name="ctr",
            timeline=(now - timedelta(days=30), now),
            values=(5.0, 6.5),
            trend_direction="up",
            trend_magnitude=0.30,
        )

        assert trend.metric_name == "ctr"
        assert trend.trend_direction == "up"

    def test_performance_comparison_creation(self):
        """Create performance comparison."""
        comp = PerformanceComparison(
            metric_name="views",
            period_1_name="Last Month",
            period_1_value=10000,
            period_2_name="This Month",
            period_2_value=15000,
            change_percent=50.0,
        )

        assert comp.change_percent == 50.0

    def test_creator_metrics_summary_creation(self):
        """Create creator metrics summary."""
        summary = CreatorMetricsSummary(
            creator_id="creator-1",
            period="last_30_days",
            total_videos=10,
            total_views=50000,
            average_ctr=6.5,
            average_engagement_rate=0.08,
        )

        assert summary.total_videos == 10

    def test_platform_metrics_creation(self):
        """Create platform metrics."""
        metrics = PlatformMetrics(
            platform="youtube",
            creator_id="creator-1",
            total_videos=10,
            total_views=50000,
            best_posting_day="wednesday",
            best_posting_time="19:00",
        )

        assert metrics.platform == "youtube"


# ============================================================================
# ANALYTICS REFERENCE TESTS
# ============================================================================


class TestAnalyticsReference:
    """Test analytics reference model."""

    def test_analytics_reference_creation(self):
        """Create analytics reference."""
        ref = AnalyticsReference(
            published_asset_id="asset-1",
            platform="youtube",
            video_id="dQw4w9WgXcQ",
            external_reference="yt:dQw4w9WgXcQ",
        )

        assert ref.published_asset_id == "asset-1"
        assert ref.id is not None

    def test_analytics_reference_immutable(self):
        """Reference is immutable."""
        ref = AnalyticsReference()

        with pytest.raises(AttributeError):
            ref.platform = "tiktok"


# ============================================================================
# LEARNING REPORT TESTS
# ============================================================================


class TestLearningReports:
    """Test learning report models."""

    def test_learning_report_creation(self):
        """Create learning report."""
        report = LearningReport(
            learning_job_id="job-1",
            total_tasks=20,
            completed_tasks=18,
            successful_tasks=16,
            recommendations_generated=50,
        )

        assert report.total_tasks == 20
        assert report.completed_tasks == 18

    def test_learning_report_immutable(self):
        """Report is immutable."""
        report = LearningReport()

        with pytest.raises(AttributeError):
            report.total_tasks = 100


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================


class TestSerialization:
    """Test model serialization."""

    def test_learning_job_to_dict(self):
        """Serialize learning job."""
        job = LearningJob(
            creator_id="creator-1",
            learning_objectives=("increase_ctr", "improve_retention"),
        )

        d = job.to_dict()

        assert d["creator_id"] == "creator-1"
        assert len(d["learning_objectives"]) == 2

    def test_video_performance_to_dict(self):
        """Serialize video performance."""
        perf = VideoPerformance(
            video_id="video-1",
            views=1000,
            likes=50,
        )

        d = perf.to_dict()

        assert d["views"] == 1000
        assert d["likes"] == 50

    def test_creator_profile_to_dict(self):
        """Serialize creator profile."""
        profile = CreatorProfile(
            creator_id="creator-1",
            preferred_topics=("tech", "productivity"),
        )

        d = profile.to_dict()

        assert d["creator_id"] == "creator-1"
        assert len(d["preferred_topics"]) == 2

    def test_learning_memory_to_dict(self):
        """Serialize learning memory."""
        memory = LearningMemory(
            creator_id="creator-1",
            total_videos_analyzed=50,
        )

        d = memory.to_dict()

        assert d["total_videos_analyzed"] == 50


# ============================================================================
# MANIFEST TESTS
# ============================================================================


class TestLearningManifest:
    """Test learning manifest."""

    def test_manifest_creation(self):
        """Create learning manifest."""
        job = LearningJob(creator_id="creator-1")
        manifest = LearningManifest(learning_job=job)

        assert manifest.learning_job.creator_id == "creator-1"
        assert manifest.id is not None

    def test_manifest_get_learning_job_id(self):
        """Get learning job ID from manifest."""
        job = LearningJob(creator_id="creator-1")
        manifest = LearningManifest(learning_job=job)

        assert manifest.get_learning_job_id() == job.id

    def test_manifest_get_creator_id(self):
        """Get creator ID from manifest."""
        job = LearningJob(creator_id="creator-1")
        manifest = LearningManifest(learning_job=job)

        assert manifest.get_creator_id() == "creator-1"

    def test_manifest_get_task_count(self):
        """Get task count from manifest."""
        task = LearningTask(learning_job_id="job-1")
        manifest = LearningManifest(learning_tasks=(task,))

        assert manifest.get_task_count() == 1

    def test_manifest_filter_tasks_by_status(self):
        """Filter tasks by status."""
        task1 = LearningTask(status=LearningStatus.COMPLETED)
        task2 = LearningTask(status=LearningStatus.PENDING)

        manifest = LearningManifest(learning_tasks=(task1, task2))

        completed = manifest.filter_tasks_by_status(LearningStatus.COMPLETED)
        assert len(completed) == 1

    def test_manifest_filter_recommendations_by_priority(self):
        """Filter recommendations by priority."""
        rec1 = OptimizationRecommendation(priority=RecommendationPriority.HIGH)
        rec2 = OptimizationRecommendation(priority=RecommendationPriority.LOW)

        manifest = LearningManifest(
            optimization_recommendations=(rec1, rec2),
        )

        high_priority = manifest.filter_recommendations_by_priority(
            RecommendationPriority.HIGH,
        )
        assert len(high_priority) == 1

    def test_manifest_to_dict(self):
        """Serialize manifest."""
        job = LearningJob(creator_id="creator-1")
        manifest = LearningManifest(learning_job=job)

        d = manifest.to_dict()

        assert d["manifest_version"] == 1
        assert d["learning_job"]["creator_id"] == "creator-1"

    def test_manifest_immutable(self):
        """Manifest is immutable."""
        manifest = LearningManifest()

        with pytest.raises(AttributeError):
            manifest.manifest_version = 2

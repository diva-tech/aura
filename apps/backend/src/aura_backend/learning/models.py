"""M14 Phase 1: Learning Foundation – Domain Models.

Immutable models for the Learning & Optimization Engine.
Tracks learning jobs, tasks, performance metrics, and recommendations.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class LearningStatus(StrEnum):
    """Learning job status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class LearningPriority(StrEnum):
    """Learning priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationPriority(StrEnum):
    """Recommendation priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationCategory(StrEnum):
    """Optimization recommendation categories."""

    THUMBNAIL = "thumbnail"
    TITLE = "title"
    DESCRIPTION = "description"
    HASHTAGS = "hashtags"
    EDITING = "editing"
    PACING = "pacing"
    HOOK = "hook"
    CTA = "cta"
    PUBLISHING_TIME = "publishing_time"
    PLATFORM = "platform"
    CONTENT_STRATEGY = "content_strategy"


class LearningConfidence(StrEnum):
    """Confidence levels for recommendations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================================================
# LEARNING JOB & TASK MODELS
# ============================================================================


@dataclass(frozen=True)
class LearningTask:
    """Atomic learning task."""

    id: str = ""
    learning_job_id: str = ""
    task_type: str = ""
    status: LearningStatus = LearningStatus.PENDING
    published_asset_id: str | None = None
    analytics_reference_id: str | None = None
    performance_metrics: dict = None
    created_at: datetime = None
    completed_at: datetime | None = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learning_job_id": self.learning_job_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "published_asset_id": self.published_asset_id,
            "analytics_reference_id": self.analytics_reference_id,
            "performance_metrics": self.performance_metrics or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass(frozen=True)
class LearningJob:
    """Learning job for a single creator or campaign."""

    id: str = ""
    creator_id: str = ""
    job_type: str = "general_learning"
    status: LearningStatus = LearningStatus.PENDING
    priority: LearningPriority = LearningPriority.MEDIUM
    learning_objectives: tuple[str, ...] = None
    published_assets_count: int = 0
    learning_tasks_count: int = 0
    recommendations_generated: int = 0
    created_at: datetime = None
    completed_at: datetime | None = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())
        if self.learning_objectives is None:
            object.__setattr__(self, "learning_objectives", ())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "priority": self.priority.value,
            "learning_objectives": (
                list(self.learning_objectives) if self.learning_objectives else []
            ),
            "published_assets_count": self.published_assets_count,
            "learning_tasks_count": self.learning_tasks_count,
            "recommendations_generated": self.recommendations_generated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ============================================================================
# PERFORMANCE METRICS
# ============================================================================


@dataclass(frozen=True)
class PerformanceMetric:
    """Base performance metric with confidence."""

    metric_name: str = ""
    value: float = 0.0
    confidence: float = 100.0  # 0-100%
    source: str = "analytics"
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass(frozen=True)
class VideoPerformance:
    """Complete performance metrics for a single video."""

    video_id: str = ""
    published_asset_id: str = ""
    views: int = 0
    unique_views: int = 0
    watch_time_seconds: int = 0
    average_view_duration_seconds: float = 0.0
    audience_retention: float = 0.0
    click_through_rate: float = 0.0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    subscribers_gained: int = 0
    revenue: float = 0.0
    rpm: float = 0.0
    engagement_score: float = 0.0
    completion_rate: float = 0.0
    bounce_rate: float = 0.0
    conversion_rate: float = 0.0
    platform: str = ""
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "published_asset_id": self.published_asset_id,
            "views": self.views,
            "unique_views": self.unique_views,
            "watch_time_seconds": self.watch_time_seconds,
            "average_view_duration_seconds": self.average_view_duration_seconds,
            "audience_retention": self.audience_retention,
            "click_through_rate": self.click_through_rate,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "subscribers_gained": self.subscribers_gained,
            "revenue": self.revenue,
            "rpm": self.rpm,
            "engagement_score": self.engagement_score,
            "completion_rate": self.completion_rate,
            "bounce_rate": self.bounce_rate,
            "conversion_rate": self.conversion_rate,
            "platform": self.platform,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class RetentionCurve:
    """Video retention curve data."""

    video_id: str = ""
    timeline_seconds: tuple[int, ...] = None
    retention_percentages: tuple[float, ...] = None
    drop_off_points: tuple[int, ...] = None
    peak_engagement_seconds: int = 0
    completion_rate: float = 0.0
    recorded_at: datetime = None

    def __post_init__(self):
        if self.timeline_seconds is None:
            object.__setattr__(self, "timeline_seconds", ())
        if self.retention_percentages is None:
            object.__setattr__(self, "retention_percentages", ())
        if self.drop_off_points is None:
            object.__setattr__(self, "drop_off_points", ())
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "timeline_seconds": list(self.timeline_seconds) if self.timeline_seconds else [],
            "retention_percentages": (
                list(self.retention_percentages) if self.retention_percentages else []
            ),
            "drop_off_points": list(self.drop_off_points) if self.drop_off_points else [],
            "peak_engagement_seconds": self.peak_engagement_seconds,
            "completion_rate": self.completion_rate,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class WatchTimeMetrics:
    """Watch time analysis."""

    video_id: str = ""
    total_watch_time_seconds: int = 0
    average_duration_seconds: float = 0.0
    median_duration_seconds: float = 0.0
    repeat_views: int = 0
    unique_viewers: int = 0
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "total_watch_time_seconds": self.total_watch_time_seconds,
            "average_duration_seconds": self.average_duration_seconds,
            "median_duration_seconds": self.median_duration_seconds,
            "repeat_views": self.repeat_views,
            "unique_viewers": self.unique_viewers,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class CTRMetrics:
    """Click-through rate metrics."""

    video_id: str = ""
    ctr: float = 0.0
    impressions: int = 0
    clicks: int = 0
    platform: str = ""
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "ctr": self.ctr,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "platform": self.platform,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class EngagementMetrics:
    """Engagement metrics."""

    video_id: str = ""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_score: float = 0.0
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "engagement_score": self.engagement_score,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class RevenueMetrics:
    """Revenue metrics."""

    video_id: str = ""
    revenue: float = 0.0
    rpm: float = 0.0
    views: int = 0
    platform: str = ""
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "video_id": self.video_id,
            "revenue": self.revenue,
            "rpm": self.rpm,
            "views": self.views,
            "platform": self.platform,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


# ============================================================================
# OPTIMIZATION RECOMMENDATIONS
# ============================================================================


@dataclass(frozen=True)
class OptimizationRecommendation:
    """Recommendation for video optimization."""

    id: str = ""
    recommendation_id: str = ""
    category: RecommendationCategory = RecommendationCategory.TITLE
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    confidence: LearningConfidence = LearningConfidence.MEDIUM
    expected_improvement: float = 0.0
    affected_component: str = ""
    reason: str = ""
    evidence: str = ""
    suggested_action: str = ""
    estimated_impact: str = ""
    learning_task_id: str | None = None
    timestamp: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if not self.recommendation_id:
            object.__setattr__(self, "recommendation_id", str(uuid4()))
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recommendation_id": self.recommendation_id,
            "category": self.category.value,
            "priority": self.priority.value,
            "confidence": self.confidence.value,
            "expected_improvement": self.expected_improvement,
            "affected_component": self.affected_component,
            "reason": self.reason,
            "evidence": self.evidence,
            "suggested_action": self.suggested_action,
            "estimated_impact": self.estimated_impact,
            "learning_task_id": self.learning_task_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ============================================================================
# LEARNING RESULTS
# ============================================================================


@dataclass(frozen=True)
class LearningResult:
    """Result of a learning task."""

    learning_task_id: str = ""
    success: bool = False
    metrics_collected: int = 0
    recommendations_generated: int = 0
    confidence_score: float = 0.0
    error_message: str | None = None
    result_data: dict = None
    created_at: datetime = None

    def __post_init__(self):
        if self.result_data is None:
            object.__setattr__(self, "result_data", {})
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "learning_task_id": self.learning_task_id,
            "success": self.success,
            "metrics_collected": self.metrics_collected,
            "recommendations_generated": self.recommendations_generated,
            "confidence_score": self.confidence_score,
            "error_message": self.error_message,
            "result_data": self.result_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass(frozen=True)
class LearningReport:
    """Report on learning progress."""

    learning_job_id: str = ""
    total_tasks: int = 0
    completed_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    recommendations_generated: int = 0
    average_confidence: float = 0.0
    top_categories: tuple[str, ...] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.top_categories is None:
            object.__setattr__(self, "top_categories", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "learning_job_id": self.learning_job_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "recommendations_generated": self.recommendations_generated,
            "average_confidence": self.average_confidence,
            "top_categories": list(self.top_categories) if self.top_categories else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# ANALYTICS REFERENCE (from M13)
# ============================================================================


@dataclass(frozen=True)
class AnalyticsReference:
    """Reference to analytics data from M13."""

    id: str = ""
    published_asset_id: str = ""
    platform: str = ""
    video_id: str = ""
    external_reference: str = ""
    metadata: dict = None
    created_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "published_asset_id": self.published_asset_id,
            "platform": self.platform,
            "video_id": self.video_id,
            "external_reference": self.external_reference,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# LEARNING OBJECTIVES
# ============================================================================


@dataclass(frozen=True)
class LearningObjective:
    """Learning objective for optimization."""

    objective_type: str = ""
    weight: float = 1.0
    target_value: float | None = None
    current_value: float = 0.0
    threshold: float = 0.0

    def to_dict(self) -> dict:
        return {
            "objective_type": self.objective_type,
            "weight": self.weight,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "threshold": self.threshold,
        }

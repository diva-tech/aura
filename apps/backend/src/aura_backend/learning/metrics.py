"""M14 Phase 1: Learning Foundation – Metrics Aggregations.

Aggregated metrics for learning and analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class MetricTrend:
    """Trend data for a single metric."""

    metric_name: str = ""
    timeline: tuple[datetime, ...] = None
    values: tuple[float, ...] = None
    trend_direction: str = ""  # up, down, flat
    trend_magnitude: float = 0.0
    confidence: float = 0.0

    def __post_init__(self):
        if self.timeline is None:
            object.__setattr__(self, "timeline", ())
        if self.values is None:
            object.__setattr__(self, "values", ())

    def to_dict(self) -> dict:
        return {
            "metric_name": self.metric_name,
            "timeline": [t.isoformat() for t in self.timeline] if self.timeline else [],
            "values": list(self.values) if self.values else [],
            "trend_direction": self.trend_direction,
            "trend_magnitude": self.trend_magnitude,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class PerformanceComparison:
    """Comparison between two periods or groups."""

    comparison_id: str = ""
    metric_name: str = ""
    period_1_name: str = ""
    period_1_value: float = 0.0
    period_2_name: str = ""
    period_2_value: float = 0.0
    change_percent: float = 0.0
    change_direction: str = ""  # positive, negative, neutral
    statistical_significance: float = 0.0
    sample_size_1: int = 0
    sample_size_2: int = 0

    def __post_init__(self):
        if not self.comparison_id:
            object.__setattr__(self, "comparison_id", str(uuid4()))

    def to_dict(self) -> dict:
        return {
            "comparison_id": self.comparison_id,
            "metric_name": self.metric_name,
            "period_1_name": self.period_1_name,
            "period_1_value": self.period_1_value,
            "period_2_name": self.period_2_name,
            "period_2_value": self.period_2_value,
            "change_percent": self.change_percent,
            "change_direction": self.change_direction,
            "statistical_significance": self.statistical_significance,
            "sample_size_1": self.sample_size_1,
            "sample_size_2": self.sample_size_2,
        }


@dataclass(frozen=True)
class CreatorMetricsSummary:
    """Summary of all metrics for a creator."""

    creator_id: str = ""
    period: str = ""  # e.g., "last_30_days", "last_90_days"
    total_videos: int = 0
    total_views: int = 0
    total_watch_time_hours: int = 0
    average_ctr: float = 0.0
    average_retention: float = 0.0
    average_engagement_rate: float = 0.0
    total_revenue: float = 0.0
    average_rpm: float = 0.0
    subscriber_growth: int = 0
    subscriber_growth_rate: float = 0.0
    top_performing_video_id: str | None = None
    top_performing_metric: str = ""
    top_performing_value: float = 0.0
    lowest_performing_video_id: str | None = None
    lowest_performing_metric: str = ""
    lowest_performing_value: float = 0.0
    created_at: datetime = None

    def __post_init__(self):
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "creator_id": self.creator_id,
            "period": self.period,
            "total_videos": self.total_videos,
            "total_views": self.total_views,
            "total_watch_time_hours": self.total_watch_time_hours,
            "average_ctr": self.average_ctr,
            "average_retention": self.average_retention,
            "average_engagement_rate": self.average_engagement_rate,
            "total_revenue": self.total_revenue,
            "average_rpm": self.average_rpm,
            "subscriber_growth": self.subscriber_growth,
            "subscriber_growth_rate": self.subscriber_growth_rate,
            "top_performing_video_id": self.top_performing_video_id,
            "top_performing_metric": self.top_performing_metric,
            "top_performing_value": self.top_performing_value,
            "lowest_performing_video_id": self.lowest_performing_video_id,
            "lowest_performing_metric": self.lowest_performing_metric,
            "lowest_performing_value": self.lowest_performing_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass(frozen=True)
class PlatformMetrics:
    """Performance metrics per platform."""

    platform: str = ""
    creator_id: str = ""
    total_videos: int = 0
    total_views: int = 0
    average_ctr: float = 0.0
    average_engagement_rate: float = 0.0
    subscriber_growth: int = 0
    revenue: float = 0.0
    best_performing_content_type: str = ""
    best_performing_length: str = ""
    best_posting_day: str = ""
    best_posting_time: str = ""
    created_at: datetime = None

    def __post_init__(self):
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "creator_id": self.creator_id,
            "total_videos": self.total_videos,
            "total_views": self.total_views,
            "average_ctr": self.average_ctr,
            "average_engagement_rate": self.average_engagement_rate,
            "subscriber_growth": self.subscriber_growth,
            "revenue": self.revenue,
            "best_performing_content_type": self.best_performing_content_type,
            "best_performing_length": self.best_performing_length,
            "best_posting_day": self.best_posting_day,
            "best_posting_time": self.best_posting_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

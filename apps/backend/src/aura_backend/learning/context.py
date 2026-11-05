"""M14 Phase 2: Analytics Providers – Learning Context and Capability.

Immutable models for provider execution context and capability declaration.
"""

from dataclasses import dataclass
from datetime import datetime

from .memory import LearningMemory
from .models import LearningObjective
from .profiles import CreatorProfile


@dataclass(frozen=True)
class LearningContext:
    """Execution context for analytics providers."""

    job_id: str = ""
    creator_id: str = ""
    creator_profile: CreatorProfile | None = None
    learning_memory: LearningMemory | None = None
    analytics_reference_id: str | None = None
    platform: str = ""
    objectives: tuple[LearningObjective, ...] = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    optimization_level: str = "standard"
    include_audience_insights: bool = True
    include_revenue_data: bool = True
    include_engagement_metrics: bool = True
    timezone: str = "UTC"
    created_at: datetime = None

    def __post_init__(self):
        if self.objectives is None:
            object.__setattr__(self, "objectives", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "creator_id": self.creator_id,
            "creator_profile": self.creator_profile.to_dict() if self.creator_profile else None,
            "learning_memory": self.learning_memory.to_dict() if self.learning_memory else None,
            "analytics_reference_id": self.analytics_reference_id,
            "platform": self.platform,
            "objectives": [o.to_dict() for o in self.objectives] if self.objectives else [],
            "time_window_start": (
                self.time_window_start.isoformat() if self.time_window_start else None
            ),
            "time_window_end": self.time_window_end.isoformat() if self.time_window_end else None,
            "optimization_level": self.optimization_level,
            "include_audience_insights": self.include_audience_insights,
            "include_revenue_data": self.include_revenue_data,
            "include_engagement_metrics": self.include_engagement_metrics,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass(frozen=True)
class AnalyticsCapability:
    """Capability declaration for analytics provider."""

    provider_name: str = ""
    supports_retention_analysis: bool = False
    supports_revenue_metrics: bool = False
    supports_audience_demographics: bool = False
    supports_ctr_metrics: bool = False
    supports_audience_segmentation: bool = False
    supports_search_terms: bool = False
    supports_comments_analysis: bool = False
    supports_live_metrics: bool = False
    supports_export: bool = False
    supported_formats: tuple[str, ...] = None
    max_lookback_days: int = 90
    max_results_per_request: int = 1000
    rate_limit_requests_per_minute: int = 60
    requires_authentication: bool = True
    supported_platforms: tuple[str, ...] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.supported_formats is None:
            object.__setattr__(self, "supported_formats", ())
        if self.supported_platforms is None:
            object.__setattr__(self, "supported_platforms", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def supports_feature(self, feature_name: str) -> bool:
        """Check if provider supports a feature."""
        feature_map = {
            "retention": self.supports_retention_analysis,
            "revenue": self.supports_revenue_metrics,
            "demographics": self.supports_audience_demographics,
            "ctr": self.supports_ctr_metrics,
            "segmentation": self.supports_audience_segmentation,
            "search_terms": self.supports_search_terms,
            "comments": self.supports_comments_analysis,
            "live_metrics": self.supports_live_metrics,
            "export": self.supports_export,
        }
        return feature_map.get(feature_name, False)

    def supports_format(self, format_name: str) -> bool:
        """Check if provider supports a format."""
        return format_name in self.supported_formats if self.supported_formats else False

    def supports_platform(self, platform_name: str) -> bool:
        """Check if provider supports a platform."""
        return platform_name in self.supported_platforms if self.supported_platforms else False

    def can_negotiate(self, required_features: tuple[str, ...]) -> bool:
        """Check if provider can satisfy all required features."""
        if not required_features:
            return True
        return all(self.supports_feature(f) for f in required_features)

    def to_dict(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "supports_retention_analysis": self.supports_retention_analysis,
            "supports_revenue_metrics": self.supports_revenue_metrics,
            "supports_audience_demographics": self.supports_audience_demographics,
            "supports_ctr_metrics": self.supports_ctr_metrics,
            "supports_audience_segmentation": self.supports_audience_segmentation,
            "supports_search_terms": self.supports_search_terms,
            "supports_comments_analysis": self.supports_comments_analysis,
            "supports_live_metrics": self.supports_live_metrics,
            "supports_export": self.supports_export,
            "supported_formats": list(self.supported_formats) if self.supported_formats else [],
            "max_lookback_days": self.max_lookback_days,
            "max_results_per_request": self.max_results_per_request,
            "rate_limit_requests_per_minute": self.rate_limit_requests_per_minute,
            "requires_authentication": self.requires_authentication,
            "supported_platforms": (
                list(self.supported_platforms) if self.supported_platforms else []
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

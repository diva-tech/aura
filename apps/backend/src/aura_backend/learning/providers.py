"""M14 Phase 2: Analytics Providers – Abstract Interface.

Abstract provider interface for analytics data retrieval.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .context import AnalyticsCapability, LearningContext
from .models import (
    CTRMetrics,
    EngagementMetrics,
    RetentionCurve,
    RevenueMetrics,
    VideoPerformance,
    WatchTimeMetrics,
)
from .profiles import AudienceProfile


@dataclass(frozen=True)
class AuthenticationResult:
    """Result of authentication attempt."""

    success: bool = False
    message: str = ""
    token: str | None = None
    expires_at: datetime | None = None
    error_code: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "token": self.token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "error_code": self.error_code,
        }


@dataclass(frozen=True)
class MetricsResult:
    """Result of metrics retrieval."""

    success: bool = False
    video_performance: VideoPerformance | None = None
    retention_curve: RetentionCurve | None = None
    watch_time_metrics: WatchTimeMetrics | None = None
    ctr_metrics: CTRMetrics | None = None
    engagement_metrics: EngagementMetrics | None = None
    revenue_metrics: RevenueMetrics | None = None
    error_message: str | None = None
    error_code: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "video_performance": (
                self.video_performance.to_dict() if self.video_performance else None
            ),
            "retention_curve": self.retention_curve.to_dict() if self.retention_curve else None,
            "watch_time_metrics": (
                self.watch_time_metrics.to_dict() if self.watch_time_metrics else None
            ),
            "ctr_metrics": self.ctr_metrics.to_dict() if self.ctr_metrics else None,
            "engagement_metrics": (
                self.engagement_metrics.to_dict() if self.engagement_metrics else None
            ),
            "revenue_metrics": self.revenue_metrics.to_dict() if self.revenue_metrics else None,
            "error_message": self.error_message,
            "error_code": self.error_code,
        }


@dataclass(frozen=True)
class AudienceResult:
    """Result of audience data retrieval."""

    success: bool = False
    audience_profile: AudienceProfile | None = None
    total_audience_size: int = 0
    error_message: str | None = None
    error_code: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "audience_profile": self.audience_profile.to_dict() if self.audience_profile else None,
            "total_audience_size": self.total_audience_size,
            "error_message": self.error_message,
            "error_code": self.error_code,
        }


class AnalyticsProvider(ABC):
    """Abstract analytics provider interface."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> AnalyticsCapability:
        """Provider capabilities."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available."""
        pass

    @abstractmethod
    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        """Authenticate with the provider."""
        pass

    @abstractmethod
    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        """Validate credentials."""
        pass

    @abstractmethod
    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        """Retrieve video performance metrics."""
        pass

    @abstractmethod
    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        """Retrieve retention curve data."""
        pass

    @abstractmethod
    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        """Retrieve audience data."""
        pass

    @abstractmethod
    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        """Retrieve revenue metrics."""
        pass

    @abstractmethod
    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        """Retrieve CTR metrics."""
        pass

    @abstractmethod
    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        """Export metrics in specified format."""
        pass

    @abstractmethod
    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        """Check if provider supports required features."""
        pass


class AnalyticsProviderRegistry:
    """Registry for analytics providers."""

    def __init__(self):
        self._providers = {}

    def register(self, provider: AnalyticsProvider) -> None:
        """Register a provider."""
        self._providers[provider.provider_name] = provider

    def get(self, provider_name: str) -> AnalyticsProvider | None:
        """Get a provider by name."""
        return self._providers.get(provider_name)

    def get_all(self) -> dict:
        """Get all registered providers."""
        return self._providers.copy()

    def list_providers(self) -> list:
        """List all provider names."""
        return list(self._providers.keys())

    def filter_by_capability(self, required_feature: str) -> list:
        """Filter providers by capability."""
        return [
            name
            for name, provider in self._providers.items()
            if provider.capabilities.supports_feature(required_feature)
        ]

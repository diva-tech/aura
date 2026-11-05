"""M14 Phase 2: Analytics Providers – Reference Implementations.

Six reference provider implementations (Mock, YouTube, TikTok, Instagram, LinkedIn, Podcast).
All stateless, async, capability-based.
"""

from datetime import datetime
from typing import Any

from .context import AnalyticsCapability, LearningContext
from .models import (
    CTRMetrics,
    RetentionCurve,
    RevenueMetrics,
    VideoPerformance,
)
from .profiles import AudienceProfile, AudienceSegment
from .providers import (
    AnalyticsProvider,
    AnalyticsProviderRegistry,
    AudienceResult,
    AuthenticationResult,
    MetricsResult,
)


class MockAnalyticsProvider(AnalyticsProvider):
    """Mock provider for testing."""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="mock",
            supports_retention_analysis=True,
            supports_revenue_metrics=True,
            supports_audience_demographics=True,
            supports_ctr_metrics=True,
            supports_audience_segmentation=True,
            supports_search_terms=False,
            supports_comments_analysis=True,
            supports_live_metrics=True,
            supports_export=True,
            supported_formats=("json", "csv"),
            max_lookback_days=90,
            max_results_per_request=1000,
            rate_limit_requests_per_minute=1000,
            requires_authentication=False,
            supported_platforms=("youtube", "tiktok", "instagram", "linkedin", "podcast"),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        return AuthenticationResult(
            success=True,
            message="Mock authentication successful",
        )

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return True

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=50000,
                unique_views=40000,
                watch_time_seconds=500000,
                average_view_duration_seconds=10.0,
                audience_retention=75.0,
                click_through_rate=5.5,
                likes=2500,
                comments=500,
                shares=200,
                subscribers_gained=1500,
                revenue=250.0,
                rpm=5.0,
                engagement_score=7.2,
                completion_rate=80.0,
                bounce_rate=15.0,
                conversion_rate=3.5,
                platform=context.platform,
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return RetentionCurve(
            video_id=video_id,
            timeline_seconds=(0, 30, 60, 120, 180, 300, 600),
            retention_percentages=(100, 85, 75, 65, 55, 45, 35),
            drop_off_points=(30, 60, 120),
            peak_engagement_seconds=30,
            completion_rate=80.0,
        )

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="Primary Audience",
            age_group="25-34",
            geography=("US", "UK", "Canada"),
            interests=("tech", "productivity", "business"),
            size_percent=60.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=50000,
                segments=(segment,),
                top_geographies=("US", "UK", "Canada"),
                top_interests=("tech", "productivity"),
            ),
            total_audience_size=50000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return RevenueMetrics(
            video_id=video_id or "unknown",
            revenue=250.0,
            rpm=5.0,
            views=50000,
            platform=context.platform,
        )

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return CTRMetrics(
            video_id=video_id,
            ctr=5.5,
            impressions=100000,
            clicks=5500,
            platform=context.platform,
        )

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {
            "format": format_type,
            "video_count": len(video_ids),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


class YouTubeAnalyticsProvider(AnalyticsProvider):
    """YouTube Analytics provider."""

    @property
    def provider_name(self) -> str:
        return "youtube"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="youtube",
            supports_retention_analysis=True,
            supports_revenue_metrics=True,
            supports_audience_demographics=True,
            supports_ctr_metrics=True,
            supports_audience_segmentation=True,
            supports_search_terms=True,
            supports_comments_analysis=True,
            supports_live_metrics=True,
            supports_export=True,
            supported_formats=("json", "csv", "xlsx"),
            max_lookback_days=365,
            max_results_per_request=500,
            rate_limit_requests_per_minute=100,
            requires_authentication=True,
            supported_platforms=("youtube",),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        if "api_key" not in credentials:
            return AuthenticationResult(
                success=False,
                message="Missing API key",
                error_code="MISSING_CREDENTIALS",
            )
        return AuthenticationResult(success=True, message="YouTube authentication successful")

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return "api_key" in credentials

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=100000,
                unique_views=85000,
                watch_time_seconds=1500000,
                average_view_duration_seconds=15.0,
                audience_retention=78.0,
                click_through_rate=4.2,
                likes=5000,
                comments=1200,
                shares=300,
                subscribers_gained=2500,
                revenue=500.0,
                rpm=5.0,
                engagement_score=7.8,
                completion_rate=85.0,
                bounce_rate=12.0,
                conversion_rate=2.5,
                platform="youtube",
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return RetentionCurve(
            video_id=video_id,
            timeline_seconds=(0, 30, 60, 120, 180, 300, 600),
            retention_percentages=(100, 88, 78, 68, 58, 48, 38),
            drop_off_points=(30, 60, 120),
            peak_engagement_seconds=45,
            completion_rate=85.0,
        )

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="YouTube Subscribers",
            age_group="18-44",
            geography=("US", "IN", "BR", "ID", "MX"),
            interests=("education", "entertainment", "tech"),
            size_percent=70.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=100000,
                segments=(segment,),
                top_geographies=("US", "IN", "BR"),
                top_interests=("education", "entertainment"),
            ),
            total_audience_size=100000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return RevenueMetrics(
            video_id=video_id or "unknown",
            revenue=500.0,
            rpm=5.0,
            views=100000,
            platform="youtube",
        )

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return CTRMetrics(
            video_id=video_id,
            ctr=4.2,
            impressions=500000,
            clicks=21000,
            platform="youtube",
        )

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {
            "format": format_type,
            "video_count": len(video_ids),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


class TikTokAnalyticsProvider(AnalyticsProvider):
    """TikTok Analytics provider."""

    @property
    def provider_name(self) -> str:
        return "tiktok"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="tiktok",
            supports_retention_analysis=False,
            supports_revenue_metrics=True,
            supports_audience_demographics=True,
            supports_ctr_metrics=False,
            supports_audience_segmentation=True,
            supports_search_terms=False,
            supports_comments_analysis=True,
            supports_live_metrics=True,
            supports_export=False,
            supported_formats=("json",),
            max_lookback_days=30,
            max_results_per_request=100,
            rate_limit_requests_per_minute=1000,
            requires_authentication=True,
            supported_platforms=("tiktok",),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        if "access_token" not in credentials:
            return AuthenticationResult(
                success=False,
                message="Missing access token",
                error_code="MISSING_CREDENTIALS",
            )
        return AuthenticationResult(success=True, message="TikTok authentication successful")

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return "access_token" in credentials

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=500000,
                unique_views=400000,
                watch_time_seconds=2000000,
                average_view_duration_seconds=4.0,
                audience_retention=60.0,
                click_through_rate=8.5,
                likes=25000,
                comments=5000,
                shares=2000,
                subscribers_gained=5000,
                revenue=100.0,
                rpm=0.2,
                engagement_score=8.5,
                completion_rate=60.0,
                bounce_rate=20.0,
                conversion_rate=1.5,
                platform="tiktok",
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return None

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="TikTok Followers",
            age_group="13-24",
            geography=("US", "CN", "BR", "IN"),
            interests=("entertainment", "dance", "comedy", "lifestyle"),
            size_percent=85.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=500000,
                segments=(segment,),
                top_geographies=("US", "CN", "BR"),
                top_interests=("entertainment", "dance"),
            ),
            total_audience_size=500000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return RevenueMetrics(
            video_id=video_id or "unknown",
            revenue=100.0,
            rpm=0.2,
            views=500000,
            platform="tiktok",
        )

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return None

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {"status": "error", "message": "TikTok does not support metrics export"}

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


class InstagramAnalyticsProvider(AnalyticsProvider):
    """Instagram Analytics provider."""

    @property
    def provider_name(self) -> str:
        return "instagram"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="instagram",
            supports_retention_analysis=False,
            supports_revenue_metrics=True,
            supports_audience_demographics=True,
            supports_ctr_metrics=False,
            supports_audience_segmentation=True,
            supports_search_terms=False,
            supports_comments_analysis=True,
            supports_live_metrics=False,
            supports_export=True,
            supported_formats=("json", "csv"),
            max_lookback_days=90,
            max_results_per_request=100,
            rate_limit_requests_per_minute=200,
            requires_authentication=True,
            supported_platforms=("instagram",),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        if "access_token" not in credentials:
            return AuthenticationResult(
                success=False,
                message="Missing access token",
                error_code="MISSING_CREDENTIALS",
            )
        return AuthenticationResult(success=True, message="Instagram authentication successful")

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return "access_token" in credentials

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=200000,
                unique_views=150000,
                watch_time_seconds=600000,
                average_view_duration_seconds=3.0,
                audience_retention=65.0,
                click_through_rate=3.5,
                likes=10000,
                comments=2000,
                shares=500,
                subscribers_gained=1000,
                revenue=80.0,
                rpm=0.4,
                engagement_score=6.5,
                completion_rate=65.0,
                bounce_rate=25.0,
                conversion_rate=1.0,
                platform="instagram",
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return None

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="Instagram Followers",
            age_group="18-35",
            geography=("US", "BR", "MX", "FR"),
            interests=("lifestyle", "fashion", "beauty", "fitness"),
            size_percent=75.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=200000,
                segments=(segment,),
                top_geographies=("US", "BR", "MX"),
                top_interests=("lifestyle", "fashion"),
            ),
            total_audience_size=200000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return RevenueMetrics(
            video_id=video_id or "unknown",
            revenue=80.0,
            rpm=0.4,
            views=200000,
            platform="instagram",
        )

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return None

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {
            "format": format_type,
            "video_count": len(video_ids),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


class LinkedInAnalyticsProvider(AnalyticsProvider):
    """LinkedIn Analytics provider."""

    @property
    def provider_name(self) -> str:
        return "linkedin"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="linkedin",
            supports_retention_analysis=False,
            supports_revenue_metrics=False,
            supports_audience_demographics=True,
            supports_ctr_metrics=False,
            supports_audience_segmentation=True,
            supports_search_terms=False,
            supports_comments_analysis=True,
            supports_live_metrics=False,
            supports_export=True,
            supported_formats=("json", "csv"),
            max_lookback_days=180,
            max_results_per_request=100,
            rate_limit_requests_per_minute=100,
            requires_authentication=True,
            supported_platforms=("linkedin",),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        if "access_token" not in credentials:
            return AuthenticationResult(
                success=False,
                message="Missing access token",
                error_code="MISSING_CREDENTIALS",
            )
        return AuthenticationResult(success=True, message="LinkedIn authentication successful")

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return "access_token" in credentials

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=50000,
                unique_views=40000,
                watch_time_seconds=300000,
                average_view_duration_seconds=6.0,
                audience_retention=70.0,
                click_through_rate=2.5,
                likes=2000,
                comments=500,
                shares=200,
                subscribers_gained=500,
                revenue=0.0,
                rpm=0.0,
                engagement_score=6.0,
                completion_rate=70.0,
                bounce_rate=20.0,
                conversion_rate=2.0,
                platform="linkedin",
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return None

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="LinkedIn Followers",
            age_group="25-55",
            geography=("US", "UK", "CA", "AU"),
            interests=("business", "technology", "career", "innovation"),
            size_percent=90.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=50000,
                segments=(segment,),
                top_geographies=("US", "UK", "CA"),
                top_interests=("business", "technology"),
            ),
            total_audience_size=50000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return None

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return None

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {
            "format": format_type,
            "video_count": len(video_ids),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


class PodcastAnalyticsProvider(AnalyticsProvider):
    """Podcast Analytics provider."""

    @property
    def provider_name(self) -> str:
        return "podcast"

    @property
    def capabilities(self) -> AnalyticsCapability:
        return AnalyticsCapability(
            provider_name="podcast",
            supports_retention_analysis=False,
            supports_revenue_metrics=True,
            supports_audience_demographics=True,
            supports_ctr_metrics=False,
            supports_audience_segmentation=True,
            supports_search_terms=False,
            supports_comments_analysis=False,
            supports_live_metrics=False,
            supports_export=True,
            supported_formats=("json", "csv"),
            max_lookback_days=365,
            max_results_per_request=500,
            rate_limit_requests_per_minute=500,
            requires_authentication=True,
            supported_platforms=("podcast",),
        )

    async def is_available(self) -> bool:
        return True

    async def authenticate(self, credentials: dict[str, Any]) -> AuthenticationResult:
        if "api_key" not in credentials:
            return AuthenticationResult(
                success=False,
                message="Missing API key",
                error_code="MISSING_CREDENTIALS",
            )
        return AuthenticationResult(success=True, message="Podcast authentication successful")

    async def validate_credentials(self, credentials: dict[str, Any]) -> bool:
        return "api_key" in credentials

    async def get_video_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> MetricsResult:
        return MetricsResult(
            success=True,
            video_performance=VideoPerformance(
                video_id=video_id,
                views=10000,
                unique_views=8000,
                watch_time_seconds=600000,
                average_view_duration_seconds=60.0,
                audience_retention=85.0,
                click_through_rate=0.0,
                likes=500,
                comments=100,
                shares=50,
                subscribers_gained=200,
                revenue=500.0,
                rpm=50.0,
                engagement_score=7.0,
                completion_rate=85.0,
                bounce_rate=10.0,
                conversion_rate=0.5,
                platform="podcast",
            ),
        )

    async def get_retention_curve(
        self,
        context: LearningContext,
        video_id: str,
    ) -> RetentionCurve | None:
        return None

    async def get_audience_data(
        self,
        context: LearningContext,
    ) -> AudienceResult:
        segment = AudienceSegment(
            segment_name="Podcast Listeners",
            age_group="25-54",
            geography=("US", "UK", "CA", "AU", "DE"),
            interests=("education", "news", "business", "health"),
            size_percent=95.0,
        )
        return AudienceResult(
            success=True,
            audience_profile=AudienceProfile(
                creator_id=context.creator_id,
                total_subscribers=100000,
                segments=(segment,),
                top_geographies=("US", "UK", "CA"),
                top_interests=("education", "news"),
            ),
            total_audience_size=100000,
        )

    async def get_revenue_data(
        self,
        context: LearningContext,
        video_id: str | None = None,
    ) -> RevenueMetrics | None:
        return RevenueMetrics(
            video_id=video_id or "unknown",
            revenue=500.0,
            rpm=50.0,
            views=10000,
            platform="podcast",
        )

    async def get_ctr_metrics(
        self,
        context: LearningContext,
        video_id: str,
    ) -> CTRMetrics | None:
        return None

    async def export_metrics(
        self,
        context: LearningContext,
        video_ids: tuple,
        format_type: str = "json",
    ) -> dict[str, Any]:
        return {
            "format": format_type,
            "episode_count": len(video_ids),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
        }

    async def check_capability_support(
        self,
        required_features: tuple,
    ) -> bool:
        return self.capabilities.can_negotiate(required_features)


def create_default_provider_registry() -> AnalyticsProviderRegistry:
    """Create registry with all reference providers."""
    registry = AnalyticsProviderRegistry()
    registry.register(MockAnalyticsProvider())
    registry.register(YouTubeAnalyticsProvider())
    registry.register(TikTokAnalyticsProvider())
    registry.register(InstagramAnalyticsProvider())
    registry.register(LinkedInAnalyticsProvider())
    registry.register(PodcastAnalyticsProvider())
    return registry

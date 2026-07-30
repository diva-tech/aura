"""Milestone 14: Learning & Optimization Engine.

Phase 1: Learning Foundation
- Domain models for learning jobs, tasks, metrics, profiles
- Creator and audience profile tracking
- Learning memory and optimization knowledge
- Recommendations and performance analysis
- Learning manifest for complete context

Phase 2: Analytics Providers
- Learning context and analytics capability models
- Abstract provider interface with async methods
- Six reference provider implementations
- Provider registry for discovery and selection
"""

from .backends import (
    InstagramAnalyticsProvider,
    LinkedInAnalyticsProvider,
    MockAnalyticsProvider,
    PodcastAnalyticsProvider,
    TikTokAnalyticsProvider,
    YouTubeAnalyticsProvider,
    create_default_provider_registry,
)
from .context import AnalyticsCapability, LearningContext
from .manifest import LearningManifest
from .memory import (
    ConfidenceHistory,
    ExperimentRecord,
    FeatureImportance,
    LearningMemory,
    OptimizationHistory,
    RecommendationAcceptance,
)
from .metrics import (
    CreatorMetricsSummary,
    MetricTrend,
    PerformanceComparison,
    PlatformMetrics,
)
from .models import (
    AnalyticsReference,
    CTRMetrics,
    EngagementMetrics,
    LearningConfidence,
    LearningJob,
    LearningObjective,
    LearningPriority,
    LearningReport,
    LearningResult,
    LearningStatus,
    LearningTask,
    OptimizationRecommendation,
    PerformanceMetric,
    RecommendationCategory,
    RecommendationPriority,
    RetentionCurve,
    RevenueMetrics,
    VideoPerformance,
    WatchTimeMetrics,
)
from .profiles import (
    AudienceProfile,
    AudienceSegment,
    CreatorPreference,
    CreatorProfile,
    EditingStyle,
    StyleCategory,
    VideoLengthPreference,
)
from .providers import (
    AnalyticsProvider,
    AnalyticsProviderRegistry,
    AudienceResult,
    AuthenticationResult,
    MetricsResult,
)
from .recommendations import (
    CategoryRecommendations,
    RecommendationBatch,
    RecommendationSummary,
)

__all__ = [
    # Phase 2: Analytics Providers
    "LearningContext",
    "AnalyticsCapability",
    "AnalyticsProvider",
    "AnalyticsProviderRegistry",
    "AuthenticationResult",
    "AudienceResult",
    "MetricsResult",
    "MockAnalyticsProvider",
    "YouTubeAnalyticsProvider",
    "TikTokAnalyticsProvider",
    "InstagramAnalyticsProvider",
    "LinkedInAnalyticsProvider",
    "PodcastAnalyticsProvider",
    "create_default_provider_registry",
    # Enums
    "LearningStatus",
    "LearningPriority",
    "RecommendationPriority",
    "RecommendationCategory",
    "LearningConfidence",
    "VideoLengthPreference",
    "StyleCategory",
    "EditingStyle",
    # Models
    "LearningJob",
    "LearningTask",
    "LearningObjective",
    "PerformanceMetric",
    "VideoPerformance",
    "RetentionCurve",
    "WatchTimeMetrics",
    "CTRMetrics",
    "EngagementMetrics",
    "RevenueMetrics",
    "OptimizationRecommendation",
    "LearningResult",
    "LearningReport",
    "AnalyticsReference",
    # Profiles
    "CreatorProfile",
    "CreatorPreference",
    "AudienceProfile",
    "AudienceSegment",
    # Memory
    "LearningMemory",
    "FeatureImportance",
    "RecommendationAcceptance",
    "ExperimentRecord",
    "OptimizationHistory",
    "ConfidenceHistory",
    # Recommendations
    "RecommendationBatch",
    "CategoryRecommendations",
    "RecommendationSummary",
    # Metrics
    "MetricTrend",
    "PerformanceComparison",
    "CreatorMetricsSummary",
    "PlatformMetrics",
    # Manifest
    "LearningManifest",
]

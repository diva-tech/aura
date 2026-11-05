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

Phase 3: Learning Orchestration
- Learning stage and failure models
- DAG-based planning with M8 integration
- Seven M6 learning agents
- Lifecycle events and metrics

Phase 4: Production Readiness
- Learning dashboard for operational monitoring
- Operational metrics aggregation
- Performance optimization strategies
- Integration tests and benchmarks
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
from .dashboard import (
    AnalyticsProgress,
    CreatorProfileEvolution,
    LearningDashboard,
    LearningQueueItem,
    MemoryStatistics,
    ProviderHealth,
    ProviderHealthStatus,
    RecommendationSummary,
)
from .events import (
    LearningCompleted,
    LearningEvent,
    LearningMetricsEvent,
    LearningStarted,
    StageCompleted,
    StageFailed,
    StageStarted,
)
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
from .operational_metrics import (
    ConfidenceDistribution,
    LearningThroughputMetric,
    ObjectiveCompletionMetric,
    OperationalMetricsAggregator,
    ProviderLatencyMetric,
    RecommendationMetric,
    StageDurationMetric,
)
from .optimizer import (
    CapabilityBasedProviderSelector,
    ParallelAnalyticsCollector,
    QueueOptimizer,
    RecommendationCacheEntry,
    RecommendationCacheManager,
    RetryOptimizer,
)
from .orchestration import (
    AnalysisAgent,
    AuthenticationAgent,
    LearningAgent,
    LearningAgentRegistry,
    LearningPlanner,
    MemoryUpdateAgent,
    MetricsRetrievalAgent,
    ProfileUpdateAgent,
    RecommendationAgent,
    ValidationAgent,
    create_default_learning_agent_registry,
)
from .orchestration import LearningTask as M8LearningTask
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
)
from .stages import LearningFailure, LearningStage, LearningStageStatus, StageType

__all__ = [
    # Phase 4: Production Readiness
    "LearningDashboard",
    "LearningQueueItem",
    "AnalyticsProgress",
    "ProviderHealth",
    "ProviderHealthStatus",
    "RecommendationSummary",
    "CreatorProfileEvolution",
    "MemoryStatistics",
    "OperationalMetricsAggregator",
    "StageDurationMetric",
    "ProviderLatencyMetric",
    "RecommendationMetric",
    "ConfidenceDistribution",
    "ObjectiveCompletionMetric",
    "LearningThroughputMetric",
    "CapabilityBasedProviderSelector",
    "RecommendationCacheManager",
    "RecommendationCacheEntry",
    "QueueOptimizer",
    "RetryOptimizer",
    "ParallelAnalyticsCollector",
    # Phase 3: Learning Orchestration
    "LearningStage",
    "LearningStageStatus",
    "StageType",
    "LearningFailure",
    "LearningEvent",
    "LearningStarted",
    "StageStarted",
    "StageCompleted",
    "StageFailed",
    "LearningCompleted",
    "LearningMetricsEvent",
    "M8LearningTask",
    "LearningAgent",
    "ValidationAgent",
    "AuthenticationAgent",
    "MetricsRetrievalAgent",
    "AnalysisAgent",
    "RecommendationAgent",
    "ProfileUpdateAgent",
    "MemoryUpdateAgent",
    "LearningAgentRegistry",
    "LearningPlanner",
    "create_default_learning_agent_registry",
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

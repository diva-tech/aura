"""Milestone 14: Learning & Optimization Engine.

Phase 1: Learning Foundation
- Domain models for learning jobs, tasks, metrics, profiles
- Creator and audience profile tracking
- Learning memory and optimization knowledge
- Recommendations and performance analysis
- Learning manifest for complete context
"""

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
from .recommendations import (
    CategoryRecommendations,
    RecommendationBatch,
    RecommendationSummary,
)

__all__ = [
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

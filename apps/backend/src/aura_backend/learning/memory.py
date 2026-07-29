"""M14 Phase 1: Learning Foundation – Learning Memory.

Immutable model for tracking learning history and optimization knowledge.
NOT conversational memory - stores optimization knowledge only.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class FeatureImportance:
    """Importance score for a feature."""

    feature_name: str = ""
    importance_score: float = 0.0
    rank: int = 0
    confidence: float = 0.0
    last_updated: datetime = None

    def __post_init__(self):
        if not self.last_updated:
            object.__setattr__(self, "last_updated", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "feature_name": self.feature_name,
            "importance_score": self.importance_score,
            "rank": self.rank,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


@dataclass(frozen=True)
class RecommendationAcceptance:
    """Record of a recommendation acceptance/rejection."""

    recommendation_id: str = ""
    category: str = ""
    accepted: bool = False
    impact_on_performance: float = 0.0
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    recorded_at: datetime = None

    def __post_init__(self):
        if not self.recorded_at:
            object.__setattr__(self, "recorded_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "recommendation_id": self.recommendation_id,
            "category": self.category,
            "accepted": self.accepted,
            "impact_on_performance": self.impact_on_performance,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


@dataclass(frozen=True)
class ExperimentRecord:
    """Record of an optimization experiment."""

    experiment_id: str = ""
    category: str = ""
    hypothesis: str = ""
    control_videos: tuple[str, ...] = None
    variant_videos: tuple[str, ...] = None
    metric_tracked: str = ""
    control_performance: float = 0.0
    variant_performance: float = 0.0
    improvement_percent: float = 0.0
    statistically_significant: bool = False
    started_at: datetime = None
    completed_at: datetime | None = None

    def __post_init__(self):
        if self.control_videos is None:
            object.__setattr__(self, "control_videos", ())
        if self.variant_videos is None:
            object.__setattr__(self, "variant_videos", ())
        if not self.started_at:
            object.__setattr__(self, "started_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "category": self.category,
            "hypothesis": self.hypothesis,
            "control_videos": list(self.control_videos) if self.control_videos else [],
            "variant_videos": list(self.variant_videos) if self.variant_videos else [],
            "metric_tracked": self.metric_tracked,
            "control_performance": self.control_performance,
            "variant_performance": self.variant_performance,
            "improvement_percent": self.improvement_percent,
            "statistically_significant": self.statistically_significant,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass(frozen=True)
class OptimizationHistory:
    """History of optimizations applied."""

    optimization_id: str = ""
    category: str = ""
    action_taken: str = ""
    videos_applied_to: tuple[str, ...] = None
    performance_before: float = 0.0
    performance_after: float = 0.0
    improvement_percent: float = 0.0
    applied_at: datetime = None

    def __post_init__(self):
        if not self.optimization_id:
            object.__setattr__(self, "optimization_id", str(uuid4()))
        if self.videos_applied_to is None:
            object.__setattr__(self, "videos_applied_to", ())
        if not self.applied_at:
            object.__setattr__(self, "applied_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "optimization_id": self.optimization_id,
            "category": self.category,
            "action_taken": self.action_taken,
            "videos_applied_to": list(self.videos_applied_to) if self.videos_applied_to else [],
            "performance_before": self.performance_before,
            "performance_after": self.performance_after,
            "improvement_percent": self.improvement_percent,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
        }


@dataclass(frozen=True)
class ConfidenceHistory:
    """History of confidence scores over time."""

    category: str = ""
    timeline: tuple[datetime, ...] = None
    confidence_scores: tuple[float, ...] = None
    sample_counts: tuple[int, ...] = None

    def __post_init__(self):
        if self.timeline is None:
            object.__setattr__(self, "timeline", ())
        if self.confidence_scores is None:
            object.__setattr__(self, "confidence_scores", ())
        if self.sample_counts is None:
            object.__setattr__(self, "sample_counts", ())

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "timeline": [t.isoformat() for t in self.timeline] if self.timeline else [],
            "confidence_scores": list(self.confidence_scores) if self.confidence_scores else [],
            "sample_counts": list(self.sample_counts) if self.sample_counts else [],
        }


@dataclass(frozen=True)
class LearningMemory:
    """Immutable learning memory for a creator."""

    id: str = ""
    creator_id: str = ""
    memory_version: int = 1
    historical_performance: tuple[dict, ...] = None
    previous_recommendations: tuple[str, ...] = None
    accepted_recommendations: tuple[RecommendationAcceptance, ...] = None
    rejected_recommendations: tuple[RecommendationAcceptance, ...] = None
    feature_importance: tuple[FeatureImportance, ...] = None
    confidence_history: tuple[ConfidenceHistory, ...] = None
    optimization_history: tuple[OptimizationHistory, ...] = None
    experiment_history: tuple[ExperimentRecord, ...] = None
    total_videos_analyzed: int = 0
    total_recommendations_made: int = 0
    total_recommendations_accepted: int = 0
    acceptance_rate: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.historical_performance is None:
            object.__setattr__(self, "historical_performance", ())
        if self.previous_recommendations is None:
            object.__setattr__(self, "previous_recommendations", ())
        if self.accepted_recommendations is None:
            object.__setattr__(self, "accepted_recommendations", ())
        if self.rejected_recommendations is None:
            object.__setattr__(self, "rejected_recommendations", ())
        if self.feature_importance is None:
            object.__setattr__(self, "feature_importance", ())
        if self.confidence_history is None:
            object.__setattr__(self, "confidence_history", ())
        if self.optimization_history is None:
            object.__setattr__(self, "optimization_history", ())
        if self.experiment_history is None:
            object.__setattr__(self, "experiment_history", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "memory_version": self.memory_version,
            "historical_performance": (
                list(self.historical_performance) if self.historical_performance else []
            ),
            "previous_recommendations": (
                list(self.previous_recommendations) if self.previous_recommendations else []
            ),
            "accepted_recommendations": (
                [r.to_dict() for r in self.accepted_recommendations]
                if self.accepted_recommendations
                else []
            ),
            "rejected_recommendations": (
                [r.to_dict() for r in self.rejected_recommendations]
                if self.rejected_recommendations
                else []
            ),
            "feature_importance": (
                [f.to_dict() for f in self.feature_importance] if self.feature_importance else []
            ),
            "confidence_history": (
                [c.to_dict() for c in self.confidence_history] if self.confidence_history else []
            ),
            "optimization_history": (
                [o.to_dict() for o in self.optimization_history]
                if self.optimization_history
                else []
            ),
            "experiment_history": (
                [e.to_dict() for e in self.experiment_history] if self.experiment_history else []
            ),
            "total_videos_analyzed": self.total_videos_analyzed,
            "total_recommendations_made": self.total_recommendations_made,
            "total_recommendations_accepted": self.total_recommendations_accepted,
            "acceptance_rate": self.acceptance_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

"""M14 Phase 1: Learning Foundation – Learning Manifest.

Immutable manifest containing all learning-related artifacts.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .memory import LearningMemory
from .models import (
    AnalyticsReference,
    LearningJob,
    LearningObjective,
    LearningReport,
    LearningTask,
    OptimizationRecommendation,
)
from .profiles import AudienceProfile, CreatorProfile


@dataclass(frozen=True)
class LearningManifest:
    """Complete manifest of learning artifacts."""

    id: str = ""
    manifest_version: int = 1
    learning_job: LearningJob | None = None
    learning_tasks: tuple[LearningTask, ...] = None
    creator_profile: CreatorProfile | None = None
    audience_profile: AudienceProfile | None = None
    learning_memory: LearningMemory | None = None
    optimization_recommendations: tuple[OptimizationRecommendation, ...] = None
    learning_reports: tuple[LearningReport, ...] = None
    learning_objectives: tuple[LearningObjective, ...] = None
    analytics_references: tuple[AnalyticsReference, ...] = None
    performance_metrics: tuple[dict, ...] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.learning_tasks is None:
            object.__setattr__(self, "learning_tasks", ())
        if self.optimization_recommendations is None:
            object.__setattr__(self, "optimization_recommendations", ())
        if self.learning_reports is None:
            object.__setattr__(self, "learning_reports", ())
        if self.learning_objectives is None:
            object.__setattr__(self, "learning_objectives", ())
        if self.analytics_references is None:
            object.__setattr__(self, "analytics_references", ())
        if self.performance_metrics is None:
            object.__setattr__(self, "performance_metrics", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", datetime.utcnow())

    def get_learning_job_id(self) -> str | None:
        """Get learning job ID if available."""
        return self.learning_job.id if self.learning_job else None

    def get_creator_id(self) -> str | None:
        """Get creator ID if available."""
        if self.learning_job:
            return self.learning_job.creator_id
        if self.creator_profile:
            return self.creator_profile.creator_id
        return None

    def get_task_count(self) -> int:
        """Get count of learning tasks."""
        return len(self.learning_tasks) if self.learning_tasks else 0

    def get_recommendation_count(self) -> int:
        """Get count of recommendations."""
        return len(self.optimization_recommendations) if self.optimization_recommendations else 0

    def filter_tasks_by_status(self, status: str) -> tuple[LearningTask, ...]:
        """Filter tasks by status."""
        if not self.learning_tasks:
            return ()
        return tuple(t for t in self.learning_tasks if t.status == status)

    def filter_recommendations_by_priority(
        self, priority: str
    ) -> tuple[OptimizationRecommendation, ...]:
        """Filter recommendations by priority."""
        if not self.optimization_recommendations:
            return ()
        return tuple(r for r in self.optimization_recommendations if r.priority == priority)

    def filter_recommendations_by_category(
        self, category: str
    ) -> tuple[OptimizationRecommendation, ...]:
        """Filter recommendations by category."""
        if not self.optimization_recommendations:
            return ()
        return tuple(r for r in self.optimization_recommendations if r.category == category)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "manifest_version": self.manifest_version,
            "learning_job": self.learning_job.to_dict() if self.learning_job else None,
            "learning_tasks": (
                [t.to_dict() for t in self.learning_tasks] if self.learning_tasks else []
            ),
            "creator_profile": self.creator_profile.to_dict() if self.creator_profile else None,
            "audience_profile": self.audience_profile.to_dict() if self.audience_profile else None,
            "learning_memory": self.learning_memory.to_dict() if self.learning_memory else None,
            "optimization_recommendations": (
                [r.to_dict() for r in self.optimization_recommendations]
                if self.optimization_recommendations
                else []
            ),
            "learning_reports": (
                [r.to_dict() for r in self.learning_reports] if self.learning_reports else []
            ),
            "learning_objectives": (
                [o.to_dict() for o in self.learning_objectives] if self.learning_objectives else []
            ),
            "analytics_references": (
                [a.to_dict() for a in self.analytics_references]
                if self.analytics_references
                else []
            ),
            "performance_metrics": (
                list(self.performance_metrics) if self.performance_metrics else []
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

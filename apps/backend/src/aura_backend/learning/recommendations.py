"""M14 Phase 1: Learning Foundation – Recommendations.

Recommendation collections and aggregations.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .models import OptimizationRecommendation, RecommendationCategory


@dataclass(frozen=True)
class RecommendationBatch:
    """A batch of recommendations for a single video."""

    id: str = ""
    video_id: str = ""
    published_asset_id: str = ""
    recommendations: tuple[OptimizationRecommendation, ...] = None
    total_expected_improvement: float = 0.0
    average_confidence: float = 0.0
    batch_created_at: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.recommendations is None:
            object.__setattr__(self, "recommendations", ())
        if not self.batch_created_at:
            object.__setattr__(self, "batch_created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "video_id": self.video_id,
            "published_asset_id": self.published_asset_id,
            "recommendations": (
                [r.to_dict() for r in self.recommendations] if self.recommendations else []
            ),
            "total_expected_improvement": self.total_expected_improvement,
            "average_confidence": self.average_confidence,
            "batch_created_at": (
                self.batch_created_at.isoformat() if self.batch_created_at else None
            ),
        }


@dataclass(frozen=True)
class CategoryRecommendations:
    """Recommendations grouped by category."""

    category: RecommendationCategory = RecommendationCategory.TITLE
    recommendations: tuple[OptimizationRecommendation, ...] = None
    count: int = 0
    average_priority: str = ""
    average_confidence: float = 0.0
    total_expected_improvement: float = 0.0

    def __post_init__(self):
        if self.recommendations is None:
            object.__setattr__(self, "recommendations", ())

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "recommendations": (
                [r.to_dict() for r in self.recommendations] if self.recommendations else []
            ),
            "count": self.count,
            "average_priority": self.average_priority,
            "average_confidence": self.average_confidence,
            "total_expected_improvement": self.total_expected_improvement,
        }


@dataclass(frozen=True)
class RecommendationSummary:
    """Summary of recommendations."""

    creator_id: str = ""
    total_recommendations: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0
    top_categories: tuple[RecommendationCategory, ...] = None
    average_expected_improvement: float = 0.0
    estimated_performance_uplift: float = 0.0
    created_at: datetime = None

    def __post_init__(self):
        if self.top_categories is None:
            object.__setattr__(self, "top_categories", ())
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "creator_id": self.creator_id,
            "total_recommendations": self.total_recommendations,
            "high_priority_count": self.high_priority_count,
            "medium_priority_count": self.medium_priority_count,
            "low_priority_count": self.low_priority_count,
            "high_confidence_count": self.high_confidence_count,
            "medium_confidence_count": self.medium_confidence_count,
            "low_confidence_count": self.low_confidence_count,
            "top_categories": [c.value for c in self.top_categories] if self.top_categories else [],
            "average_expected_improvement": self.average_expected_improvement,
            "estimated_performance_uplift": self.estimated_performance_uplift,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

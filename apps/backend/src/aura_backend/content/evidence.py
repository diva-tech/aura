"""Content evidence and score cards for explainability.

Tracks which observations supported each discovery and detailed scoring breakdown.
Every intelligence component produces immutable evidence artifacts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .scoring import ScoringDimension, ScoringResult


@dataclass(frozen=True)
class ContentEvidence:
    """Immutable evidence backing a content discovery.

    Provides traceability from final content object back to source observations.
    Enables audit trail and explainability.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # What this evidence supports
    discovery_type: str = ""  # "story", "highlight", "hook", "chapter", "topic", "quote", "recommendation"
    discovery_id: str = ""  # ID of Story, Highlight, etc.

    # Source observations
    observation_ids: List[str] = field(default_factory=list)

    # Evidence breakdown by type
    observation_types_used: List[str] = field(default_factory=list)  # ["SPEECH", "OBJECT", ...]

    # Confidence in evidence
    evidence_quality: float = 0.5  # 0-1: how strong/direct is the evidence
    coverage_percentage: float = 0.0  # % of discovery supported by observations

    # Supporting details
    summary: str = ""  # Brief explanation of evidence
    reasoning: str = ""  # Why these observations support the discovery

    # Analysis context
    analysis_method: str = ""  # Which engine/strategy produced this
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "discovery_type": self.discovery_type,
            "discovery_id": self.discovery_id,
            "observation_count": len(self.observation_ids),
            "observation_types": self.observation_types_used,
            "evidence_quality": self.evidence_quality,
            "coverage_percentage": self.coverage_percentage,
            "summary": self.summary,
            "analysis_method": self.analysis_method,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ScoreCard:
    """Immutable scorecard tracking all scoring decisions.

    Provides complete transparency into how final scores were computed.
    Each intelligence component produces a scorecard explaining its output.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    # What this card scores
    target_type: str = ""  # "story", "highlight", "hook", "chapter", "topic", "quote", "recommendation"
    target_id: str = ""  # ID of the scored object

    # Final scores
    final_score: float = 0.5  # 0-1 composite score
    final_confidence: float = 0.5  # 0-1 confidence in final score

    # Dimension scores
    dimension_scores: Dict[ScoringDimension, float] = field(default_factory=dict)  # Dimension → score
    dimension_confidences: Dict[ScoringDimension, float] = field(default_factory=dict)  # Dimension → confidence

    # Dimension reasoning
    dimension_reasoning: Dict[ScoringDimension, str] = field(default_factory=dict)  # Dimension → why

    # Aggregation method
    aggregation_strategy: str = "confidence_weighted"  # How dimensions were combined
    dimension_weights: Dict[ScoringDimension, float] = field(default_factory=dict)  # Custom weights used

    # Component scores (for multi-component discoveries)
    component_scores: Dict[str, float] = field(default_factory=dict)  # Component name → score

    # Contributing observations
    observation_ids: List[str] = field(default_factory=list)

    # Analysis metadata
    analysis_engine: str = ""  # Which engine produced this scorecard
    analysis_version: str = "1.0"

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        dimension_scores_dict = {
            str(dim): score for dim, score in self.dimension_scores.items()
        }
        dimension_confidences_dict = {
            str(dim): conf for dim, conf in self.dimension_confidences.items()
        }
        dimension_reasoning_dict = {
            str(dim): reason for dim, reason in self.dimension_reasoning.items()
        }
        dimension_weights_dict = {
            str(dim): weight for dim, weight in self.dimension_weights.items()
        }

        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "final_score": self.final_score,
            "final_confidence": self.final_confidence,
            "dimension_count": len(self.dimension_scores),
            "dimension_scores": dimension_scores_dict,
            "dimension_confidences": dimension_confidences_dict,
            "aggregation_strategy": self.aggregation_strategy,
            "analysis_engine": self.analysis_engine,
            "observation_count": len(self.observation_ids),
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class AnalysisOutput:
    """Immutable output from an intelligence engine.

    Bundles the discovered content object, evidence, and scorecard.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    video_id: str = ""

    engine_name: str = ""  # Name of engine that produced this
    output_type: str = ""  # "story", "highlight", "hook", "chapter", "topic", "quote", "recommendation"

    # Primary output (serialized to dict for flexibility)
    output_data: Dict[str, Any] = field(default_factory=dict)

    # Supporting evidence and scoring
    evidence: Optional[ContentEvidence] = None
    scorecard: Optional[ScoreCard] = None

    # Quality metrics
    is_confident: bool = True
    requires_review: bool = False
    review_reason: str = ""  # Why this needs review

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_id": self.video_id,
            "engine_name": self.engine_name,
            "output_type": self.output_type,
            "output_data": self.output_data,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "scorecard": self.scorecard.to_dict() if self.scorecard else None,
            "is_confident": self.is_confident,
            "requires_review": self.requires_review,
            "review_reason": self.review_reason,
            "created_at": self.created_at.isoformat(),
        }

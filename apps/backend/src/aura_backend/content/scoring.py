"""Pluggable scoring framework for content intelligence.

Separates scoring concerns from analysis engines, allowing independent
tuning and composition of scoring strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ScoringDimension(StrEnum):
    """Available scoring dimensions"""

    IMPORTANCE = "importance"
    EMOTION = "emotion"
    NOVELTY = "novelty"
    ENGAGEMENT = "engagement"
    SPEECH_QUALITY = "speech_quality"
    VISUAL_QUALITY = "visual_quality"
    TOPIC_STRENGTH = "topic_strength"
    CONFIDENCE = "confidence"
    HOOK_EFFECTIVENESS = "hook_effectiveness"
    RECOMMENDATION_SCORE = "recommendation_score"


@dataclass(frozen=True)
class ScoringResult:
    """Result of scoring operation"""

    dimension: ScoringDimension
    score: float  # 0-1
    confidence: float  # 0-1 confidence in score
    reasoning: str
    contributing_factors: dict[str, float]  # Breakdown of score components


class ScoreAggregator:
    """Aggregate multiple dimension scores"""

    @staticmethod
    def weighted_average(
        scores: list[ScoringResult], weights: dict[ScoringDimension, float] | None = None
    ) -> float:
        """Compute weighted average of dimension scores"""
        if not scores:
            return 0.5

        if weights is None:
            weights = {dim: 1.0 for dim in ScoringDimension}

        total_weight = 0.0
        weighted_sum = 0.0

        for score in scores:
            weight = weights.get(score.dimension, 1.0)
            weighted_sum += score.score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    @staticmethod
    def confidence_weighted_average(
        scores: list[ScoringResult], weights: dict[ScoringDimension, float] | None = None
    ) -> float:
        """Compute weighted average, factoring in confidence"""
        if not scores:
            return 0.5

        if weights is None:
            weights = {dim: 1.0 for dim in ScoringDimension}

        total_confidence_weight = 0.0
        weighted_sum = 0.0

        for score in scores:
            base_weight = weights.get(score.dimension, 1.0)
            confidence_weight = base_weight * score.confidence

            weighted_sum += score.score * confidence_weight
            total_confidence_weight += confidence_weight

        return weighted_sum / total_confidence_weight if total_confidence_weight > 0 else 0.5

    @staticmethod
    def min_score(scores: list[ScoringResult]) -> float:
        """Use minimum score as bottleneck"""
        if not scores:
            return 0.5
        return min(s.score for s in scores)

    @staticmethod
    def max_score(scores: list[ScoringResult]) -> float:
        """Use maximum score"""
        if not scores:
            return 0.5
        return max(s.score for s in scores)


class ScoringStrategy(ABC):
    """Base class for scoring strategies"""

    @abstractmethod
    def score(self, data: dict[str, Any]) -> ScoringResult:
        """Score provided data"""
        pass

    @staticmethod
    def clamp(value: float) -> float:
        """Clamp value to 0-1 range"""
        return max(0.0, min(1.0, value))


# ============================================================================
# DIMENSION-SPECIFIC STRATEGIES
# ============================================================================


class ImportanceScorer(ScoringStrategy):
    """Score content importance based on semantic signals"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Entity count: more unique entities = higher importance
        entity_count = data.get("entity_count", 0)
        entity_score = self.clamp(entity_count / 10)  # Normalize to 0-1
        factors["entity_count"] = entity_score

        # Topic keywords: presence of primary topics
        primary_topics = data.get("primary_topics", [])
        topic_score = 1.0 if primary_topics else 0.0
        factors["topic_presence"] = topic_score

        # Duration: longer segments may indicate importance
        duration = data.get("duration_seconds", 0)
        duration_score = self.clamp(duration / 30)  # 30s = fully important
        factors["duration"] = duration_score

        # Composite
        combined = entity_score * 0.3 + topic_score * 0.4 + duration_score * 0.3
        final_score = self.clamp(combined)

        reasoning = (
            f"Composite of entity ({entity_score:.2f}), topics ({topic_score:.2f}), "
            f"duration ({duration_score:.2f})"
        )
        return ScoringResult(
            dimension=ScoringDimension.IMPORTANCE,
            score=final_score,
            confidence=0.8,
            reasoning=reasoning,
            contributing_factors=factors,
        )


class EmotionScorer(ScoringStrategy):
    """Score emotional intensity from speech, faces, text"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Speech emotion
        speech_emotion = data.get("speech_emotion", 0.5)
        factors["speech_emotion"] = speech_emotion

        # Face emotions (from vision)
        face_emotions = data.get("face_emotions", [])
        avg_face_emotion = sum(face_emotions) / len(face_emotions) if face_emotions else 0.5
        factors["face_emotions"] = avg_face_emotion

        # Sentiment from text
        text_sentiment = data.get("text_sentiment", 0.5)
        factors["text_sentiment"] = text_sentiment

        # Composite
        combined = speech_emotion * 0.4 + avg_face_emotion * 0.35 + text_sentiment * 0.25
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.EMOTION,
            score=final_score,
            confidence=0.7,
            reasoning="Composite of speech emotion, facial expressions, and text sentiment",
            contributing_factors=factors,
        )


class NoveltyScorer(ScoringStrategy):
    """Score how novel/unexpected content is"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Rare objects/concepts
        rare_entities = data.get("rare_entities", 0)
        rarity_score = self.clamp(rare_entities / 5)
        factors["rare_entities"] = rarity_score

        # Unexpected transitions
        scene_changes = data.get("scene_changes", 0)
        transition_score = self.clamp(scene_changes / 3)
        factors["scene_changes"] = transition_score

        # New topics
        new_topics = data.get("new_topics", 0)
        topic_score = self.clamp(new_topics / 4)
        factors["new_topics"] = topic_score

        # Composite
        combined = rarity_score * 0.35 + transition_score * 0.35 + topic_score * 0.3
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.NOVELTY,
            score=final_score,
            confidence=0.65,
            reasoning="Composite of rare entities, unexpected transitions, and new topics",
            contributing_factors=factors,
        )


class EngagementScorer(ScoringStrategy):
    """Score engagement potential"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Audience interaction
        questions = data.get("questions", 0)
        cta_strength = data.get("cta_strength", 0.5)
        question_score = self.clamp(questions / 3)
        factors["questions"] = question_score
        factors["cta_strength"] = cta_strength

        # Pacing (words/sec for speech)
        words_per_second = data.get("words_per_second", 2.5)
        pacing_score = self.clamp(words_per_second / 4.0)
        factors["pacing"] = pacing_score

        # Hook presence
        has_hook = data.get("has_hook", False)
        hook_score = 1.0 if has_hook else 0.3
        factors["hook_present"] = hook_score

        # Composite
        combined = (
            question_score * 0.25 + cta_strength * 0.2 + pacing_score * 0.2 + hook_score * 0.35
        )
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.ENGAGEMENT,
            score=final_score,
            confidence=0.75,
            reasoning="Composite of questions, CTA strength, pacing, and hook presence",
            contributing_factors=factors,
        )


class SpeechQualityScorer(ScoringStrategy):
    """Score speech audio quality"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # SNR (signal-to-noise ratio)
        snr = data.get("snr_db", 20)
        snr_score = self.clamp((snr + 10) / 30)  # -10 to 20 dB normalized
        factors["snr"] = snr_score

        # Clarity (articulation)
        clarity = data.get("clarity", 0.7)
        factors["clarity"] = clarity

        # Absence of artifacts
        artifacts = data.get("artifacts", [])
        artifact_score = 1.0 - min(1.0, len(artifacts) / 5)
        factors["artifacts"] = artifact_score

        # Composite
        combined = snr_score * 0.35 + clarity * 0.35 + artifact_score * 0.3
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.SPEECH_QUALITY,
            score=final_score,
            confidence=0.8,
            reasoning="Composite of SNR, clarity, and absence of artifacts",
            contributing_factors=factors,
        )


class VisualQualityScorer(ScoringStrategy):
    """Score visual quality"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Resolution
        resolution = data.get("resolution", "1080p")
        resolution_score = {"4k": 1.0, "1080p": 0.8, "720p": 0.6, "480p": 0.4}.get(resolution, 0.5)
        factors["resolution"] = resolution_score

        # Lighting
        lighting = data.get("lighting_score", 0.7)
        factors["lighting"] = lighting

        # Sharpness
        sharpness = data.get("sharpness", 0.7)
        factors["sharpness"] = sharpness

        # Composite
        combined = resolution_score * 0.3 + lighting * 0.35 + sharpness * 0.35
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.VISUAL_QUALITY,
            score=final_score,
            confidence=0.75,
            reasoning="Composite of resolution, lighting, and sharpness",
            contributing_factors=factors,
        )


class TopicStrengthScorer(ScoringStrategy):
    """Score how strongly a topic is represented"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Mention count
        mention_count = data.get("mention_count", 0)
        mention_score = self.clamp(mention_count / 10)
        factors["mention_count"] = mention_score

        # Duration of topic
        duration_seconds = data.get("duration_seconds", 0)
        duration_score = self.clamp(duration_seconds / 30)
        factors["duration"] = duration_score

        # Associated entities
        entity_count = data.get("entity_count", 0)
        entity_score = self.clamp(entity_count / 5)
        factors["entities"] = entity_score

        # Composite
        combined = mention_score * 0.4 + duration_score * 0.3 + entity_score * 0.3
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.TOPIC_STRENGTH,
            score=final_score,
            confidence=0.8,
            reasoning="Composite of mention count, duration, and associated entities",
            contributing_factors=factors,
        )


class ConfidenceScorer(ScoringStrategy):
    """Score confidence in other scores"""

    def score(self, data: dict[str, Any]) -> ScoringResult:
        factors = {}

        # Data quality
        data_quality = data.get("data_quality", 0.7)
        factors["data_quality"] = data_quality

        # Agreement between signals
        agreement_score = data.get("signal_agreement", 0.7)
        factors["signal_agreement"] = agreement_score

        # Sample size / coverage
        observation_count = data.get("observation_count", 5)
        coverage_score = self.clamp(observation_count / 10)
        factors["coverage"] = coverage_score

        # Composite
        combined = data_quality * 0.35 + agreement_score * 0.35 + coverage_score * 0.3
        final_score = self.clamp(combined)

        return ScoringResult(
            dimension=ScoringDimension.CONFIDENCE,
            score=final_score,
            confidence=0.85,
            reasoning="Composite of data quality, signal agreement, and observation coverage",
            contributing_factors=factors,
        )


# ============================================================================
# STRATEGY REGISTRY
# ============================================================================


class ScoringRegistry:
    """Registry for scoring strategies"""

    def __init__(self):
        self._strategies: dict[ScoringDimension, ScoringStrategy] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register default strategies"""
        self._strategies[ScoringDimension.IMPORTANCE] = ImportanceScorer()
        self._strategies[ScoringDimension.EMOTION] = EmotionScorer()
        self._strategies[ScoringDimension.NOVELTY] = NoveltyScorer()
        self._strategies[ScoringDimension.ENGAGEMENT] = EngagementScorer()
        self._strategies[ScoringDimension.SPEECH_QUALITY] = SpeechQualityScorer()
        self._strategies[ScoringDimension.VISUAL_QUALITY] = VisualQualityScorer()
        self._strategies[ScoringDimension.TOPIC_STRENGTH] = TopicStrengthScorer()
        self._strategies[ScoringDimension.CONFIDENCE] = ConfidenceScorer()

    def register_strategy(self, dimension: ScoringDimension, strategy: ScoringStrategy):
        """Register custom scoring strategy"""
        self._strategies[dimension] = strategy

    def get_strategy(self, dimension: ScoringDimension) -> ScoringStrategy | None:
        """Get strategy for dimension"""
        return self._strategies.get(dimension)

    def score_all_dimensions(self, data: dict[str, Any]) -> dict[ScoringDimension, ScoringResult]:
        """Score across all dimensions"""
        results = {}
        for dimension, strategy in self._strategies.items():
            results[dimension] = strategy.score(data)
        return results

    def score_dimensions(
        self, data: dict[str, Any], dimensions: list[ScoringDimension]
    ) -> dict[ScoringDimension, ScoringResult]:
        """Score specific dimensions"""
        results = {}
        for dimension in dimensions:
            strategy = self._strategies.get(dimension)
            if strategy:
                results[dimension] = strategy.score(data)
        return results


# ============================================================================
# SCORING PIPELINE
# ============================================================================


class ScoringPipeline:
    """Complete scoring pipeline with aggregation"""

    def __init__(self, registry: ScoringRegistry | None = None):
        self.registry = registry or ScoringRegistry()

    def score(
        self,
        data: dict[str, Any],
        dimensions: list[ScoringDimension] | None = None,
        weights: dict[ScoringDimension, float] | None = None,
        aggregation: str = "confidence_weighted",
    ) -> float:
        """Score data across dimensions and aggregate"""
        if dimensions is None:
            dimensions = list(ScoringDimension)

        results = self.registry.score_dimensions(data, dimensions)
        results_list = list(results.values())

        if aggregation == "weighted":
            return ScoreAggregator.weighted_average(results_list, weights)
        elif aggregation == "confidence_weighted":
            return ScoreAggregator.confidence_weighted_average(results_list, weights)
        elif aggregation == "min":
            return ScoreAggregator.min_score(results_list)
        elif aggregation == "max":
            return ScoreAggregator.max_score(results_list)
        else:
            return ScoreAggregator.confidence_weighted_average(results_list, weights)

    def score_detailed(
        self,
        data: dict[str, Any],
        dimensions: list[ScoringDimension] | None = None,
    ) -> tuple[float, dict[ScoringDimension, ScoringResult]]:
        """Score and return detailed results"""
        if dimensions is None:
            dimensions = list(ScoringDimension)

        results = self.registry.score_dimensions(data, dimensions)
        results_list = list(results.values())

        aggregate = ScoreAggregator.confidence_weighted_average(results_list)
        return aggregate, results

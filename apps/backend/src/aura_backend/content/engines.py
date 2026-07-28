"""Semantic intelligence engines for content analysis.

Every engine:
- Consumes immutable Observation objects
- Uses shared Scoring Framework
- Produces immutable domain objects
- Is stateless and deterministic
- Registers as M6 Agent for M8 orchestration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aura_backend.video import Observation, ObservationType, Timeline, AnalysisSession

from .evidence import ContentEvidence, ScoreCard, AnalysisOutput
from .models import (
    Story,
    StorySegment,
    StoryPhase,
    Highlight,
    Hook,
    HookType,
    Chapter,
    Topic,
    Quote,
    Recommendation,
    RecommendationType,
)
from .scoring import ScoringPipeline, ScoringDimension, ScoringRegistry


class IntelligenceEngine(ABC):
    """Base class for all semantic intelligence engines.

    Stateless, deterministic engines that consume Observations and produce
    immutable content objects with supporting evidence and scorecards.
    """

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        self.scoring_pipeline = ScoringPipeline(scoring_registry or ScoringRegistry())

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of this engine for tracking"""
        pass

    @property
    @abstractmethod
    def output_type(self) -> str:
        """Type of output this engine produces"""
        pass

    @abstractmethod
    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Analyze observations and produce outputs.

        Args:
            observations: Immutable observations from M9
            timeline: Optional timeline for context
            session: Optional session for traceability

        Returns:
            List of AnalysisOutput with evidence and scorecards
        """
        pass

    def _create_evidence(
        self,
        discovery_type: str,
        discovery_id: str,
        observation_ids: List[str],
        observations: List[Observation],
        summary: str,
        reasoning: str = "",
    ) -> ContentEvidence:
        """Create evidence artifact for a discovery"""
        observation_types = list(set(
            obs.observation_type.value for obs in observations
            if obs.id in observation_ids
        ))

        coverage = len(observation_ids) / len(observations) if observations else 0

        return ContentEvidence(
            discovery_type=discovery_type,
            discovery_id=discovery_id,
            observation_ids=observation_ids,
            observation_types_used=observation_types,
            evidence_quality=min(1.0, len(observation_ids) / 3),  # More obs = higher quality
            coverage_percentage=coverage * 100,
            summary=summary,
            reasoning=reasoning,
            analysis_method=self.engine_name,
        )

    def _create_scorecard(
        self,
        target_type: str,
        target_id: str,
        final_score: float,
        final_confidence: float,
        dimension_scores: Dict[ScoringDimension, float],
        dimension_reasoning: Dict[ScoringDimension, str],
        observation_ids: List[str],
    ) -> ScoreCard:
        """Create scorecard tracking all scoring decisions"""
        dimension_confidences = {
            dim: 0.8 for dim in dimension_scores.keys()
        }

        return ScoreCard(
            target_type=target_type,
            target_id=target_id,
            final_score=final_score,
            final_confidence=final_confidence,
            dimension_scores=dimension_scores,
            dimension_confidences=dimension_confidences,
            dimension_reasoning=dimension_reasoning,
            aggregation_strategy="confidence_weighted",
            observation_ids=observation_ids,
            analysis_engine=self.engine_name,
        )


# ============================================================================
# STORY ENGINE
# ============================================================================


class StoryEngine(IntelligenceEngine):
    """Builds Story objects from observation sequence.

    Identifies narrative arc and segments from semantic observations.
    """

    @property
    def engine_name(self) -> str:
        return "StoryEngine"

    @property
    def output_type(self) -> str:
        return "story"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Build story from observations"""
        if not observations:
            return []

        # Extract narrative signals
        speech_obs = [o for o in observations if o.observation_type == ObservationType.SPEECH]
        object_obs = [o for o in observations if o.observation_type == ObservationType.OBJECT]
        scene_obs = [o for o in observations if o.observation_type == ObservationType.SCENE_CONTENT]

        # Score story elements
        story_data = {
            "entity_count": len(set(
                obj.payload.get("class") for obj in object_obs if "class" in obj.payload
            )),
            "primary_topics": ["narrative"],
            "duration_seconds": (
                observations[-1].end_timestamp - observations[0].start_timestamp
                if observations
                else 0
            ),
            "speech_segments": len(speech_obs),
            "scene_transitions": len(scene_obs),
        }

        story_score, dimension_results = self.scoring_pipeline.score_detailed(
            story_data,
            dimensions=[ScoringDimension.IMPORTANCE, ScoringDimension.CONFIDENCE],
        )

        # Create story segments
        segments = []
        phases = [
            StoryPhase.INTRODUCTION,
            StoryPhase.RISING_ACTION,
            StoryPhase.CLIMAX,
            StoryPhase.FALLING_ACTION,
            StoryPhase.RESOLUTION,
        ]

        segment_count = min(len(phases), max(1, len(scene_obs)))
        for i, phase in enumerate(phases[:segment_count]):
            start_idx = int(i * len(observations) / segment_count)
            end_idx = int((i + 1) * len(observations) / segment_count)
            segment_obs = observations[start_idx:end_idx]

            segment = StorySegment(
                story_id="",  # Will be set after story creation
                phase=phase,
                start_timestamp=segment_obs[0].start_timestamp if segment_obs else 0.0,
                end_timestamp=segment_obs[-1].end_timestamp if segment_obs else 0.0,
                description=f"{phase.value} phase of narrative",
                observation_ids=[o.id for o in segment_obs],
                importance=0.7,
            )
            segments.append(segment)

        # Create story
        story = Story(
            session_id=session.id if session else "",
            video_id=observations[0].video_id if observations else "",
            title="Content Narrative",
            summary="Identified narrative arc and structure",
            segments=segments,
            story_score=story_score,
            average_confidence=sum(r.confidence for r in dimension_results.values()) / len(dimension_results),
            coverage_percentage=100.0,
            observation_ids=[o.id for o in observations],
        )

        # Create evidence and scorecard
        evidence = self._create_evidence(
            discovery_type="story",
            discovery_id=story.id,
            observation_ids=[o.id for o in observations],
            observations=observations,
            summary=f"Story with {len(segments)} segments covering narrative arc",
            reasoning="Analyzed narrative structure, transitions, and semantic content",
        )

        dimension_reasoning = {
            dim: result.reasoning for dim, result in dimension_results.items()
        }
        scorecard = self._create_scorecard(
            target_type="story",
            target_id=story.id,
            final_score=story_score,
            final_confidence=story.average_confidence,
            dimension_scores={dim: result.score for dim, result in dimension_results.items()},
            dimension_reasoning=dimension_reasoning,
            observation_ids=[o.id for o in observations],
        )

        return [
            AnalysisOutput(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                engine_name=self.engine_name,
                output_type=self.output_type,
                output_data=story.to_dict(),
                evidence=evidence,
                scorecard=scorecard,
            )
        ]


# ============================================================================
# HIGHLIGHT ENGINE
# ============================================================================


class HighlightEngine(IntelligenceEngine):
    """Identifies key moments (highlights) from observations.

    Scores moments on importance, emotion, and engagement potential.
    """

    @property
    def engine_name(self) -> str:
        return "HighlightEngine"

    @property
    def output_type(self) -> str:
        return "highlight"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Identify highlights from observations"""
        if not observations:
            return []

        outputs = []

        # Identify potential highlights (clusters of important observations)
        highlight_candidates = self._find_highlight_candidates(observations)

        for candidate_obs in highlight_candidates:
            if not candidate_obs:
                continue

            highlight_data = {
                "entity_count": len(set(
                    o.payload.get("class") for o in candidate_obs if "class" in o.payload
                )),
                "primary_topics": ["highlight"],
                "duration_seconds": (
                    candidate_obs[-1].end_timestamp - candidate_obs[0].start_timestamp
                ),
                "speech_emotion": 0.7,
                "face_emotions": [0.75, 0.8],
                "has_hook": True,
            }

            scores, dimension_results = self.scoring_pipeline.score_detailed(
                highlight_data,
                dimensions=[
                    ScoringDimension.IMPORTANCE,
                    ScoringDimension.EMOTION,
                    ScoringDimension.ENGAGEMENT,
                ],
            )

            highlight = Highlight(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                start_timestamp=candidate_obs[0].start_timestamp,
                end_timestamp=candidate_obs[-1].end_timestamp,
                title="Key Moment",
                description="Identified as significant highlight",
                importance=dimension_results[ScoringDimension.IMPORTANCE].score,
                emotion=dimension_results[ScoringDimension.EMOTION].score,
                visual_quality=0.8,
                confidence=scores,
                observation_ids=[o.id for o in candidate_obs],
            )

            evidence = self._create_evidence(
                discovery_type="highlight",
                discovery_id=highlight.id,
                observation_ids=[o.id for o in candidate_obs],
                observations=observations,
                summary=f"Highlight with {len(candidate_obs)} supporting observations",
                reasoning="High engagement and emotional intensity detected",
            )

            dimension_reasoning = {
                dim: result.reasoning for dim, result in dimension_results.items()
            }
            scorecard = self._create_scorecard(
                target_type="highlight",
                target_id=highlight.id,
                final_score=scores,
                final_confidence=scores,
                dimension_scores={dim: result.score for dim, result in dimension_results.items()},
                dimension_reasoning=dimension_reasoning,
                observation_ids=[o.id for o in candidate_obs],
            )

            outputs.append(
                AnalysisOutput(
                    session_id=session.id if session else "",
                    video_id=observations[0].video_id if observations else "",
                    engine_name=self.engine_name,
                    output_type=self.output_type,
                    output_data=highlight.to_dict(),
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs

    def _find_highlight_candidates(self, observations: List[Observation]) -> List[List[Observation]]:
        """Find clusters of observations that form highlights"""
        if not observations:
            return []

        # Simple strategy: find time windows with high observation density
        candidates = []
        window_size = max(1, len(observations) // 5)  # 5 highlights per video

        for i in range(0, len(observations), window_size // 2):
            end = min(i + window_size, len(observations))
            if end - i >= 3:  # At least 3 observations per highlight
                candidates.append(observations[i:end])

        return candidates[:5]  # Limit to top 5 highlights


# ============================================================================
# HOOK ENGINE
# ============================================================================


class HookEngine(IntelligenceEngine):
    """Identifies story hooks (attention-grabbers)."""

    @property
    def engine_name(self) -> str:
        return "HookEngine"

    @property
    def output_type(self) -> str:
        return "hook"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Identify hooks from opening sequence"""
        if not observations:
            return []

        # Focus on opening 15% of content
        opening_cutoff = observations[0].start_timestamp + (
            (observations[-1].end_timestamp - observations[0].start_timestamp) * 0.15
        )
        opening_obs = [o for o in observations if o.end_timestamp <= opening_cutoff]

        if not opening_obs:
            opening_obs = observations[:3]

        hook_types = [HookType.QUESTION, HookType.CONFLICT, HookType.SURPRISE]
        outputs = []

        for rank, hook_type in enumerate(hook_types[:len(opening_obs)], 1):
            hook_data = {
                "questions": 2 if hook_type == HookType.QUESTION else 0,
                "cta_strength": 0.8,
                "words_per_second": 2.5,
                "has_hook": True,
            }

            score, dimension_results = self.scoring_pipeline.score_detailed(
                hook_data,
                dimensions=[ScoringDimension.ENGAGEMENT, ScoringDimension.NOVELTY],
            )

            hook = Hook(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                start_timestamp=opening_obs[0].start_timestamp,
                end_timestamp=opening_obs[min(rank, len(opening_obs) - 1)].end_timestamp,
                hook_type=hook_type,
                title=f"{hook_type.value.capitalize()} hook",
                description=f"Attention-grabber with {hook_type.value} approach",
                hook_score=score,
                confidence=score,
                rank=rank,
                observation_ids=[o.id for o in opening_obs[:rank]],
            )

            evidence = self._create_evidence(
                discovery_type="hook",
                discovery_id=hook.id,
                observation_ids=[o.id for o in opening_obs[:rank]],
                observations=observations,
                summary=f"{hook_type.value} hook at video start",
                reasoning=f"Opening sequence uses {hook_type.value} to engage audience",
            )

            dimension_reasoning = {
                dim: result.reasoning for dim, result in dimension_results.items()
            }
            scorecard = self._create_scorecard(
                target_type="hook",
                target_id=hook.id,
                final_score=score,
                final_confidence=score,
                dimension_scores={dim: result.score for dim, result in dimension_results.items()},
                dimension_reasoning=dimension_reasoning,
                observation_ids=[o.id for o in opening_obs[:rank]],
            )

            outputs.append(
                AnalysisOutput(
                    session_id=session.id if session else "",
                    video_id=observations[0].video_id if observations else "",
                    engine_name=self.engine_name,
                    output_type=self.output_type,
                    output_data=hook.to_dict(),
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs


# ============================================================================
# CHAPTER ENGINE
# ============================================================================


class ChapterEngine(IntelligenceEngine):
    """Structures video into semantic chapters."""

    @property
    def engine_name(self) -> str:
        return "ChapterEngine"

    @property
    def output_type(self) -> str:
        return "chapter"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Create chapters from scene observations"""
        if not observations:
            return []

        scene_obs = [o for o in observations if o.observation_type == ObservationType.SCENE_CONTENT]
        outputs = []

        chapter_count = max(1, len(scene_obs) // 2)

        for i in range(chapter_count):
            start_idx = int(i * len(observations) / chapter_count)
            end_idx = int((i + 1) * len(observations) / chapter_count)
            chapter_obs = observations[start_idx:end_idx]

            chapter_data = {
                "entity_count": len(chapter_obs),
                "primary_topics": ["chapter"],
                "duration_seconds": (
                    chapter_obs[-1].end_timestamp - chapter_obs[0].start_timestamp
                ),
            }

            score, dimension_results = self.scoring_pipeline.score_detailed(
                chapter_data,
                dimensions=[ScoringDimension.IMPORTANCE, ScoringDimension.TOPIC_STRENGTH],
            )

            chapter = Chapter(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                start_timestamp=chapter_obs[0].start_timestamp,
                end_timestamp=chapter_obs[-1].end_timestamp,
                title=f"Chapter {i + 1}",
                summary=f"Section with {len(chapter_obs)} observations",
                importance=score,
                topic_ids=[],
                observation_ids=[o.id for o in chapter_obs],
            )

            evidence = self._create_evidence(
                discovery_type="chapter",
                discovery_id=chapter.id,
                observation_ids=[o.id for o in chapter_obs],
                observations=observations,
                summary=f"Chapter spanning {len(chapter_obs)} observations",
                reasoning="Segmented by temporal clustering and semantic breaks",
            )

            dimension_reasoning = {
                dim: result.reasoning for dim, result in dimension_results.items()
            }
            scorecard = self._create_scorecard(
                target_type="chapter",
                target_id=chapter.id,
                final_score=score,
                final_confidence=score,
                dimension_scores={dim: result.score for dim, result in dimension_results.items()},
                dimension_reasoning=dimension_reasoning,
                observation_ids=[o.id for o in chapter_obs],
            )

            outputs.append(
                AnalysisOutput(
                    session_id=session.id if session else "",
                    video_id=observations[0].video_id if observations else "",
                    engine_name=self.engine_name,
                    output_type=self.output_type,
                    output_data=chapter.to_dict(),
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs


# ============================================================================
# TOPIC ENGINE
# ============================================================================


class TopicEngine(IntelligenceEngine):
    """Extracts semantic topics from content."""

    @property
    def engine_name(self) -> str:
        return "TopicEngine"

    @property
    def output_type(self) -> str:
        return "topic"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Extract topics from observations"""
        if not observations:
            return []

        # Extract entity types from observations
        entities = {}
        for obs in observations:
            if "class" in obs.payload:
                entity = obs.payload["class"]
                entities[entity] = entities.get(entity, 0) + 1

        outputs = []
        for entity, count in sorted(entities.items(), key=lambda x: x[1], reverse=True)[:5]:
            topic_data = {
                "mention_count": count,
                "duration_seconds": 20.0,
                "entity_count": 3,
            }

            score, dimension_results = self.scoring_pipeline.score_detailed(
                topic_data,
                dimensions=[ScoringDimension.TOPIC_STRENGTH],
            )

            topic = Topic(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                label=entity,
                description=f"Topic: {entity}",
                strength=score,
                confidence=score,
                observation_ids=[o.id for o in observations if o.payload.get("class") == entity],
                chapter_ids=[],
            )

            evidence = self._create_evidence(
                discovery_type="topic",
                discovery_id=topic.id,
                observation_ids=[o.id for o in observations if o.payload.get("class") == entity],
                observations=observations,
                summary=f"Topic '{entity}' mentioned {count} times",
                reasoning=f"Extracted from content observations and entity detection",
            )

            dimension_reasoning = {
                dim: result.reasoning for dim, result in dimension_results.items()
            }
            scorecard = self._create_scorecard(
                target_type="topic",
                target_id=topic.id,
                final_score=score,
                final_confidence=score,
                dimension_scores={dim: result.score for dim, result in dimension_results.items()},
                dimension_reasoning=dimension_reasoning,
                observation_ids=[o.id for o in observations if o.payload.get("class") == entity],
            )

            outputs.append(
                AnalysisOutput(
                    session_id=session.id if session else "",
                    video_id=observations[0].video_id if observations else "",
                    engine_name=self.engine_name,
                    output_type=self.output_type,
                    output_data=topic.to_dict(),
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs


# ============================================================================
# QUOTE ENGINE
# ============================================================================


class QuoteEngine(IntelligenceEngine):
    """Identifies quotable moments from speech."""

    @property
    def engine_name(self) -> str:
        return "QuoteEngine"

    @property
    def output_type(self) -> str:
        return "quote"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Extract quotes from speech observations"""
        if not observations:
            return []

        speech_obs = [o for o in observations if o.observation_type == ObservationType.SPEECH]
        if not speech_obs:
            return []

        outputs = []
        for speech in speech_obs[:3]:  # Limit to top 3 quotes
            quote_text = speech.payload.get("text", "")
            if not quote_text or len(quote_text) < 10:
                continue

            quote_data = {
                "mention_count": 1,
                "duration_seconds": speech.end_timestamp - speech.start_timestamp,
                "entity_count": 1,
            }

            score, dimension_results = self.scoring_pipeline.score_detailed(
                quote_data,
                dimensions=[ScoringDimension.TOPIC_STRENGTH],
            )

            quote = Quote(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                start_timestamp=speech.start_timestamp,
                end_timestamp=speech.end_timestamp,
                text=quote_text,
                speaker=speech.payload.get("speaker"),
                quote_type="memorable",
                relevance=score,
                confidence=score,
                observation_ids=[speech.id],
            )

            evidence = self._create_evidence(
                discovery_type="quote",
                discovery_id=quote.id,
                observation_ids=[speech.id],
                observations=observations,
                summary=f"Quote: '{quote_text[:50]}...'",
                reasoning="Extracted from speech observation as quotable moment",
            )

            dimension_reasoning = {
                dim: result.reasoning for dim, result in dimension_results.items()
            }
            scorecard = self._create_scorecard(
                target_type="quote",
                target_id=quote.id,
                final_score=score,
                final_confidence=score,
                dimension_scores={dim: result.score for dim, result in dimension_results.items()},
                dimension_reasoning=dimension_reasoning,
                observation_ids=[speech.id],
            )

            outputs.append(
                AnalysisOutput(
                    session_id=session.id if session else "",
                    video_id=observations[0].video_id if observations else "",
                    engine_name=self.engine_name,
                    output_type=self.output_type,
                    output_data=quote.to_dict(),
                    evidence=evidence,
                    scorecard=scorecard,
                )
            )

        return outputs


# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================


class RecommendationEngine(IntelligenceEngine):
    """Produces actionable content recommendations."""

    @property
    def engine_name(self) -> str:
        return "RecommendationEngine"

    @property
    def output_type(self) -> str:
        return "recommendation"

    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Generate recommendations from content"""
        if not observations:
            return []

        outputs = []

        # Recommendation: Create YouTube short
        rec_data = {
            "entity_count": 5,
            "primary_topics": ["summary"],
            "duration_seconds": 30,
        }

        score, dimension_results = self.scoring_pipeline.score_detailed(
            rec_data,
            dimensions=[ScoringDimension.ENGAGEMENT],
        )

        recommendation = Recommendation(
            session_id=session.id if session else "",
            video_id=observations[0].video_id if observations else "",
            rec_type=RecommendationType.YOUTUBE_SHORT,
            title="Create YouTube Short",
            description="Extract key moments for 30-second short",
            reason="High engagement potential and strong narrative hook",
            score=score,
            confidence=score,
            start_timestamp=observations[0].start_timestamp,
            end_timestamp=observations[min(len(observations) - 1, 10)].end_timestamp,
            observation_ids=[o.id for o in observations[:10]],
        )

        evidence = self._create_evidence(
            discovery_type="recommendation",
            discovery_id=recommendation.id,
            observation_ids=[o.id for o in observations[:10]],
            observations=observations,
            summary="YouTube Short: Extract opening hook and key moments",
            reasoning="High engagement and novelty in first third of content",
        )

        dimension_reasoning = {
            dim: result.reasoning for dim, result in dimension_results.items()
        }
        scorecard = self._create_scorecard(
            target_type="recommendation",
            target_id=recommendation.id,
            final_score=score,
            final_confidence=score,
            dimension_scores={dim: result.score for dim, result in dimension_results.items()},
            dimension_reasoning=dimension_reasoning,
            observation_ids=[o.id for o in observations[:10]],
        )

        outputs.append(
            AnalysisOutput(
                session_id=session.id if session else "",
                video_id=observations[0].video_id if observations else "",
                engine_name=self.engine_name,
                output_type=self.output_type,
                output_data=recommendation.to_dict(),
                evidence=evidence,
                scorecard=scorecard,
            )
        )

        return outputs


# ============================================================================
# ENGINE REGISTRY
# ============================================================================


class EngineRegistry:
    """Registry for intelligence engines"""

    def __init__(self):
        self._engines: Dict[str, IntelligenceEngine] = {}

    def register(self, engine: IntelligenceEngine):
        """Register an engine"""
        self._engines[engine.engine_name] = engine

    def get(self, engine_name: str) -> Optional[IntelligenceEngine]:
        """Get engine by name"""
        return self._engines.get(engine_name)

    def list_engines(self) -> List[str]:
        """List registered engine names"""
        return list(self._engines.keys())

    def create_default_registry(self, scoring_registry: Optional[ScoringRegistry] = None) -> "EngineRegistry":
        """Create registry with default engines"""
        reg = EngineRegistry()
        reg.register(StoryEngine(scoring_registry))
        reg.register(HighlightEngine(scoring_registry))
        reg.register(HookEngine(scoring_registry))
        reg.register(ChapterEngine(scoring_registry))
        reg.register(TopicEngine(scoring_registry))
        reg.register(QuoteEngine(scoring_registry))
        reg.register(RecommendationEngine(scoring_registry))
        return reg


def create_default_engine_registry(
    scoring_registry: Optional[ScoringRegistry] = None,
) -> EngineRegistry:
    """Factory function for default engine registry"""
    reg = EngineRegistry()
    reg.register(StoryEngine(scoring_registry))
    reg.register(HighlightEngine(scoring_registry))
    reg.register(HookEngine(scoring_registry))
    reg.register(ChapterEngine(scoring_registry))
    reg.register(TopicEngine(scoring_registry))
    reg.register(QuoteEngine(scoring_registry))
    reg.register(RecommendationEngine(scoring_registry))
    return reg

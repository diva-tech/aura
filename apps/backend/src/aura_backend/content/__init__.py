"""Milestone 10: Content Intelligence & Story Engine.

Phase 1: Domain models, scoring framework, LLM provider abstractions.
Phase 2: Semantic intelligence engines as M6 agents for M8 orchestration.
"""

# Evidence and Scoring Cards (Phase 2)
from .agents import (
    ChapterAnalysisAgent,
    ContentIntelligenceAgent,
    ContentIntelligenceAgentRegistry,
    HighlightAnalysisAgent,
    HookAnalysisAgent,
    QuoteAnalysisAgent,
    RecommendationAnalysisAgent,
    StoryAnalysisAgent,
    TopicAnalysisAgent,
)

# Intelligence Engines (Phase 2)
from .engines import (
    ChapterEngine,
    EngineRegistry,
    HighlightEngine,
    HookEngine,
    IntelligenceEngine,
    QuoteEngine,
    RecommendationEngine,
    StoryEngine,
    TopicEngine,
    create_default_engine_registry,
)

# Evidence and Scoring Cards (Phase 2)
from .evidence import (
    AnalysisOutput,
    ContentEvidence,
    ScoreCard,
)

# LLM Providers
from .llm_providers import (
    AnthropicProvider,
    GeminiProvider,
    LLMModel,
    LLMProvider,
    LLMProviderRegistry,
    LLMResponse,
    LocalOllamaProvider,
    OpenAIProvider,
    create_default_registry,
)

# Domain Models
from .models import (
    Chapter,
    ContentMetrics,
    Highlight,
    Hook,
    HookType,
    Quote,
    Recommendation,
    RecommendationType,
    Story,
    StoryGraph,
    StoryPhase,
    StorySegment,
    Topic,
)

# Scoring Framework
from .scoring import (
    ConfidenceScorer,
    EmotionScorer,
    EngagementScorer,
    ImportanceScorer,
    NoveltyScorer,
    ScoreAggregator,
    ScoringDimension,
    ScoringPipeline,
    ScoringRegistry,
    ScoringResult,
    ScoringStrategy,
    SpeechQualityScorer,
    TopicStrengthScorer,
    VisualQualityScorer,
)

__all__ = [
    # Agents (Phase 2)
    "ContentIntelligenceAgent",
    "ChapterAnalysisAgent",
    "ContentIntelligenceAgentRegistry",
    "HighlightAnalysisAgent",
    "HookAnalysisAgent",
    "QuoteAnalysisAgent",
    "RecommendationAnalysisAgent",
    "StoryAnalysisAgent",
    "TopicAnalysisAgent",
    # Engines (Phase 2)
    "ChapterEngine",
    "EngineRegistry",
    "HighlightEngine",
    "HookEngine",
    "IntelligenceEngine",
    "QuoteEngine",
    "RecommendationEngine",
    "StoryEngine",
    "TopicEngine",
    "create_default_engine_registry",
    # Evidence (Phase 2)
    "AnalysisOutput",
    "ContentEvidence",
    "ScoreCard",
    # LLM
    "AnthropicProvider",
    "GeminiProvider",
    "LLMModel",
    "LLMProvider",
    "LLMProviderRegistry",
    "LLMResponse",
    "LocalOllamaProvider",
    "OpenAIProvider",
    "create_default_registry",
    # Models
    "Chapter",
    "ContentMetrics",
    "Highlight",
    "Hook",
    "HookType",
    "Quote",
    "Recommendation",
    "RecommendationType",
    "Story",
    "StoryGraph",
    "StoryPhase",
    "StorySegment",
    "Topic",
    # Scoring
    "ConfidenceScorer",
    "EmotionScorer",
    "EngagementScorer",
    "ImportanceScorer",
    "NoveltyScorer",
    "ScoreAggregator",
    "ScoringDimension",
    "ScoringPipeline",
    "ScoringRegistry",
    "ScoringResult",
    "ScoringStrategy",
    "SpeechQualityScorer",
    "TopicStrengthScorer",
    "VisualQualityScorer",
]

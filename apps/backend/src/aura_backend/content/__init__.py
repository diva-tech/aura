"""Milestone 10: Content Intelligence & Story Engine.

Phase 1 domain models, scoring framework, and LLM provider abstractions.
"""

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
    # Models
    "StoryPhase",
    "HookType",
    "RecommendationType",
    "StorySegment",
    "Story",
    "Highlight",
    "Hook",
    "Chapter",
    "Topic",
    "Quote",
    "Recommendation",
    "StoryGraph",
    "ContentMetrics",
    # Scoring
    "ScoringDimension",
    "ScoringResult",
    "ScoreAggregator",
    "ScoringStrategy",
    "ImportanceScorer",
    "EmotionScorer",
    "NoveltyScorer",
    "EngagementScorer",
    "SpeechQualityScorer",
    "VisualQualityScorer",
    "TopicStrengthScorer",
    "ConfidenceScorer",
    "ScoringRegistry",
    "ScoringPipeline",
    # LLM
    "LLMModel",
    "LLMResponse",
    "LLMProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "LocalOllamaProvider",
    "LLMProviderRegistry",
    "create_default_registry",
]

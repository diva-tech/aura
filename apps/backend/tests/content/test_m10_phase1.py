"""Milestone 10 Phase 1 Tests: Domain Models, Scoring, LLM Providers.

Comprehensive tests for:
1. Immutable domain models
2. Pluggable scoring framework
3. Provider-agnostic LLM abstractions
"""


import pytest

from aura_backend.content import (  # Models; Scoring; LLM
    AnthropicProvider,
    Chapter,
    ConfidenceScorer,
    ContentMetrics,
    EmotionScorer,
    EngagementScorer,
    GeminiProvider,
    Highlight,
    Hook,
    HookType,
    ImportanceScorer,
    LLMModel,
    LLMProviderRegistry,
    LLMResponse,
    LocalOllamaProvider,
    NoveltyScorer,
    OpenAIProvider,
    Quote,
    Recommendation,
    RecommendationType,
    ScoreAggregator,
    ScoringDimension,
    ScoringPipeline,
    ScoringRegistry,
    ScoringResult,
    SpeechQualityScorer,
    Story,
    StoryGraph,
    StoryPhase,
    StorySegment,
    Topic,
    TopicStrengthScorer,
    VisualQualityScorer,
    create_default_registry,
)

# ============================================================================
# DOMAIN MODEL TESTS
# ============================================================================


class TestStorySegment:
    """Test StorySegment immutability and fields"""

    def test_segment_creation(self):
        """StorySegment can be created"""
        segment = StorySegment(
            story_id="s1",
            video_id="v1",
            phase=StoryPhase.INTRODUCTION,
            start_timestamp=0.0,
            end_timestamp=10.0,
            description="Opening scene",
        )

        assert segment.phase == StoryPhase.INTRODUCTION
        assert segment.start_timestamp == 0.0
        assert segment.end_timestamp == 10.0

    def test_segment_immutable(self):
        """StorySegment is immutable"""
        segment = StorySegment(story_id="s1", video_id="v1")

        with pytest.raises(AttributeError):
            segment.phase = StoryPhase.CLIMAX

    def test_segment_to_dict(self):
        """StorySegment can serialize to dict"""
        segment = StorySegment(
            story_id="s1",
            video_id="v1",
            phase=StoryPhase.CLIMAX,
            importance=0.9,
        )

        d = segment.to_dict()
        assert d["phase"] == "climax"
        assert d["importance"] == 0.9


class TestStory:
    """Test Story model"""

    def test_story_creation(self):
        """Story can be created"""
        story = Story(
            session_id="sess-1",
            video_id="v1",
            title="Amazing Journey",
            summary="A remarkable story",
            story_score=0.85,
        )

        assert story.title == "Amazing Journey"
        assert story.story_score == 0.85

    def test_story_with_segments(self):
        """Story can contain segments"""
        segments = [
            StorySegment(story_id="s1", phase=StoryPhase.INTRODUCTION),
            StorySegment(story_id="s1", phase=StoryPhase.CLIMAX),
        ]

        story = Story(
            session_id="sess-1",
            video_id="v1",
            segments=segments,
        )

        assert len(story.segments) == 2

    def test_story_immutable(self):
        """Story is immutable"""
        story = Story(session_id="sess-1", video_id="v1")

        with pytest.raises(AttributeError):
            story.title = "New Title"

    def test_story_observation_tracking(self):
        """Story tracks source observations"""
        obs_ids = ["obs-1", "obs-2", "obs-3"]
        story = Story(
            session_id="sess-1",
            video_id="v1",
            observation_ids=obs_ids,
        )

        assert len(story.observation_ids) == 3
        assert story.observation_ids[0] == "obs-1"


class TestHighlight:
    """Test Highlight model"""

    def test_highlight_creation(self):
        """Highlight can be created"""
        highlight = Highlight(
            session_id="sess-1",
            video_id="v1",
            start_timestamp=30.0,
            end_timestamp=35.0,
            title="Peak Moment",
            importance=0.95,
        )

        assert highlight.title == "Peak Moment"
        assert highlight.importance == 0.95

    def test_highlight_scoring(self):
        """Highlight has multiple scoring dimensions"""
        highlight = Highlight(
            session_id="sess-1",
            video_id="v1",
            importance=0.9,
            emotion=0.8,
            visual_quality=0.7,
            confidence=0.85,
        )

        assert highlight.importance == 0.9
        assert highlight.emotion == 0.8
        assert highlight.visual_quality == 0.7
        assert highlight.confidence == 0.85

    def test_highlight_immutable(self):
        """Highlight is immutable"""
        highlight = Highlight(session_id="sess-1", video_id="v1")

        with pytest.raises(AttributeError):
            highlight.importance = 0.5


class TestHook:
    """Test Hook model"""

    def test_hook_types(self):
        """Hook supports all types"""
        for hook_type in HookType:
            hook = Hook(
                session_id="sess-1",
                video_id="v1",
                hook_type=hook_type,
                title=f"A {hook_type.value} hook",
            )

            assert hook.hook_type == hook_type

    def test_hook_ranking(self):
        """Hook can be ranked"""
        hooks = [
            Hook(session_id="sess-1", video_id="v1", rank=1, hook_score=0.95),
            Hook(session_id="sess-1", video_id="v1", rank=2, hook_score=0.80),
            Hook(session_id="sess-1", video_id="v1", rank=3, hook_score=0.65),
        ]

        assert hooks[0].rank < hooks[1].rank
        assert hooks[0].hook_score > hooks[2].hook_score


class TestChapter:
    """Test Chapter model"""

    def test_chapter_creation(self):
        """Chapter can be created"""
        chapter = Chapter(
            session_id="sess-1",
            video_id="v1",
            story_id="s1",
            title="The Beginning",
            importance=0.8,
        )

        assert chapter.title == "The Beginning"

    def test_chapter_topics(self):
        """Chapter tracks topics"""
        topic_ids = ["t1", "t2", "t3"]
        chapter = Chapter(
            session_id="sess-1",
            video_id="v1",
            story_id="s1",
            topic_ids=topic_ids,
        )

        assert len(chapter.topic_ids) == 3


class TestTopic:
    """Test Topic model"""

    def test_topic_creation(self):
        """Topic can be created"""
        topic = Topic(
            session_id="sess-1",
            video_id="v1",
            label="Technology",
            description="Discussion of AI systems",
            strength=0.9,
        )

        assert topic.label == "Technology"
        assert topic.strength == 0.9

    def test_topic_relationships(self):
        """Topic tracks related content"""
        topic = Topic(
            session_id="sess-1",
            video_id="v1",
            label="Tech",
            observation_ids=["o1", "o2"],
            chapter_ids=["c1"],
        )

        assert len(topic.observation_ids) == 2
        assert len(topic.chapter_ids) == 1


class TestQuote:
    """Test Quote model"""

    def test_quote_creation(self):
        """Quote can be created"""
        quote = Quote(
            session_id="sess-1",
            video_id="v1",
            text="To be or not to be",
            speaker="Shakespeare",
            quote_type="memorable",
            relevance=0.95,
        )

        assert quote.text == "To be or not to be"
        assert quote.speaker == "Shakespeare"
        assert quote.relevance == 0.95

    def test_quote_types(self):
        """Quote supports different types"""
        types = ["opinion", "definition", "statistic", "cta", "memorable"]
        for q_type in types:
            quote = Quote(
                session_id="sess-1",
                video_id="v1",
                text="Sample",
                quote_type=q_type,
            )

            assert quote.quote_type == q_type


class TestRecommendation:
    """Test Recommendation model"""

    def test_recommendation_types(self):
        """Recommendation supports all types"""
        for rec_type in RecommendationType:
            rec = Recommendation(
                session_id="sess-1",
                video_id="v1",
                rec_type=rec_type,
                title=f"{rec_type.value} recommendation",
            )

            assert rec.rec_type == rec_type

    def test_recommendation_with_timestamp(self):
        """Recommendation can reference specific segment"""
        rec = Recommendation(
            session_id="sess-1",
            video_id="v1",
            rec_type=RecommendationType.YOUTUBE_SHORT,
            start_timestamp=10.0,
            end_timestamp=25.0,
            score=0.88,
        )

        assert rec.start_timestamp == 10.0
        assert rec.end_timestamp == 25.0
        assert rec.score == 0.88


class TestStoryGraph:
    """Test StoryGraph model"""

    def test_story_graph_creation(self):
        """StoryGraph can be created"""
        graph = StoryGraph(
            session_id="sess-1",
            video_id="v1",
            story_id="s1",
            chapter_ids=["c1", "c2"],
            highlight_ids=["h1", "h2", "h3"],
        )

        assert len(graph.chapter_ids) == 2
        assert len(graph.highlight_ids) == 3

    def test_story_graph_relationships(self):
        """StoryGraph stores semantic relationships"""
        graph = StoryGraph(
            session_id="sess-1",
            video_id="v1",
            relationships={
                "h1": ["t1", "t2"],  # Highlight h1 has topics t1, t2
                "c1": ["h1", "h2"],  # Chapter c1 has highlights h1, h2
            },
        )

        assert graph.relationships["h1"] == ["t1", "t2"]


class TestContentMetrics:
    """Test ContentMetrics model"""

    def test_metrics_creation(self):
        """ContentMetrics can be created"""
        metrics = ContentMetrics(
            session_id="sess-1",
            video_id="v1",
            story_score=0.85,
            coverage_percentage=75.0,
            highlight_count=5,
            hook_count=2,
        )

        assert metrics.story_score == 0.85
        assert metrics.highlight_count == 5

    def test_metrics_component_counts(self):
        """Metrics track all component counts"""
        metrics = ContentMetrics(
            session_id="sess-1",
            video_id="v1",
            highlight_count=3,
            hook_count=2,
            chapter_count=4,
            topic_count=8,
            quote_count=12,
            recommendation_count=5,
        )

        total = (
            metrics.highlight_count
            + metrics.hook_count
            + metrics.chapter_count
            + metrics.topic_count
            + metrics.quote_count
            + metrics.recommendation_count
        )

        assert total == 34


# ============================================================================
# SCORING FRAMEWORK TESTS
# ============================================================================


class TestScoringResult:
    """Test ScoringResult immutability"""

    def test_scoring_result_immutable(self):
        """ScoringResult is immutable"""
        result = ScoringResult(
            dimension=ScoringDimension.IMPORTANCE,
            score=0.8,
            confidence=0.9,
            reasoning="Test",
            contributing_factors={},
        )

        with pytest.raises(AttributeError):
            result.score = 0.5


class TestImportanceScorer:
    """Test ImportanceScorer strategy"""

    def test_importance_scorer_creation(self):
        """ImportanceScorer can score"""
        scorer = ImportanceScorer()
        result = scorer.score(
            {
                "entity_count": 5,
                "primary_topics": ["tech"],
                "duration_seconds": 15,
            }
        )

        assert result.dimension == ScoringDimension.IMPORTANCE
        assert 0.0 <= result.score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.contributing_factors

    def test_importance_scorer_factors(self):
        """ImportanceScorer includes contributing factors"""
        scorer = ImportanceScorer()
        result = scorer.score({"entity_count": 10, "primary_topics": ["a", "b"]})

        assert "entity_count" in result.contributing_factors
        assert "topic_presence" in result.contributing_factors
        assert "duration" in result.contributing_factors


class TestEmotionScorer:
    """Test EmotionScorer strategy"""

    def test_emotion_scorer_creation(self):
        """EmotionScorer can score"""
        scorer = EmotionScorer()
        result = scorer.score(
            {
                "speech_emotion": 0.7,
                "face_emotions": [0.8, 0.75],
                "text_sentiment": 0.6,
            }
        )

        assert result.dimension == ScoringDimension.EMOTION
        assert 0.0 <= result.score <= 1.0


class TestNoveltyScorer:
    """Test NoveltyScorer strategy"""

    def test_novelty_scorer_empty_data(self):
        """NoveltyScorer handles empty data"""
        scorer = NoveltyScorer()
        result = scorer.score({})

        assert result.dimension == ScoringDimension.NOVELTY
        assert 0.0 <= result.score <= 1.0


class TestEngagementScorer:
    """Test EngagementScorer strategy"""

    def test_engagement_scorer_with_hook(self):
        """EngagementScorer scores higher with hook present"""
        scorer = EngagementScorer()

        result_with_hook = scorer.score(
            {
                "questions": 2,
                "cta_strength": 0.8,
                "words_per_second": 2.5,
                "has_hook": True,
            }
        )

        result_without_hook = scorer.score(
            {
                "questions": 2,
                "cta_strength": 0.8,
                "words_per_second": 2.5,
                "has_hook": False,
            }
        )

        assert result_with_hook.score > result_without_hook.score


class TestSpeechQualityScorer:
    """Test SpeechQualityScorer strategy"""

    def test_speech_quality_scorer(self):
        """SpeechQualityScorer can score speech"""
        scorer = SpeechQualityScorer()
        result = scorer.score(
            {
                "snr_db": 15,
                "clarity": 0.85,
                "artifacts": [],
            }
        )

        assert result.dimension == ScoringDimension.SPEECH_QUALITY
        assert 0.0 <= result.score <= 1.0


class TestVisualQualityScorer:
    """Test VisualQualityScorer strategy"""

    def test_visual_quality_scorer_resolution(self):
        """VisualQualityScorer considers resolution"""
        scorer = VisualQualityScorer()

        result_4k = scorer.score({"resolution": "4k", "lighting_score": 0.5, "sharpness": 0.5})
        result_480p = scorer.score({"resolution": "480p", "lighting_score": 0.5, "sharpness": 0.5})

        assert result_4k.score > result_480p.score


class TestTopicStrengthScorer:
    """Test TopicStrengthScorer strategy"""

    def test_topic_strength_scorer(self):
        """TopicStrengthScorer can score topics"""
        scorer = TopicStrengthScorer()
        result = scorer.score(
            {
                "mention_count": 8,
                "duration_seconds": 20,
                "entity_count": 3,
            }
        )

        assert result.dimension == ScoringDimension.TOPIC_STRENGTH
        assert 0.0 <= result.score <= 1.0


class TestConfidenceScorer:
    """Test ConfidenceScorer strategy"""

    def test_confidence_scorer(self):
        """ConfidenceScorer scores confidence"""
        scorer = ConfidenceScorer()
        result = scorer.score(
            {
                "data_quality": 0.9,
                "signal_agreement": 0.85,
                "observation_count": 10,
            }
        )

        assert result.dimension == ScoringDimension.CONFIDENCE
        assert result.score > 0.7  # Should be confident


class TestScoreAggregator:
    """Test score aggregation strategies"""

    def test_weighted_average(self):
        """ScoreAggregator.weighted_average works"""
        results = [
            ScoringResult(
                dimension=ScoringDimension.IMPORTANCE,
                score=0.9,
                confidence=0.9,
                reasoning="",
                contributing_factors={},
            ),
            ScoringResult(
                dimension=ScoringDimension.ENGAGEMENT,
                score=0.6,
                confidence=0.8,
                reasoning="",
                contributing_factors={},
            ),
        ]

        avg = ScoreAggregator.weighted_average(results)
        assert 0.0 <= avg <= 1.0

    def test_confidence_weighted_average(self):
        """ScoreAggregator.confidence_weighted_average factors in confidence"""
        high_confidence = ScoringResult(
            dimension=ScoringDimension.IMPORTANCE,
            score=0.9,
            confidence=0.95,
            reasoning="",
            contributing_factors={},
        )

        low_confidence = ScoringResult(
            dimension=ScoringDimension.ENGAGEMENT,
            score=0.1,
            confidence=0.2,
            reasoning="",
            contributing_factors={},
        )

        avg = ScoreAggregator.confidence_weighted_average([high_confidence, low_confidence])
        assert avg > 0.5  # Should be closer to high_confidence value

    def test_min_score(self):
        """ScoreAggregator.min_score returns minimum"""
        results = [
            ScoringResult(
                dimension=ScoringDimension.IMPORTANCE,
                score=0.9,
                confidence=0.9,
                reasoning="",
                contributing_factors={},
            ),
            ScoringResult(
                dimension=ScoringDimension.ENGAGEMENT,
                score=0.3,
                confidence=0.8,
                reasoning="",
                contributing_factors={},
            ),
        ]

        min_score = ScoreAggregator.min_score(results)
        assert min_score == 0.3

    def test_max_score(self):
        """ScoreAggregator.max_score returns maximum"""
        results = [
            ScoringResult(
                dimension=ScoringDimension.IMPORTANCE,
                score=0.9,
                confidence=0.9,
                reasoning="",
                contributing_factors={},
            ),
            ScoringResult(
                dimension=ScoringDimension.ENGAGEMENT,
                score=0.3,
                confidence=0.8,
                reasoning="",
                contributing_factors={},
            ),
        ]

        max_score = ScoreAggregator.max_score(results)
        assert max_score == 0.9


class TestScoringRegistry:
    """Test ScoringRegistry pattern"""

    def test_registry_defaults(self):
        """Registry registers default strategies"""
        registry = ScoringRegistry()

        importance = registry.get_strategy(ScoringDimension.IMPORTANCE)
        assert importance is not None

        emotion = registry.get_strategy(ScoringDimension.EMOTION)
        assert emotion is not None

    def test_registry_custom_strategy(self):
        """Registry can register custom strategies"""
        registry = ScoringRegistry()

        class CustomScorer(ScoringResult):
            def score(self, data):
                return ScoringResult(
                    dimension=ScoringDimension.IMPORTANCE,
                    score=0.5,
                    confidence=0.5,
                    reasoning="Custom",
                    contributing_factors={},
                )

        custom = CustomScorer()
        registry.register_strategy(ScoringDimension.IMPORTANCE, custom)

        retrieved = registry.get_strategy(ScoringDimension.IMPORTANCE)
        assert retrieved == custom

    def test_registry_score_dimensions(self):
        """Registry can score multiple dimensions"""
        registry = ScoringRegistry()

        results = registry.score_dimensions(
            {"entity_count": 5, "speech_emotion": 0.7},
            [ScoringDimension.IMPORTANCE, ScoringDimension.EMOTION],
        )

        assert len(results) == 2
        assert ScoringDimension.IMPORTANCE in results
        assert ScoringDimension.EMOTION in results


class TestScoringPipeline:
    """Test complete ScoringPipeline"""

    def test_pipeline_creation(self):
        """ScoringPipeline can be created"""
        pipeline = ScoringPipeline()
        assert pipeline is not None

    def test_pipeline_score_single(self):
        """Pipeline can score with aggregation"""
        pipeline = ScoringPipeline()

        score = pipeline.score(
            {"entity_count": 5, "speech_emotion": 0.7},
            dimensions=[ScoringDimension.IMPORTANCE, ScoringDimension.EMOTION],
        )

        assert 0.0 <= score <= 1.0

    def test_pipeline_score_detailed(self):
        """Pipeline can return detailed results"""
        pipeline = ScoringPipeline()

        aggregate, results = pipeline.score_detailed(
            {"entity_count": 5, "speech_emotion": 0.7},
            dimensions=[ScoringDimension.IMPORTANCE, ScoringDimension.EMOTION],
        )

        assert 0.0 <= aggregate <= 1.0
        assert ScoringDimension.IMPORTANCE in results
        assert ScoringDimension.EMOTION in results


# ============================================================================
# LLM PROVIDER TESTS
# ============================================================================


class TestLLMResponse:
    """Test LLMResponse immutability"""

    def test_response_immutable(self):
        """LLMResponse is immutable"""
        response = LLMResponse(
            model="claude",
            content="Test",
            stop_reason="stop_sequence",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

        with pytest.raises(AttributeError):
            response.content = "Modified"

    def test_response_is_success(self):
        """LLMResponse.is_success() works"""
        success = LLMResponse(
            model="claude",
            content="Success",
            stop_reason="stop_sequence",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

        failure = LLMResponse(
            model="claude",
            content="",
            stop_reason="error",
            usage={"input_tokens": 0, "output_tokens": 0},
            error="API error",
        )

        assert success.is_success()
        assert not failure.is_success()

    def test_response_get_json(self):
        """LLMResponse.get_json() extracts JSON"""
        response = LLMResponse(
            model="claude",
            content='{"key": "value", "number": 42}',
            stop_reason="stop_sequence",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

        data = response.get_json()
        assert data is not None
        assert data["key"] == "value"
        assert data["number"] == 42

    def test_response_get_json_markdown_block(self):
        """LLMResponse.get_json() extracts JSON from markdown blocks"""
        response = LLMResponse(
            model="claude",
            content='Some text\n```json\n{"key": "value"}\n```\nMore text',
            stop_reason="stop_sequence",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

        data = response.get_json()
        assert data is not None
        assert data["key"] == "value"


class TestAnthropicProvider:
    """Test Anthropic Claude provider"""

    def test_provider_initialization(self):
        """AnthropicProvider can be initialized"""
        provider = AnthropicProvider(api_key="sk-test")
        assert provider is not None
        assert provider.model == LLMModel.CLAUDE_3_5_SONNET

    def test_provider_supports_model(self):
        """AnthropicProvider supports Claude models"""
        provider = AnthropicProvider()

        assert provider.supports_model(LLMModel.CLAUDE_3_5_SONNET)
        assert provider.supports_model(LLMModel.CLAUDE_3_OPUS)
        assert not provider.supports_model(LLMModel.GPT_4O)

    def test_provider_default_model(self):
        """AnthropicProvider has default model"""
        provider = AnthropicProvider()
        assert provider.get_default_model() == LLMModel.CLAUDE_3_5_SONNET

    def test_provider_generate_without_api_key(self):
        """AnthropicProvider handles missing API key"""
        provider = AnthropicProvider()  # No API key

        response = provider.generate("Test prompt")
        assert not response.is_success()
        assert response.error is not None

    def test_provider_generate(self):
        """AnthropicProvider can generate"""
        provider = AnthropicProvider(api_key="sk-test")

        response = provider.generate("Test prompt", system="You are helpful")
        assert response.model == LLMModel.CLAUDE_3_5_SONNET.value


class TestOpenAIProvider:
    """Test OpenAI provider"""

    def test_provider_initialization(self):
        """OpenAIProvider can be initialized"""
        provider = OpenAIProvider(api_key="sk-test")
        assert provider is not None
        assert provider.model == LLMModel.GPT_4O

    def test_provider_supports_model(self):
        """OpenAIProvider supports GPT models"""
        provider = OpenAIProvider()

        assert provider.supports_model(LLMModel.GPT_4_TURBO)
        assert provider.supports_model(LLMModel.GPT_4O)
        assert not provider.supports_model(LLMModel.CLAUDE_3_5_SONNET)


class TestGeminiProvider:
    """Test Google Gemini provider"""

    def test_provider_initialization(self):
        """GeminiProvider can be initialized"""
        provider = GeminiProvider(api_key="test")
        assert provider is not None
        assert provider.model == LLMModel.GEMINI_2_0_PRO

    def test_provider_supports_model(self):
        """GeminiProvider supports Gemini"""
        provider = GeminiProvider()

        assert provider.supports_model(LLMModel.GEMINI_2_0_PRO)
        assert not provider.supports_model(LLMModel.GPT_4O)


class TestLocalOllamaProvider:
    """Test Local Ollama provider"""

    def test_provider_initialization(self):
        """LocalOllamaProvider can be initialized"""
        provider = LocalOllamaProvider()
        assert provider is not None

    def test_provider_generate(self):
        """LocalOllamaProvider can generate"""
        provider = LocalOllamaProvider()

        response = provider.generate("Test prompt")
        assert response.model.startswith("ollama:")


class TestLLMProviderRegistry:
    """Test LLM provider registry"""

    def test_registry_registration(self):
        """Registry can register providers"""
        registry = LLMProviderRegistry()

        claude = AnthropicProvider(api_key="sk-test")
        registry.register("claude", claude, is_default=True)

        retrieved = registry.get("claude")
        assert retrieved == claude

    def test_registry_default_provider(self):
        """Registry can return default provider"""
        registry = LLMProviderRegistry()

        claude = AnthropicProvider(api_key="sk-test")
        registry.register("claude", claude, is_default=True)

        default = registry.get_default()
        assert default == claude

    def test_registry_by_model(self):
        """Registry can find provider by model"""
        registry = LLMProviderRegistry()

        claude = AnthropicProvider(api_key="sk-test")
        registry.register("claude", claude)

        provider = registry.get_by_model(LLMModel.CLAUDE_3_5_SONNET)
        assert provider == claude

    def test_registry_list_providers(self):
        """Registry can list providers"""
        registry = LLMProviderRegistry()

        claude = AnthropicProvider(api_key="sk-test")
        openai = OpenAIProvider(api_key="sk-test")

        registry.register("claude", claude)
        registry.register("openai", openai)

        providers = registry.list_providers()
        assert "claude" in providers
        assert "openai" in providers


class TestCreateDefaultRegistry:
    """Test default registry factory"""

    def test_default_registry_created(self):
        """Default registry is created with providers"""
        registry = create_default_registry()

        assert registry.get("claude") is not None
        assert registry.get("openai") is not None
        assert registry.get("gemini") is not None
        assert registry.get("ollama") is not None

    def test_default_registry_has_default(self):
        """Default registry has default provider"""
        registry = create_default_registry()

        default = registry.get_default()
        assert default is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase1Integration:
    """Test Phase 1 components working together"""

    def test_story_with_scoring(self):
        """Story creation with scoring pipeline"""
        pipeline = ScoringPipeline()

        story_score = pipeline.score(
            {
                "entity_count": 10,
                "primary_topics": ["tech", "ai"],
                "duration_seconds": 45,
            },
            dimensions=[ScoringDimension.IMPORTANCE],
        )

        story = Story(
            session_id="sess-1",
            video_id="v1",
            title="AI Innovation",
            story_score=story_score,
        )

        assert story.story_score > 0.0

    def test_highlights_ranked_by_scoring(self):
        """Highlights scored and ranked"""
        registry = ScoringRegistry()
        pipeline = ScoringPipeline(registry)

        highlights = []
        for i in range(3):
            score = pipeline.score(
                {"entity_count": i + 5, "primary_topics": ["tech"]},
                dimensions=[ScoringDimension.IMPORTANCE],
            )
            highlights.append(
                Highlight(
                    session_id="sess-1",
                    video_id="v1",
                    importance=score,
                )
            )

        sorted_highlights = sorted(highlights, key=lambda h: h.importance, reverse=True)
        assert sorted_highlights[0].importance >= sorted_highlights[-1].importance

    def test_llm_provider_for_story_analysis(self):
        """LLM provider can analyze story content"""
        registry = create_default_registry()
        claude = registry.get("claude")

        response = claude.generate("Generate a story title from observations")
        assert response is not None

    def test_end_to_end_content_metric_computation(self):
        """End-to-end metrics computation"""
        # Create domain objects
        story = Story(
            session_id="sess-1",
            video_id="v1",
            title="Test Story",
        )

        highlights = [
            Highlight(session_id="sess-1", video_id="v1"),
            Highlight(session_id="sess-1", video_id="v1"),
            Highlight(session_id="sess-1", video_id="v1"),
        ]

        hooks = [
            Hook(session_id="sess-1", video_id="v1"),
            Hook(session_id="sess-1", video_id="v1"),
        ]

        # Create metrics
        metrics = ContentMetrics(
            session_id="sess-1",
            video_id="v1",
            story_score=story.story_score,
            highlight_count=len(highlights),
            hook_count=len(hooks),
            chapter_count=3,
            topic_count=5,
            quote_count=7,
            recommendation_count=2,
        )

        assert metrics.highlight_count == 3
        assert metrics.hook_count == 2
        assert (
            metrics.highlight_count
            + metrics.hook_count
            + metrics.chapter_count
            + metrics.topic_count
            + metrics.quote_count
            + metrics.recommendation_count
            == 20
        )

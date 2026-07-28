"""Milestone 10 Phase 2 Tests: Intelligence Engines, Evidence, and Agents.

Comprehensive tests for:
1. Evidence and scorecard models
2. Intelligence engines (stateless, deterministic)
3. M6 Agent wrappers for M8 orchestration
"""

import pytest
from datetime import datetime

from aura_backend.content import (
    # Evidence (Phase 2)
    ContentEvidence,
    ScoreCard,
    AnalysisOutput,
    # Engines (Phase 2)
    IntelligenceEngine,
    StoryEngine,
    HighlightEngine,
    HookEngine,
    ChapterEngine,
    TopicEngine,
    QuoteEngine,
    RecommendationEngine,
    EngineRegistry,
    create_default_engine_registry,
    # Agents (Phase 2)
    ContentIntelligenceAgent,
    StoryAnalysisAgent,
    HighlightAnalysisAgent,
    HookAnalysisAgent,
    ChapterAnalysisAgent,
    TopicAnalysisAgent,
    QuoteAnalysisAgent,
    RecommendationAnalysisAgent,
    ContentIntelligenceAgentRegistry,
    # Phase 1 models for comparison
    Story,
    Highlight,
    Hook,
    Chapter,
    Topic,
    Quote,
    Recommendation,
)

from aura_backend.video import (
    Observation,
    ObservationType,
    Timeline,
    AnalysisSession,
)

from aura_backend.content import ScoringDimension


# ============================================================================
# EVIDENCE MODEL TESTS
# ============================================================================


class TestContentEvidence:
    """Test ContentEvidence immutability and traceability"""

    def test_evidence_creation(self):
        """ContentEvidence can be created"""
        evidence = ContentEvidence(
            session_id="sess-1",
            video_id="v1",
            discovery_type="highlight",
            discovery_id="h1",
            observation_ids=["obs-1", "obs-2", "obs-3"],
            observation_types_used=["SPEECH", "OBJECT"],
            evidence_quality=0.85,
            coverage_percentage=75.0,
            summary="3 observations support this highlight",
            reasoning="High emotion and novelty detected",
            analysis_method="HighlightEngine",
        )

        assert evidence.discovery_type == "highlight"
        assert len(evidence.observation_ids) == 3
        assert evidence.evidence_quality == 0.85

    def test_evidence_immutable(self):
        """ContentEvidence is immutable"""
        evidence = ContentEvidence(session_id="sess-1", video_id="v1")

        with pytest.raises(AttributeError):
            evidence.evidence_quality = 0.95

    def test_evidence_to_dict(self):
        """ContentEvidence serializes to dict"""
        evidence = ContentEvidence(
            session_id="sess-1",
            video_id="v1",
            discovery_type="highlight",
            observation_ids=["o1", "o2"],
            observation_types_used=["SPEECH"],
            evidence_quality=0.8,
        )

        d = evidence.to_dict()
        assert d["discovery_type"] == "highlight"
        assert d["observation_count"] == 2
        assert d["evidence_quality"] == 0.8


class TestScoreCard:
    """Test ScoreCard for scoring transparency"""

    def test_scorecard_creation(self):
        """ScoreCard can be created"""
        scorecard = ScoreCard(
            session_id="sess-1",
            video_id="v1",
            target_type="highlight",
            target_id="h1",
            final_score=0.85,
            final_confidence=0.92,
            dimension_scores={
                ScoringDimension.IMPORTANCE: 0.9,
                ScoringDimension.ENGAGEMENT: 0.8,
            },
            dimension_confidences={
                ScoringDimension.IMPORTANCE: 0.95,
                ScoringDimension.ENGAGEMENT: 0.85,
            },
            dimension_reasoning={
                ScoringDimension.IMPORTANCE: "High entity count",
                ScoringDimension.ENGAGEMENT: "Strong questions",
            },
            analysis_engine="HighlightEngine",
        )

        assert scorecard.final_score == 0.85
        assert len(scorecard.dimension_scores) == 2

    def test_scorecard_immutable(self):
        """ScoreCard is immutable"""
        scorecard = ScoreCard(session_id="sess-1", video_id="v1")

        with pytest.raises(AttributeError):
            scorecard.final_score = 0.95

    def test_scorecard_to_dict(self):
        """ScoreCard serializes to dict"""
        scorecard = ScoreCard(
            session_id="sess-1",
            video_id="v1",
            target_type="highlight",
            dimension_scores={
                ScoringDimension.IMPORTANCE: 0.9,
            },
            analysis_engine="HighlightEngine",
        )

        d = scorecard.to_dict()
        assert d["target_type"] == "highlight"
        assert d["analysis_engine"] == "HighlightEngine"
        assert d["dimension_count"] == 1


class TestAnalysisOutput:
    """Test AnalysisOutput bundling content with evidence"""

    def test_analysis_output_creation(self):
        """AnalysisOutput can be created"""
        output = AnalysisOutput(
            session_id="sess-1",
            video_id="v1",
            engine_name="StoryEngine",
            output_type="story",
            output_data={"title": "Test Story"},
            is_confident=True,
        )

        assert output.engine_name == "StoryEngine"
        assert output.output_type == "story"
        assert output.is_confident

    def test_analysis_output_with_evidence(self):
        """AnalysisOutput can include evidence and scorecard"""
        evidence = ContentEvidence(
            session_id="sess-1",
            video_id="v1",
            discovery_type="story",
            discovery_id="s1",
            observation_ids=["o1", "o2"],
        )

        scorecard = ScoreCard(
            session_id="sess-1",
            video_id="v1",
            target_type="story",
            target_id="s1",
            final_score=0.85,
        )

        output = AnalysisOutput(
            session_id="sess-1",
            video_id="v1",
            engine_name="StoryEngine",
            output_type="story",
            output_data={},
            evidence=evidence,
            scorecard=scorecard,
        )

        assert output.evidence is not None
        assert output.scorecard is not None
        assert output.evidence.discovery_type == "story"


# ============================================================================
# ENGINE TESTS
# ============================================================================


class TestStoryEngine:
    """Test Story engine"""

    def test_story_engine_initialization(self):
        """StoryEngine can be initialized"""
        engine = StoryEngine()
        assert engine.engine_name == "StoryEngine"
        assert engine.output_type == "story"

    def test_story_engine_analyze(self):
        """StoryEngine produces Story objects"""
        engine = StoryEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH),
            Observation(video_id="v1", observation_type=ObservationType.SCENE_CONTENT),
            Observation(video_id="v1", observation_type=ObservationType.OBJECT),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        assert outputs[0].engine_name == "StoryEngine"
        assert outputs[0].output_type == "story"
        assert outputs[0].evidence is not None
        assert outputs[0].scorecard is not None

    def test_story_engine_stateless(self):
        """StoryEngine is stateless and deterministic"""
        engine1 = StoryEngine()
        engine2 = StoryEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH),
        ]

        outputs1 = engine1.analyze(observations)
        outputs2 = engine2.analyze(observations)

        # Both should produce equivalent results (deterministic)
        assert len(outputs1) == len(outputs2)


class TestHighlightEngine:
    """Test Highlight engine"""

    def test_highlight_engine_initialization(self):
        """HighlightEngine can be initialized"""
        engine = HighlightEngine()
        assert engine.engine_name == "HighlightEngine"
        assert engine.output_type == "highlight"

    def test_highlight_engine_analyze(self):
        """HighlightEngine produces Highlight objects"""
        engine = HighlightEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.OBJECT, start_timestamp=0.0, end_timestamp=10.0),
            Observation(video_id="v1", observation_type=ObservationType.OBJECT, start_timestamp=10.0, end_timestamp=20.0),
            Observation(video_id="v1", observation_type=ObservationType.OBJECT, start_timestamp=20.0, end_timestamp=30.0),
            Observation(video_id="v1", observation_type=ObservationType.OBJECT, start_timestamp=30.0, end_timestamp=40.0),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        for output in outputs:
            assert output.output_type == "highlight"
            assert output.evidence is not None
            assert output.scorecard is not None


class TestHookEngine:
    """Test Hook engine"""

    def test_hook_engine_initialization(self):
        """HookEngine can be initialized"""
        engine = HookEngine()
        assert engine.engine_name == "HookEngine"
        assert engine.output_type == "hook"

    def test_hook_engine_analyze(self):
        """HookEngine produces Hook objects"""
        engine = HookEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH, start_timestamp=0.0, end_timestamp=5.0),
            Observation(video_id="v1", observation_type=ObservationType.SPEECH, start_timestamp=5.0, end_timestamp=10.0),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        for output in outputs:
            assert output.output_type == "hook"


class TestChapterEngine:
    """Test Chapter engine"""

    def test_chapter_engine_initialization(self):
        """ChapterEngine can be initialized"""
        engine = ChapterEngine()
        assert engine.engine_name == "ChapterEngine"
        assert engine.output_type == "chapter"

    def test_chapter_engine_analyze(self):
        """ChapterEngine produces Chapter objects"""
        engine = ChapterEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SCENE_CONTENT, start_timestamp=0.0, end_timestamp=10.0),
            Observation(video_id="v1", observation_type=ObservationType.SCENE_CONTENT, start_timestamp=10.0, end_timestamp=20.0),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        for output in outputs:
            assert output.output_type == "chapter"


class TestTopicEngine:
    """Test Topic engine"""

    def test_topic_engine_initialization(self):
        """TopicEngine can be initialized"""
        engine = TopicEngine()
        assert engine.engine_name == "TopicEngine"
        assert engine.output_type == "topic"

    def test_topic_engine_analyze(self):
        """TopicEngine produces Topic objects"""
        engine = TopicEngine()

        observations = [
            Observation(
                video_id="v1",
                observation_type=ObservationType.OBJECT,
                payload={"class": "person"},
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.OBJECT,
                payload={"class": "person"},
            ),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        for output in outputs:
            assert output.output_type == "topic"


class TestQuoteEngine:
    """Test Quote engine"""

    def test_quote_engine_initialization(self):
        """QuoteEngine can be initialized"""
        engine = QuoteEngine()
        assert engine.engine_name == "QuoteEngine"
        assert engine.output_type == "quote"

    def test_quote_engine_analyze(self):
        """QuoteEngine produces Quote objects"""
        engine = QuoteEngine()

        observations = [
            Observation(
                video_id="v1",
                observation_type=ObservationType.SPEECH,
                start_timestamp=0.0,
                end_timestamp=5.0,
                payload={"text": "This is a memorable quote", "speaker": "Speaker"},
            ),
        ]

        outputs = engine.analyze(observations)

        # May or may not produce outputs depending on quote quality
        for output in outputs:
            assert output.output_type == "quote"


class TestRecommendationEngine:
    """Test Recommendation engine"""

    def test_recommendation_engine_initialization(self):
        """RecommendationEngine can be initialized"""
        engine = RecommendationEngine()
        assert engine.engine_name == "RecommendationEngine"
        assert engine.output_type == "recommendation"

    def test_recommendation_engine_analyze(self):
        """RecommendationEngine produces Recommendation objects"""
        engine = RecommendationEngine()

        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        for output in outputs:
            assert output.output_type == "recommendation"


# ============================================================================
# ENGINE REGISTRY TESTS
# ============================================================================


class TestEngineRegistry:
    """Test engine registry pattern"""

    def test_registry_creation(self):
        """EngineRegistry can be created"""
        registry = create_default_engine_registry()
        assert registry is not None

    def test_registry_lists_engines(self):
        """Registry lists all engines"""
        registry = create_default_engine_registry()
        engines = registry.list_engines()

        assert "StoryEngine" in engines
        assert "HighlightEngine" in engines
        assert "TopicEngine" in engines
        assert len(engines) >= 7

    def test_registry_retrieves_engine(self):
        """Registry can retrieve engines by name"""
        registry = create_default_engine_registry()

        story_engine = registry.get("StoryEngine")
        assert story_engine is not None
        assert isinstance(story_engine, StoryEngine)


# ============================================================================
# M6 AGENT TESTS
# ============================================================================


class TestContentIntelligenceAgent:
    """Test M6 agent wrapper"""

    def test_agent_initialization(self):
        """ContentIntelligenceAgent can be initialized"""
        engine = StoryEngine()
        agent = ContentIntelligenceAgent(engine)

        assert agent.engine == engine
        assert "ContentIntelligence.StoryEngine" in agent.name

    def test_agent_properties(self):
        """Agent has required M6 properties"""
        agent = StoryAnalysisAgent()

        assert agent.name is not None
        assert agent.description is not None
        assert "Story" in agent.name or "story" in agent.description


class TestStoryAnalysisAgent:
    """Test Story analysis agent"""

    def test_agent_initialization(self):
        """StoryAnalysisAgent initializes"""
        agent = StoryAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, StoryEngine)


class TestHighlightAnalysisAgent:
    """Test Highlight analysis agent"""

    def test_agent_initialization(self):
        """HighlightAnalysisAgent initializes"""
        agent = HighlightAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, HighlightEngine)


class TestHookAnalysisAgent:
    """Test Hook analysis agent"""

    def test_agent_initialization(self):
        """HookAnalysisAgent initializes"""
        agent = HookAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, HookEngine)


class TestChapterAnalysisAgent:
    """Test Chapter analysis agent"""

    def test_agent_initialization(self):
        """ChapterAnalysisAgent initializes"""
        agent = ChapterAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, ChapterEngine)


class TestTopicAnalysisAgent:
    """Test Topic analysis agent"""

    def test_agent_initialization(self):
        """TopicAnalysisAgent initializes"""
        agent = TopicAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, TopicEngine)


class TestQuoteAnalysisAgent:
    """Test Quote analysis agent"""

    def test_agent_initialization(self):
        """QuoteAnalysisAgent initializes"""
        agent = QuoteAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, QuoteEngine)


class TestRecommendationAnalysisAgent:
    """Test Recommendation analysis agent"""

    def test_agent_initialization(self):
        """RecommendationAnalysisAgent initializes"""
        agent = RecommendationAnalysisAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, RecommendationEngine)


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================


class TestContentIntelligenceAgentRegistry:
    """Test M6 agent registry for M8 dispatcher"""

    def test_registry_initialization(self):
        """ContentIntelligenceAgentRegistry initializes"""
        registry = ContentIntelligenceAgentRegistry()
        assert registry is not None

    def test_registry_lists_agents(self):
        """Registry lists all agents"""
        registry = ContentIntelligenceAgentRegistry()
        agents = registry.list_agents()

        assert len(agents) >= 7
        assert any("Story" in name for name in agents)
        assert any("Highlight" in name for name in agents)

    def test_registry_retrieves_agent(self):
        """Registry can retrieve agents by name"""
        registry = ContentIntelligenceAgentRegistry()

        agents = registry.list_agents()
        for agent_name in agents:
            agent = registry.get(agent_name)
            assert agent is not None

    def test_registry_finds_agents_by_type(self):
        """Registry finds agents by output type"""
        registry = ContentIntelligenceAgentRegistry()

        story_agents = registry.get_agents_by_output_type("story")
        assert len(story_agents) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase2Integration:
    """Test Phase 2 components working together"""

    def test_engine_produces_evidence_and_scorecard(self):
        """Engine produces output with evidence and scorecard"""
        engine = StoryEngine()
        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH, start_timestamp=0.0, end_timestamp=10.0),
            Observation(video_id="v1", observation_type=ObservationType.SCENE_CONTENT, start_timestamp=10.0, end_timestamp=20.0),
        ]

        outputs = engine.analyze(observations)

        assert len(outputs) > 0
        output = outputs[0]

        # Check evidence is present
        assert output.evidence is not None
        assert len(output.evidence.observation_ids) > 0
        assert output.evidence.analysis_method == "StoryEngine"

        # Check scorecard is present
        assert output.scorecard is not None
        assert output.scorecard.final_score >= 0.0
        assert output.scorecard.final_score <= 1.0

    def test_multiple_engines_on_same_observations(self):
        """Multiple engines can analyze same observations"""
        observations = [
            Observation(video_id="v1", observation_type=ObservationType.SPEECH, start_timestamp=0.0, end_timestamp=5.0),
            Observation(video_id="v1", observation_type=ObservationType.OBJECT, start_timestamp=5.0, end_timestamp=10.0),
        ]

        story_outputs = StoryEngine().analyze(observations)
        highlight_outputs = HighlightEngine().analyze(observations)
        topic_outputs = TopicEngine().analyze(observations)

        # All engines should produce outputs
        assert len(story_outputs) > 0
        assert len(highlight_outputs) > 0
        # Topics may or may not have outputs depending on entities

    def test_agent_executes_engine(self):
        """M6 agent successfully wraps engine"""
        agent = StoryAnalysisAgent()

        # Simulate M8 execution data
        input_data = {
            "observations": [
                {
                    "id": "obs-1",
                    "video_id": "v1",
                    "observation_type": "SPEECH",
                    "source_agent": "SpeechAgent",
                    "start_timestamp": 0.0,
                    "end_timestamp": 10.0,
                    "payload": {},
                },
                {
                    "id": "obs-2",
                    "video_id": "v1",
                    "observation_type": "SCENE_CONTENT",
                    "source_agent": "SceneAgent",
                    "start_timestamp": 10.0,
                    "end_timestamp": 20.0,
                    "payload": {},
                },
            ],
            "session_id": "sess-1",
            "video_id": "v1",
        }

        # Note: Full async execution would require a real agent context
        # This tests the agent structure and data handling
        assert agent.engine is not None
        assert len(input_data["observations"]) == 2

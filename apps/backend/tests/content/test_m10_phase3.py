"""Milestone 10 Phase 3 Tests: Creator Intelligence Layer.

Tests for:
1. Creator domain models (ContentOpportunity, CreatorStrategy, ContentBundle)
2. Deterministic creator engines (stateless, deterministic)
3. M6 creator agents for M8 orchestration
4. Optional LLM enhancement agents
5. Evidence and traceability through Phase 3
"""

import pytest

from aura_backend.content import (
    # Creator Models (Phase 3)
    ContentAsset,
    ContentBundle,
    ContentFormat,
    ContentOpportunity,
    CreatorGoal,
    CreatorStrategy,
    DistributionStrategy,
    EngagementMetrics,
    OpportunityType,
    PlatformType,
    # Creator Engines (Phase 3)
    ContentBundleEngine,
    ContentOpportunityEngine,
    CreatorEngineRegistry,
    CreatorStrategyEngine,
    create_default_creator_registry,
    # Creator Agents (Phase 3)
    BundleImplementationGuideEnhancer,
    ContentBundleAgent,
    ContentOpportunityAgent,
    CreatorAgentRegistry,
    CreatorIntelligenceAgent,
    CreatorStrategyAgent,
    OpportunityTitleEnhancer,
    StrategyNarrativeEnhancer,
    # Phase 2 models for testing
    Highlight,
    Hook,
    Quote,
    Topic,
    Recommendation,
)


# ============================================================================
# CREATOR DOMAIN MODEL TESTS
# ============================================================================


class TestEngagementMetrics:
    """Test engagement metrics model"""

    def test_engagement_metrics_creation(self):
        """EngagementMetrics can be created"""
        metrics = EngagementMetrics(
            estimated_reach=100000,
            engagement_rate=0.08,
            share_likelihood=0.15,
            virality_score=0.7,
        )

        assert metrics.estimated_reach == 100000
        assert metrics.engagement_rate == 0.08

    def test_engagement_metrics_immutable(self):
        """EngagementMetrics is immutable"""
        metrics = EngagementMetrics()

        with pytest.raises(AttributeError):
            metrics.engagement_rate = 0.5


class TestContentOpportunity:
    """Test content opportunity model"""

    def test_opportunity_creation(self):
        """ContentOpportunity can be created"""
        opportunity = ContentOpportunity(
            session_id="sess-1",
            video_id="v1",
            opportunity_type=OpportunityType.CLIP_EXTRACTION,
            title="Clip: Best Moment",
            platform_fit={PlatformType.YOUTUBE: 0.9, PlatformType.TIKTOK: 0.95},
            opportunity_score=0.85,
        )

        assert opportunity.opportunity_type == OpportunityType.CLIP_EXTRACTION
        assert opportunity.opportunity_score == 0.85

    def test_opportunity_platform_fit(self):
        """Opportunity tracks platform fit scores"""
        opportunity = ContentOpportunity(
            platform_fit={
                PlatformType.TIKTOK: 0.95,
                PlatformType.YOUTUBE: 0.85,
                PlatformType.INSTAGRAM: 0.9,
            }
        )

        assert len(opportunity.platform_fit) == 3
        assert opportunity.platform_fit[PlatformType.TIKTOK] == 0.95

    def test_opportunity_immutable(self):
        """ContentOpportunity is immutable"""
        opportunity = ContentOpportunity()

        with pytest.raises(AttributeError):
            opportunity.opportunity_score = 0.5


class TestCreatorStrategy:
    """Test creator strategy model"""

    def test_strategy_creation(self):
        """CreatorStrategy can be created"""
        strategy = CreatorStrategy(
            session_id="sess-1",
            video_id="v1",
            creator_goals=[CreatorGoal.GROW_AUDIENCE, CreatorGoal.INCREASE_ENGAGEMENT],
            primary_narrative="Growth-focused multi-platform strategy",
            strategy_score=0.85,
        )

        assert len(strategy.creator_goals) == 2
        assert strategy.strategy_score == 0.85

    def test_strategy_with_distribution(self):
        """Strategy can include distribution plan"""
        distribution = DistributionStrategy(
            primary_platform=PlatformType.TIKTOK,
            secondary_platforms=[PlatformType.YOUTUBE, PlatformType.INSTAGRAM],
        )

        strategy = CreatorStrategy(
            distribution_strategy=distribution,
        )

        assert strategy.distribution_strategy is not None
        assert strategy.distribution_strategy.primary_platform == PlatformType.TIKTOK


class TestContentBundle:
    """Test content bundle model"""

    def test_bundle_creation(self):
        """ContentBundle can be created"""
        bundle = ContentBundle(
            session_id="sess-1",
            video_id="v1",
            title="4-Week Campaign",
            theme="engagement-focused",
            bundle_score=0.85,
        )

        assert bundle.title == "4-Week Campaign"
        assert bundle.bundle_score == 0.85

    def test_bundle_with_assets(self):
        """Bundle contains content assets"""
        assets = [
            ContentAsset(title="Clip 1", platform=PlatformType.TIKTOK),
            ContentAsset(title="Quote 1", platform=PlatformType.INSTAGRAM),
        ]

        bundle = ContentBundle(assets=assets)

        assert len(bundle.assets) == 2

    def test_bundle_calendar(self):
        """Bundle has week-by-week calendar"""
        bundle = ContentBundle(
            week_1_posts=["asset-1", "asset-2"],
            week_2_posts=["asset-3"],
            week_3_posts=["asset-4", "asset-5"],
            week_4_posts=[],
        )

        assert len(bundle.week_1_posts) == 2
        assert len(bundle.week_2_posts) == 1


# ============================================================================
# DETERMINISTIC ENGINE TESTS
# ============================================================================


class TestContentOpportunityEngine:
    """Test opportunity identification engine"""

    def test_engine_initialization(self):
        """ContentOpportunityEngine can be initialized"""
        engine = ContentOpportunityEngine()
        assert engine is not None

    def test_engine_from_highlights(self):
        """Engine identifies opportunities from highlights"""
        engine = ContentOpportunityEngine()

        highlights = [
            Highlight(session_id="s1", video_id="v1", title="Peak Moment", start_timestamp=10.0, end_timestamp=15.0),
            Highlight(session_id="s1", video_id="v1", title="Key Point", start_timestamp=30.0, end_timestamp=35.0),
        ]

        opportunities = engine.analyze(highlights=highlights)

        assert len(opportunities) > 0
        assert opportunities[0].opportunity_type == OpportunityType.CLIP_EXTRACTION

    def test_engine_stateless_determinism(self):
        """Engine is deterministic and stateless"""
        engine1 = ContentOpportunityEngine()
        engine2 = ContentOpportunityEngine()

        highlights = [
            Highlight(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        ]

        opp1 = engine1.analyze(highlights=highlights)
        opp2 = engine2.analyze(highlights=highlights)

        # Same input → same output count
        assert len(opp1) == len(opp2)


class TestCreatorStrategyEngine:
    """Test strategy building engine"""

    def test_engine_initialization(self):
        """CreatorStrategyEngine can be initialized"""
        engine = CreatorStrategyEngine()
        assert engine is not None

    def test_engine_from_opportunities(self):
        """Engine builds strategy from opportunities"""
        engine = CreatorStrategyEngine()

        opportunities = [
            ContentOpportunity(
                opportunity_type=OpportunityType.CLIP_EXTRACTION,
                potential_goals=[CreatorGoal.GROW_AUDIENCE],
            ),
        ]

        strategies = engine.analyze(opportunities=opportunities)

        assert len(strategies) > 0
        assert strategies[0].opportunity_count > 0


class TestContentBundleEngine:
    """Test bundle creation engine"""

    def test_engine_initialization(self):
        """ContentBundleEngine can be initialized"""
        engine = ContentBundleEngine()
        assert engine is not None

    def test_engine_creates_bundles(self):
        """Engine creates content bundles"""
        engine = ContentBundleEngine()

        opportunities = [
            ContentOpportunity(
                opportunity_type=OpportunityType.CLIP_EXTRACTION,
                title="Clip 1",
            ),
        ]

        highlights = [
            Highlight(session_id="s1", video_id="v1", title="H1"),
        ]

        bundles = engine.analyze(opportunities=opportunities, highlights=highlights)

        assert len(bundles) > 0
        assert len(bundles[0].assets) > 0


# ============================================================================
# CREATOR ENGINE REGISTRY TESTS
# ============================================================================


class TestCreatorEngineRegistry:
    """Test creator engine registry"""

    def test_registry_creation(self):
        """CreatorEngineRegistry can be created"""
        registry = create_default_creator_registry()
        assert registry is not None

    def test_registry_has_engines(self):
        """Registry has all default engines"""
        registry = create_default_creator_registry()
        engines = registry.list_engines()

        assert "opportunities" in engines
        assert "strategy" in engines
        assert "bundles" in engines

    def test_registry_retrieves_engine(self):
        """Registry can retrieve engines"""
        registry = create_default_creator_registry()

        opp_engine = registry.get("opportunities")
        assert opp_engine is not None
        assert isinstance(opp_engine, ContentOpportunityEngine)


# ============================================================================
# M6 AGENT TESTS (Phase 3)
# ============================================================================


class TestCreatorIntelligenceAgent:
    """Test M6 creator agent base"""

    def test_agent_initialization(self):
        """CreatorIntelligenceAgent can be initialized"""
        engine = ContentOpportunityEngine()
        agent = CreatorIntelligenceAgent(engine)

        assert agent.engine == engine
        assert "CreatorIntelligence" in agent.name


class TestContentOpportunityAgent:
    """Test opportunity agent"""

    def test_agent_initialization(self):
        """ContentOpportunityAgent initializes"""
        agent = ContentOpportunityAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, ContentOpportunityEngine)


class TestCreatorStrategyAgent:
    """Test strategy agent"""

    def test_agent_initialization(self):
        """CreatorStrategyAgent initializes"""
        agent = CreatorStrategyAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, CreatorStrategyEngine)


class TestContentBundleAgent:
    """Test bundle agent"""

    def test_agent_initialization(self):
        """ContentBundleAgent initializes"""
        agent = ContentBundleAgent()
        assert agent.engine is not None
        assert isinstance(agent.engine, ContentBundleEngine)


# ============================================================================
# OPTIONAL LLM ENHANCEMENT AGENT TESTS
# ============================================================================


class TestOpportunityTitleEnhancer:
    """Test optional title enhancement"""

    def test_agent_initialization(self):
        """OpportunityTitleEnhancer initializes"""
        agent = OpportunityTitleEnhancer()
        assert agent is not None


class TestStrategyNarrativeEnhancer:
    """Test optional narrative enhancement"""

    def test_agent_initialization(self):
        """StrategyNarrativeEnhancer initializes"""
        agent = StrategyNarrativeEnhancer()
        assert agent is not None


class TestBundleImplementationGuideEnhancer:
    """Test optional guide enhancement"""

    def test_agent_initialization(self):
        """BundleImplementationGuideEnhancer initializes"""
        agent = BundleImplementationGuideEnhancer()
        assert agent is not None


# ============================================================================
# CREATOR AGENT REGISTRY TESTS
# ============================================================================


class TestCreatorAgentRegistry:
    """Test creator agent registry for M8"""

    def test_registry_initialization(self):
        """CreatorAgentRegistry initializes"""
        registry = CreatorAgentRegistry()
        assert registry is not None

    def test_registry_has_deterministic_agents(self):
        """Registry has deterministic agents"""
        registry = CreatorAgentRegistry()

        assert registry.get("opportunities") is not None
        assert registry.get("strategy") is not None
        assert registry.get("bundles") is not None

    def test_registry_has_llm_agents(self):
        """Registry has optional LLM agents"""
        registry = CreatorAgentRegistry()

        assert registry.get("enhance_titles") is not None
        assert registry.get("enhance_narrative") is not None
        assert registry.get("enhance_guides") is not None

    def test_registry_lists_agents(self):
        """Registry can list all agents"""
        registry = CreatorAgentRegistry()
        agents = registry.list_agents()

        assert len(agents) >= 6

    def test_registry_distinguishes_agent_types(self):
        """Registry can list deterministic vs LLM agents"""
        registry = CreatorAgentRegistry()

        deterministic = registry.list_deterministic_agents()
        llm_agents = registry.list_llm_agents()

        assert len(deterministic) == 3
        assert len(llm_agents) == 3
        assert len(set(deterministic) & set(llm_agents)) == 0  # No overlap


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestPhase3Integration:
    """Test Phase 3 components working together"""

    def test_end_to_end_creator_pipeline(self):
        """End-to-end: highlights → opportunities → strategy → bundle"""
        # Phase 2 artifacts
        highlights = [
            Highlight(session_id="s1", video_id="v1", title="Peak", start_timestamp=0.0, end_timestamp=5.0),
            Highlight(session_id="s1", video_id="v1", title="Key", start_timestamp=10.0, end_timestamp=15.0),
        ]

        hooks = [
            Hook(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=2.0),
        ]

        quotes = [
            Quote(session_id="s1", video_id="v1", text="Memorable quote", start_timestamp=5.0, end_timestamp=8.0),
        ]

        # Phase 3 pipeline
        opp_engine = ContentOpportunityEngine()
        opportunities = opp_engine.analyze(highlights=highlights, hooks=hooks)

        assert len(opportunities) > 0

        strat_engine = CreatorStrategyEngine()
        strategies = strat_engine.analyze(opportunities=opportunities)

        assert len(strategies) > 0

        bundle_engine = ContentBundleEngine()
        bundles = bundle_engine.analyze(opportunities=opportunities, highlights=highlights, quotes=quotes)

        assert len(bundles) > 0
        assert len(bundles[0].assets) > 0

    def test_traceability_through_phase3(self):
        """All Phase 3 outputs traceable to Phase 2 and M9"""
        highlights = [
            Highlight(
                session_id="s1",
                video_id="v1",
                observation_ids=["obs-1", "obs-2"],
            ),
        ]

        engine = ContentOpportunityEngine()
        opportunities = engine.analyze(highlights=highlights)

        # Opportunity should reference highlight and its observations
        assert len(opportunities[0].highlight_ids) > 0
        assert len(opportunities[0].observation_ids) > 0

    def test_platform_fit_scoring(self):
        """Opportunities score for different platforms"""
        highlights = [Highlight(session_id="s1", video_id="v1")]

        engine = ContentOpportunityEngine()
        opportunities = engine.analyze(highlights=highlights)

        # Each opportunity should have platform fit scores
        assert len(opportunities[0].platform_fit) > 0
        for platform, score in opportunities[0].platform_fit.items():
            assert 0.0 <= score <= 1.0

    def test_creator_goals_flow(self):
        """Creator goals flow from strategy to opportunities to bundle"""
        highlights = [Highlight(session_id="s1", video_id="v1")]

        opp_engine = ContentOpportunityEngine()
        opportunities = opp_engine.analyze(highlights=highlights)

        # Opportunities should have associated goals
        assert len(opportunities[0].potential_goals) > 0

        strat_engine = CreatorStrategyEngine()
        strategies = strat_engine.analyze(opportunities=opportunities)

        # Strategy should also have goals
        assert len(strategies[0].creator_goals) > 0

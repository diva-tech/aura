"""M6 Agents for Phase 3 creator intelligence.

Deterministic creator engines + optional LLM enhancement agents.
LLM agents enrich but never replace deterministic outputs.
"""

from typing import Any, Dict, List, Optional

try:
    from aura_backend.agent import ExecutableAgent, AgentContext, AgentResult
except ImportError:
    # Fallback for M6 not yet integrated
    class AgentResult:
        def __init__(self, status: str = "completed", output: Dict[str, Any] = None, error: Optional[str] = None):
            self.status = status
            self.output = output
            self.error = error

    class ExecutableAgent:
        pass

    class AgentContext:
        pass

from .creator import (
    ContentBundle,
    ContentOpportunity,
    CreatorGoal,
    CreatorStrategy,
)
from .creator_engines import (
    ContentBundleEngine,
    ContentOpportunityEngine,
    CreatorEngineRegistry,
    CreatorStrategyEngine,
)
from .llm_providers import LLMProvider, LLMProviderRegistry, create_default_registry
from .models import Chapter, Highlight, Hook, Quote, Recommendation, Story, Topic
from .scoring import ScoringRegistry


# ============================================================================
# DETERMINISTIC M6 AGENTS (Phase 3)
# ============================================================================


class CreatorIntelligenceAgent(ExecutableAgent):
    """Base M6 agent for creator intelligence"""

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    @property
    def name(self) -> str:
        return f"CreatorIntelligence.{self.engine.__class__.__name__}"

    @property
    def description(self) -> str:
        return f"Runs {self.engine.__class__.__name__} for creator intelligence"


class ContentOpportunityAgent(CreatorIntelligenceAgent):
    """M6 agent for identifying content opportunities"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(ContentOpportunityEngine(scoring_registry))

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Execute opportunity identification via M8"""
        try:
            # Deserialize Phase 2 artifacts
            highlights = input_data.get("highlights", [])
            hooks = input_data.get("hooks", [])
            recommendations = input_data.get("recommendations", [])
            topics = input_data.get("topics", [])

            # Run engine
            opportunities = self.engine.analyze(
                highlights=highlights,
                hooks=hooks,
                recommendations=recommendations,
                topics=topics,
            )

            # Serialize results
            output_dicts = [opp.to_dict() for opp in opportunities]

            return AgentResult(
                status="completed",
                output={
                    "engine": "ContentOpportunityEngine",
                    "opportunity_count": len(opportunities),
                    "opportunities": output_dicts,
                },
            )

        except Exception as e:
            return AgentResult(
                status="failed",
                error=f"Opportunity identification failed: {str(e)}",
            )


class CreatorStrategyAgent(CreatorIntelligenceAgent):
    """M6 agent for building creator strategy"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(CreatorStrategyEngine(scoring_registry))

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Execute strategy building via M8"""
        try:
            opportunities = input_data.get("opportunities", [])
            creator_goals = input_data.get("creator_goals", [])
            story_data = input_data.get("story", {})

            # Run engine
            strategies = self.engine.analyze(
                opportunities=opportunities,
                creator_goals=creator_goals,
            )

            # Serialize results
            output_dicts = [strat.to_dict() for strat in strategies]

            return AgentResult(
                status="completed",
                output={
                    "engine": "CreatorStrategyEngine",
                    "strategy_count": len(strategies),
                    "strategies": output_dicts,
                },
            )

        except Exception as e:
            return AgentResult(
                status="failed",
                error=f"Strategy building failed: {str(e)}",
            )


class ContentBundleAgent(CreatorIntelligenceAgent):
    """M6 agent for creating content bundles"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(ContentBundleEngine(scoring_registry))

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Execute bundle creation via M8"""
        try:
            opportunities = input_data.get("opportunities", [])
            strategy_data = input_data.get("strategy", {})
            highlights = input_data.get("highlights", [])
            quotes = input_data.get("quotes", [])

            # Run engine
            bundles = self.engine.analyze(
                opportunities=opportunities,
                highlights=highlights,
                quotes=quotes,
            )

            # Serialize results
            output_dicts = [bundle.to_dict() for bundle in bundles]

            return AgentResult(
                status="completed",
                output={
                    "engine": "ContentBundleEngine",
                    "bundle_count": len(bundles),
                    "bundles": output_dicts,
                },
            )

        except Exception as e:
            return AgentResult(
                status="failed",
                error=f"Bundle creation failed: {str(e)}",
            )


# ============================================================================
# OPTIONAL LLM ENHANCEMENT AGENTS (Phase 3)
# ============================================================================


class LLMEnhancementAgent(ExecutableAgent):
    """Base M6 agent for optional LLM enhancement.

    Enriches deterministic outputs but never replaces them.
    Failures are graceful - returns original data.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        super().__init__()
        if llm_provider is None:
            registry = create_default_registry()
            llm_provider = registry.get_default()
        self.llm_provider = llm_provider

    def _enrich_or_fallback(
        self,
        original_data: Dict[str, Any],
        llm_result: Optional[str],
        field_name: str,
    ) -> Dict[str, Any]:
        """Enrich data with LLM result or return original"""
        if not llm_result:
            return original_data

        enriched = original_data.copy()
        enriched[f"{field_name}_enhanced"] = llm_result
        enriched[f"{field_name}_original"] = original_data.get(field_name)
        return enriched


class OpportunityTitleEnhancer(LLMEnhancementAgent):
    """Optional LLM enhancement for opportunity titles"""

    @property
    def name(self) -> str:
        return "CreatorIntelligence.OpportunityTitleEnhancer"

    @property
    def description(self) -> str:
        return "Optional LLM enhancement for opportunity titles (never replaces deterministic)"

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Enhance opportunity titles with LLM"""
        try:
            opportunities = input_data.get("opportunities", [])

            if not self.llm_provider or not opportunities:
                return AgentResult(
                    status="completed",
                    output={
                        "engine": "OpportunityTitleEnhancer",
                        "opportunities": opportunities,
                        "enhanced": False,
                        "reason": "LLM unavailable or no opportunities",
                    },
                )

            # Enhance top 3 opportunities
            for opp in opportunities[:3]:
                prompt = f"""Create a compelling title for this content opportunity:
Type: {opp.get('opportunity_type')}
Description: {opp.get('description')}
Current Title: {opp.get('title')}

Generate a more engaging title that hooks the creator's audience."""

                response = self.llm_provider.generate(prompt)

                if response.is_success():
                    opp["title_suggestion"] = response.content
                # If LLM fails, just continue - we keep original

            return AgentResult(
                status="completed",
                output={
                    "engine": "OpportunityTitleEnhancer",
                    "opportunities": opportunities,
                    "enhanced": True,
                },
            )

        except Exception as e:
            # Graceful failure - return original data
            return AgentResult(
                status="completed",
                output={
                    "engine": "OpportunityTitleEnhancer",
                    "opportunities": input_data.get("opportunities", []),
                    "enhanced": False,
                    "error": str(e),
                },
            )


class StrategyNarrativeEnhancer(LLMEnhancementAgent):
    """Optional LLM enhancement for strategy narrative"""

    @property
    def name(self) -> str:
        return "CreatorIntelligence.StrategyNarrativeEnhancer"

    @property
    def description(self) -> str:
        return "Optional LLM enhancement for strategy narrative"

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Enhance strategy narrative with LLM"""
        try:
            strategies = input_data.get("strategies", [])

            if not self.llm_provider or not strategies:
                return AgentResult(
                    status="completed",
                    output={
                        "engine": "StrategyNarrativeEnhancer",
                        "strategies": strategies,
                        "enhanced": False,
                    },
                )

            # Enhance narratives
            for strat in strategies:
                prompt = f"""Enhance this creator strategy narrative:
Goals: {strat.get('creator_goals')}
Current Narrative: {strat.get('primary_narrative')}
Themes: {strat.get('key_themes')}

Create a more compelling narrative that inspires the creator to execute."""

                response = self.llm_provider.generate(prompt)

                if response.is_success():
                    strat["narrative_enhanced"] = response.content

            return AgentResult(
                status="completed",
                output={
                    "engine": "StrategyNarrativeEnhancer",
                    "strategies": strategies,
                    "enhanced": True,
                },
            )

        except Exception:
            # Graceful failure
            return AgentResult(
                status="completed",
                output={
                    "engine": "StrategyNarrativeEnhancer",
                    "strategies": input_data.get("strategies", []),
                    "enhanced": False,
                },
            )


class BundleImplementationGuideEnhancer(LLMEnhancementAgent):
    """Optional LLM enhancement for bundle implementation guides"""

    @property
    def name(self) -> str:
        return "CreatorIntelligence.BundleImplementationGuideEnhancer"

    @property
    def description(self) -> str:
        return "Optional LLM enhancement for bundle implementation guides"

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Enhance bundle implementation guides with LLM"""
        try:
            bundles = input_data.get("bundles", [])

            if not self.llm_provider or not bundles:
                return AgentResult(
                    status="completed",
                    output={
                        "engine": "BundleImplementationGuideEnhancer",
                        "bundles": bundles,
                        "enhanced": False,
                    },
                )

            # Enhance guides
            for bundle in bundles:
                prompt = f"""Create a detailed implementation guide for this content bundle:
Title: {bundle.get('title')}
Theme: {bundle.get('theme')}
Asset Count: {bundle.get('asset_count')}
Platforms: {bundle.get('platform_count')}

Provide step-by-step instructions for the creator to execute this bundle effectively."""

                response = self.llm_provider.generate(prompt)

                if response.is_success():
                    bundle["guide_enhanced"] = response.content

            return AgentResult(
                status="completed",
                output={
                    "engine": "BundleImplementationGuideEnhancer",
                    "bundles": bundles,
                    "enhanced": True,
                },
            )

        except Exception:
            # Graceful failure
            return AgentResult(
                status="completed",
                output={
                    "engine": "BundleImplementationGuideEnhancer",
                    "bundles": input_data.get("bundles", []),
                    "enhanced": False,
                },
            )


# ============================================================================
# AGENT REGISTRY
# ============================================================================


class CreatorAgentRegistry:
    """Registry of creator intelligence agents for M8"""

    def __init__(
        self,
        scoring_registry: Optional[ScoringRegistry] = None,
        llm_provider_registry: Optional[LLMProviderRegistry] = None,
    ):
        self.scoring_registry = scoring_registry or ScoringRegistry()
        self.llm_provider_registry = llm_provider_registry or create_default_registry()
        self.agents: Dict[str, ExecutableAgent] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register default deterministic + optional LLM agents"""
        # Deterministic agents (always available)
        self.agents["opportunities"] = ContentOpportunityAgent(self.scoring_registry)
        self.agents["strategy"] = CreatorStrategyAgent(self.scoring_registry)
        self.agents["bundles"] = ContentBundleAgent(self.scoring_registry)

        # Optional LLM enhancement agents
        default_llm = self.llm_provider_registry.get_default()
        self.agents["enhance_titles"] = OpportunityTitleEnhancer(default_llm)
        self.agents["enhance_narrative"] = StrategyNarrativeEnhancer(default_llm)
        self.agents["enhance_guides"] = BundleImplementationGuideEnhancer(default_llm)

    def register(self, name: str, agent: ExecutableAgent):
        """Register an agent"""
        self.agents[name] = agent

    def get(self, agent_name: str) -> Optional[ExecutableAgent]:
        """Get agent by name"""
        return self.agents.get(agent_name)

    def list_agents(self) -> List[str]:
        """List agent names"""
        return list(self.agents.keys())

    def list_deterministic_agents(self) -> List[str]:
        """List only deterministic agents"""
        return ["opportunities", "strategy", "bundles"]

    def list_llm_agents(self) -> List[str]:
        """List only optional LLM agents"""
        return ["enhance_titles", "enhance_narrative", "enhance_guides"]

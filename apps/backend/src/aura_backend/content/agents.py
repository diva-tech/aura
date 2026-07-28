"""M6 Agent implementations wrapping intelligence engines.

Each engine is exposed as an M6 ExecutableAgent for execution via M8 Task Orchestration.
Preserves M1-M9 architecture without modification.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    from aura_backend.agent import ExecutableAgent, AgentContext, AgentResult, AgentStatus
except ImportError:
    # Fallback for M6 not yet integrated; define minimal interface
    @dataclass
    class AgentResult:
        status: str = "completed"
        output: Dict[str, Any] = None
        error: Optional[str] = None

    class ExecutableAgent:
        """Minimal M6 Agent interface"""
        pass

    class AgentContext:
        """Minimal M6 Context interface"""
        pass

from aura_backend.video import Observation, Timeline, AnalysisSession

from .engines import (
    IntelligenceEngine,
    StoryEngine,
    HighlightEngine,
    HookEngine,
    ChapterEngine,
    TopicEngine,
    QuoteEngine,
    RecommendationEngine,
    EngineRegistry,
)
from .scoring import ScoringRegistry


class ContentIntelligenceAgent(ExecutableAgent):
    """Base M6 Agent for content intelligence engines.

    Wraps IntelligenceEngine instances for execution via M8.
    """

    def __init__(self, engine: IntelligenceEngine):
        super().__init__()
        self.engine = engine

    @property
    def name(self) -> str:
        """Agent name for M8 registry"""
        return f"ContentIntelligence.{self.engine.engine_name}"

    @property
    def description(self) -> str:
        """Agent description"""
        return f"Runs {self.engine.engine_name} for {self.engine.output_type} analysis"

    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Execute engine via M8 orchestration.

        Input data expected:
        {
            "observations": List[Dict] — serialized Observation objects
            "timeline_id": str — optional Timeline reference
            "session_id": str — AnalysisSession reference
            "video_id": str — video being analyzed
        }
        """
        try:
            # Reconstruct observations from serialized data
            observations = []
            if "observations" in input_data:
                for obs_data in input_data["observations"]:
                    obs = Observation(
                        id=obs_data.get("id"),
                        video_id=obs_data.get("video_id"),
                        observation_type=obs_data.get("observation_type"),
                        source_agent=obs_data.get("source_agent"),
                        start_timestamp=obs_data.get("start_timestamp", 0.0),
                        end_timestamp=obs_data.get("end_timestamp", 0.0),
                        payload=obs_data.get("payload", {}),
                        metadata=obs_data.get("metadata", {}),
                    )
                    observations.append(obs)

            # Reconstruct session if provided
            session = None
            if "session_id" in input_data:
                session = AnalysisSession(
                    id=input_data["session_id"],
                    video_id=input_data.get("video_id"),
                )

            # Run engine analysis
            outputs = self.engine.analyze(
                observations=observations,
                timeline=None,  # Timeline not needed for engine execution
                session=session,
            )

            # Convert outputs to serializable format
            output_dicts = [output.to_dict() for output in outputs]

            return AgentResult(
                status="completed",
                output={
                    "engine": self.engine.engine_name,
                    "output_type": self.engine.output_type,
                    "outputs": output_dicts,
                    "count": len(output_dicts),
                },
            )

        except Exception as e:
            return AgentResult(
                status="failed",
                error=f"{self.engine.engine_name} execution failed: {str(e)}",
            )


class StoryAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Story analysis"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(StoryEngine(scoring_registry))


class HighlightAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Highlight identification"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(HighlightEngine(scoring_registry))


class HookAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Hook identification"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(HookEngine(scoring_registry))


class ChapterAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Chapter extraction"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(ChapterEngine(scoring_registry))


class TopicAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Topic extraction"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(TopicEngine(scoring_registry))


class QuoteAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Quote identification"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(QuoteEngine(scoring_registry))


class RecommendationAnalysisAgent(ContentIntelligenceAgent):
    """M6 Agent for Recommendation generation"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        super().__init__(RecommendationEngine(scoring_registry))


class ContentIntelligenceAgentRegistry:
    """Registry of M6 agents for M8 dispatcher"""

    def __init__(self, scoring_registry: Optional[ScoringRegistry] = None):
        self.scoring_registry = scoring_registry or ScoringRegistry()
        self.agents: Dict[str, ContentIntelligenceAgent] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register all default intelligence agents"""
        self.register(StoryAnalysisAgent(self.scoring_registry))
        self.register(HighlightAnalysisAgent(self.scoring_registry))
        self.register(HookAnalysisAgent(self.scoring_registry))
        self.register(ChapterAnalysisAgent(self.scoring_registry))
        self.register(TopicAnalysisAgent(self.scoring_registry))
        self.register(QuoteAnalysisAgent(self.scoring_registry))
        self.register(RecommendationAnalysisAgent(self.scoring_registry))

    def register(self, agent: ContentIntelligenceAgent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def get(self, agent_name: str) -> Optional[ContentIntelligenceAgent]:
        """Get agent by name"""
        return self.agents.get(agent_name)

    def list_agents(self) -> List[str]:
        """List registered agent names"""
        return list(self.agents.keys())

    def get_agents_by_output_type(self, output_type: str) -> List[ContentIntelligenceAgent]:
        """Get all agents producing a specific output type"""
        return [
            agent for agent in self.agents.values()
            if agent.engine.output_type == output_type
        ]

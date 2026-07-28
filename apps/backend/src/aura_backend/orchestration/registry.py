"""Agent registry and executable interface.

Common protocol for all agents regardless of implementation.
Capability-driven agent selection without class binding.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set

from aura_backend.orchestration.models import (
    Capability,
    Skill,
    Task,
    TaskAttempt,
    ToolRequirement,
)


class ExecutableAgent(ABC):
    """Common interface for all agents.

    All agents (Research, Video, Script, Voice, Thumbnail, SEO, Publisher, etc.)
    implement this interface. Orchestrator invokes agents only through this interface.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique agent identifier"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> Set[Capability]:
        """What this agent can fundamentally do"""
        pass

    @property
    @abstractmethod
    def skills(self) -> Set[Skill]:
        """Specific methods/patterns this agent uses"""
        pass

    @property
    @abstractmethod
    def tool_requirements(self) -> Set[ToolRequirement]:
        """External tools/APIs this agent needs"""
        pass

    @abstractmethod
    async def can_execute(self, task: Task) -> bool:
        """Check if agent can execute this task.

        Evaluates capabilities, skills, and tool availability.
        """
        pass

    @abstractmethod
    async def execute(self, task: Task) -> TaskAttempt:
        """Execute a task and return an attempt record.

        Must be idempotent - same task input produces same output.
        Returns immutable TaskAttempt record.
        """
        pass

    @abstractmethod
    async def cancel(self, attempt_id: str) -> bool:
        """Cancel a running task attempt.

        Returns True if cancelled successfully.
        """
        pass

    def to_dict(self) -> Dict:
        """Serialize agent metadata"""
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "skills": [s.value for s in self.skills],
            "tool_requirements": [t.value for t in self.tool_requirements],
        }


class AgentRegistry:
    """Registry of available agents.

    Maintains agent instances and provides capability-based queries.
    Enables decoupled agent selection without hardcoding agent classes.
    """

    def __init__(self):
        """Initialize empty registry"""
        self._agents: Dict[str, ExecutableAgent] = {}
        self._capability_index: Dict[Capability, List[str]] = {}
        self._skill_index: Dict[Skill, List[str]] = {}

    def register(self, agent: ExecutableAgent) -> None:
        """Register an agent in the registry.

        Agent becomes available for task assignment based on capabilities.
        """
        self._agents[agent.id] = agent

        # Build capability index for fast queries
        for capability in agent.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            self._capability_index[capability].append(agent.id)

        # Build skill index for fast queries
        for skill in agent.skills:
            if skill not in self._skill_index:
                self._skill_index[skill] = []
            self._skill_index[skill].append(agent.id)

    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        if agent_id not in self._agents:
            return False

        agent = self._agents.pop(agent_id)

        # Remove from capability index
        for capability in agent.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability] = [
                    aid for aid in self._capability_index[capability]
                    if aid != agent_id
                ]

        # Remove from skill index
        for skill in agent.skills:
            if skill in self._skill_index:
                self._skill_index[skill] = [
                    aid for aid in self._skill_index[skill]
                    if aid != agent_id
                ]

        return True

    def get(self, agent_id: str) -> Optional[ExecutableAgent]:
        """Get an agent by ID"""
        return self._agents.get(agent_id)

    def list_all(self) -> List[ExecutableAgent]:
        """List all registered agents"""
        return list(self._agents.values())

    def find_by_capability(self, capability: Capability) -> List[ExecutableAgent]:
        """Find agents with a specific capability"""
        agent_ids = self._capability_index.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def find_by_skill(self, skill: Skill) -> List[ExecutableAgent]:
        """Find agents with a specific skill"""
        agent_ids = self._skill_index.get(skill, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def find_capable(
        self,
        required_capabilities: Set[Capability],
        required_skills: Optional[Set[Skill]] = None,
        required_tools: Optional[Set[ToolRequirement]] = None,
    ) -> Optional[ExecutableAgent]:
        """Find a single agent satisfying all requirements.

        Selects the first agent that has all required capabilities.
        Skills and tools are advisory (logged if missing but not required).

        Args:
            required_capabilities: Capabilities agent must have
            required_skills: Skills agent should ideally have
            required_tools: Tools agent should ideally have

        Returns:
            First capable agent, or None if no agent matches
        """
        required_skills = required_skills or set()
        required_tools = required_tools or set()

        # Find agents with all required capabilities
        candidates = None
        for capability in required_capabilities:
            agents_with_cap = set(self._capability_index.get(capability, []))
            if candidates is None:
                candidates = agents_with_cap
            else:
                candidates = candidates.intersection(agents_with_cap)

        if not candidates:
            return None

        # Return first candidate (could add scoring/ranking later)
        agent_id = next(iter(candidates))
        return self._agents.get(agent_id)

    def find_all_capable(
        self,
        required_capabilities: Set[Capability],
    ) -> List[ExecutableAgent]:
        """Find all agents with required capabilities"""
        if not required_capabilities:
            return self.list_all()

        candidates = None
        for capability in required_capabilities:
            agents_with_cap = set(self._capability_index.get(capability, []))
            if candidates is None:
                candidates = agents_with_cap
            else:
                candidates = candidates.intersection(agents_with_cap)

        if not candidates:
            return []

        return [self._agents[aid] for aid in candidates]

    def count(self) -> int:
        """Total number of registered agents"""
        return len(self._agents)

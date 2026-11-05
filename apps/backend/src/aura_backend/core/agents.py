"""
Agent framework foundation.

Provides:
- Base agent class with lifecycle
- Agent registry and management
- Agent capabilities and metadata
- Agent health monitoring
- Thread-safe agent management

Agents are autonomous actors that perform tasks in the AURA runtime.
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type
from uuid import uuid4


class AgentStatus(str, Enum):
    """Status of an agent"""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUT_DOWN = "shut_down"


@dataclass
class AgentCapability:
    """A capability provided by an agent"""

    name: str
    description: str
    version: str = "1.0.0"


@dataclass
class AgentMetadata:
    """Metadata about an agent"""

    id: str
    name: str
    agent_type: str
    version: str
    description: str
    author: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class BaseAgent(ABC):
    """
    Base class for all agents in AURA.

    Agents are autonomous actors that execute tasks. They have:
    - A lifecycle (initialize, execute, shutdown)
    - Metadata and capabilities
    - Health monitoring
    - Status tracking
    """

    def __init__(self):
        self._id = str(uuid4())
        self._status = AgentStatus.UNINITIALIZED
        self._initialized_at: Optional[datetime] = None
        self._error: Optional[str] = None
        self._execution_count = 0
        self._total_execution_time_ms = 0.0

    @abstractmethod
    def get_metadata(self) -> AgentMetadata:
        """Return agent metadata"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shut down the agent"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Return agent health status"""
        pass

    def get_capabilities(self) -> List[AgentCapability]:
        """Return capabilities provided by this agent"""
        return []

    @property
    def id(self) -> str:
        """Get agent ID"""
        return self._id

    @property
    def status(self) -> AgentStatus:
        """Get agent status"""
        return self._status

    @property
    def error(self) -> Optional[str]:
        """Get error message if agent is in error state"""
        return self._error

    async def _set_status(self, status: AgentStatus, error: Optional[str] = None) -> None:
        """Internal method to set agent status"""
        self._status = status
        self._error = error
        if status == AgentStatus.READY:
            self._initialized_at = datetime.utcnow()

    def get_status_info(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "id": self._id,
            "status": self._status.value,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "error": self._error,
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time_ms,
        }

    async def get_info(self) -> Dict[str, Any]:
        """Get complete agent information"""
        metadata = self.get_metadata()
        capabilities = self.get_capabilities()
        health = await self.health()

        return {
            **self.get_status_info(),
            "metadata": {
                "name": metadata.name,
                "type": metadata.agent_type,
                "version": metadata.version,
                "description": metadata.description,
                "author": metadata.author,
                "tags": metadata.tags,
            },
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                }
                for cap in capabilities
            ],
            "health": health,
        }


class AgentRegistry:
    """Registry for managing agents with thread-safe operations"""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._metadata: Dict[str, AgentMetadata] = {}
        self._registry_lock = threading.RLock()
        self._agents_by_type: Dict[str, List[str]] = {}
        self._agents_by_tag: Dict[str, List[str]] = {}

    def register_class(self, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class"""
        with self._registry_lock:
            if agent_type in self._agent_classes:
                raise AgentRegistrationError(f"Agent type {agent_type} already registered")
            self._agent_classes[agent_type] = agent_class

    def create_agent(self, agent_type: str, **kwargs) -> BaseAgent:
        """Create an agent instance from a registered class"""
        with self._registry_lock:
            if agent_type not in self._agent_classes:
                raise AgentRegistrationError(f"Agent type {agent_type} not found")
            agent_class = self._agent_classes[agent_type]

        agent = agent_class(**kwargs)
        return agent

    def register_instance(self, agent: BaseAgent) -> None:
        """Register an agent instance"""
        agent_id = agent.id
        metadata = agent.get_metadata()

        with self._registry_lock:
            if agent_id in self._agents:
                raise AgentRegistrationError(f"Agent {agent_id} already registered")

            self._agents[agent_id] = agent
            self._metadata[agent_id] = metadata

            agent_type = metadata.agent_type
            if agent_type not in self._agents_by_type:
                self._agents_by_type[agent_type] = []
            self._agents_by_type[agent_type].append(agent_id)

            for tag in metadata.tags:
                if tag not in self._agents_by_tag:
                    self._agents_by_tag[tag] = []
                self._agents_by_tag[tag].append(agent_id)

    def unregister(self, agent_id: str) -> bool:
        """Unregister an agent"""
        with self._registry_lock:
            if agent_id not in self._agents:
                return False

            metadata = self._metadata[agent_id]
            del self._agents[agent_id]
            del self._metadata[agent_id]

            agent_type = metadata.agent_type
            if agent_type in self._agents_by_type:
                self._agents_by_type[agent_type] = [
                    a for a in self._agents_by_type[agent_type] if a != agent_id
                ]

            for tag in metadata.tags:
                if tag in self._agents_by_tag:
                    self._agents_by_tag[tag] = [
                        a for a in self._agents_by_tag[tag] if a != agent_id
                    ]

            return True

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        with self._registry_lock:
            return self._agents.get(agent_id)

    def list(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        with self._registry_lock:
            agents_data = [
                {
                    "id": agent_id,
                    "name": self._metadata[agent_id].name,
                    "type": self._metadata[agent_id].agent_type,
                    "status": self._agents[agent_id].status.value,
                }
                for agent_id in self._agents.keys()
            ]
        return agents_data

    def find_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Find agents by type (O(1) lookup via index)"""
        with self._registry_lock:
            agent_ids = self._agents_by_type.get(agent_type, [])
            return [self._agents[agent_id] for agent_id in agent_ids if agent_id in self._agents]

    def find_by_tag(self, tag: str) -> List[BaseAgent]:
        """Find agents by tag (O(1) lookup via index)"""
        with self._registry_lock:
            agent_ids = self._agents_by_tag.get(tag, [])
            return [self._agents[agent_id] for agent_id in agent_ids if agent_id in self._agents]

    def count(self) -> int:
        """Get count of registered agents"""
        with self._registry_lock:
            return len(self._agents)

    async def initialize_all(self) -> None:
        """Initialize all registered agents with graceful degradation"""
        with self._registry_lock:
            agents_to_init = list(self._agents.values())

        failed_agents = []
        for agent in agents_to_init:
            try:
                await agent._set_status(AgentStatus.INITIALIZING)
                await agent.initialize()
                await agent._set_status(AgentStatus.READY)
            except Exception as e:
                await agent._set_status(AgentStatus.ERROR, str(e))
                failed_agents.append((agent.id, str(e)))

        if failed_agents:
            error_msg = "; ".join(f"{aid}: {err}" for aid, err in failed_agents)
            raise AgentInitializationError(f"Failed to initialize agents: {error_msg}")

    async def shutdown_all(self) -> None:
        """Shut down all registered agents in reverse order"""
        with self._registry_lock:
            agents_to_shutdown = list(reversed(list(self._agents.values())))

        for agent in agents_to_shutdown:
            try:
                await agent._set_status(AgentStatus.SHUTTING_DOWN)
                await agent.shutdown()
                await agent._set_status(AgentStatus.SHUT_DOWN)
            except Exception as e:
                await agent._set_status(AgentStatus.ERROR, str(e))

    async def health_all(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all agents"""
        with self._registry_lock:
            agents_items = list(self._agents.items())

        health = {}
        for agent_id, agent in agents_items:
            try:
                agent_health = await agent.health()
                health[agent_id] = {
                    **agent.get_status_info(),
                    **agent_health,
                }
            except Exception as e:
                health[agent_id] = {
                    **agent.get_status_info(),
                    "error": str(e),
                }
        return health

    def get_info(self) -> Dict[str, Any]:
        """Get agent registry information"""
        with self._registry_lock:
            agent_count = len(self._agents)
            registered_types = list(self._agent_classes.keys())
            agents_list = self.list()

        return {
            "agent_count": agent_count,
            "registered_types": registered_types,
            "agents": agents_list,
        }


class AgentRegistrationError(Exception):
    """Raised when agent registration fails"""

    pass


class AgentInitializationError(Exception):
    """Raised when agent initialization fails"""

    pass

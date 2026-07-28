"""
Base agent class.

All AI agents inherit from BaseAgent and implement the lifecycle.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from aura_backend.config.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Implements lifecycle:
    - initialize(): Setup and resource allocation
    - plan(): Create execution plan for goal
    - execute(): Execute plan steps
    - observe(): Analyze execution results
    - reflect(): Learn from execution
    - shutdown(): Cleanup and resource release

    Each method publishes events to the runtime event bus.
    """

    def __init__(self):
        self._id = str(uuid4())
        self._initialized = False
        self._created_at = datetime.utcnow()
        self._execution_count = 0
        self._total_execution_time_ms = 0.0
        self._event_publisher = None

    @property
    def id(self) -> str:
        """Agent ID"""
        return self._id

    @property
    def is_initialized(self) -> bool:
        """Whether agent is initialized"""
        return self._initialized

    def set_event_publisher(self, publisher: Any) -> None:
        """Set the event publisher for lifecycle events"""
        self._event_publisher = publisher

    async def initialize(self) -> None:
        """
        Initialize the agent.

        Setup resources, connect to providers, etc.
        Publishes initialize_started event.
        """
        if self._initialized:
            logger.warning(f"Agent {self.id} already initialized")
            return

        try:
            logger.info(f"agent_initializing", extra={"agent_id": self.id})
            await self._initialize_impl()
            self._initialized = True
            logger.info(f"agent_initialized", extra={"agent_id": self.id})
        except Exception as e:
            logger.error(f"agent_initialization_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def shutdown(self) -> None:
        """
        Shutdown the agent.

        Release resources, close connections, etc.
        """
        try:
            logger.info(f"agent_shutting_down", extra={"agent_id": self.id})
            await self._shutdown_impl()
            self._initialized = False
            logger.info(f"agent_shut_down", extra={"agent_id": self.id})
        except Exception as e:
            logger.error(f"agent_shutdown_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def plan(self, goal: Any, context: Any) -> Dict[str, Any]:
        """
        Create execution plan for a goal.

        Args:
            goal: Goal to plan for
            context: Agent execution context

        Returns:
            Plan dictionary with steps
        """
        try:
            logger.info(f"agent_planning", extra={"agent_id": self.id, "goal": str(goal)})
            plan = await self._plan_impl(goal, context)
            logger.info(f"agent_plan_created", extra={"agent_id": self.id, "steps": len(plan.get("steps", []))})
            return plan
        except Exception as e:
            logger.error(f"agent_planning_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def execute(self, plan: Any, context: Any) -> Dict[str, Any]:
        """
        Execute a plan.

        Args:
            plan: Execution plan
            context: Execution context

        Returns:
            Execution result
        """
        start_time = datetime.utcnow()
        try:
            logger.info(f"agent_executing", extra={"agent_id": self.id})
            result = await self._execute_impl(plan, context)
            self._execution_count += 1
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._total_execution_time_ms += duration
            logger.info(f"agent_execution_completed", extra={"agent_id": self.id, "duration_ms": duration})
            return result
        except Exception as e:
            logger.error(f"agent_execution_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def observe(self, execution_result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Analyze execution results.

        Args:
            execution_result: Result from execution
            context: Execution context

        Returns:
            Observations and analysis
        """
        try:
            logger.info(f"agent_observing", extra={"agent_id": self.id})
            observations = await self._observe_impl(execution_result, context)
            logger.info(f"agent_observation_recorded", extra={"agent_id": self.id})
            return observations
        except Exception as e:
            logger.error(f"agent_observation_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def reflect(self, observations: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Learn from execution.

        Args:
            observations: Observations from execution
            context: Execution context

        Returns:
            Reflection and insights
        """
        try:
            logger.info(f"agent_reflecting", extra={"agent_id": self.id})
            insights = await self._reflect_impl(observations, context)
            logger.info(f"agent_reflection_completed", extra={"agent_id": self.id})
            return insights
        except Exception as e:
            logger.error(f"agent_reflection_failed", extra={"agent_id": self.id, "error": str(e)})
            raise

    async def health(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            "status": "healthy" if self._initialized else "uninitialized",
            "id": self.id,
            "initialized": self._initialized,
            "execution_count": self._execution_count,
            "avg_execution_time_ms": (
                self._total_execution_time_ms / self._execution_count
                if self._execution_count > 0
                else 0.0
            ),
        }

    async def get_info(self) -> Dict[str, Any]:
        """Get complete agent information"""
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "initialized": self._initialized,
            "created_at": self._created_at.isoformat(),
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time_ms,
            "health": await self.health(),
        }

    # Lifecycle implementation methods - subclasses override these

    async def _initialize_impl(self) -> None:
        """Implementation of initialization - override in subclasses"""
        pass

    async def _shutdown_impl(self) -> None:
        """Implementation of shutdown - override in subclasses"""
        pass

    async def _plan_impl(self, goal: Any, context: Any) -> Dict[str, Any]:
        """Implementation of planning - override in subclasses"""
        return {"steps": []}

    async def _execute_impl(self, plan: Any, context: Any) -> Dict[str, Any]:
        """Implementation of execution - override in subclasses"""
        return {"success": False}

    async def _observe_impl(self, execution_result: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Implementation of observation - override in subclasses"""
        return {}

    async def _reflect_impl(self, observations: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Implementation of reflection - override in subclasses"""
        return {}

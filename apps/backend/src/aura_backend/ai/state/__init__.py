"""
Agent state machine.

Defines valid states and transitions for agent execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AgentState(str, Enum):
    """Agent execution state"""

    IDLE = "idle"
    PLANNING = "planning"
    WAITING = "waiting"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""

    pass


# Valid state transitions
VALID_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.IDLE: {
        AgentState.PLANNING,
        AgentState.CANCELLED,
    },
    AgentState.PLANNING: {
        AgentState.WAITING,
        AgentState.EXECUTING,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.WAITING: {
        AgentState.EXECUTING,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.EXECUTING: {
        AgentState.REFLECTING,
        AgentState.WAITING,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.REFLECTING: {
        AgentState.EXECUTING,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.COMPLETED: {
        AgentState.IDLE,
    },
    AgentState.FAILED: {
        AgentState.PLANNING,
        AgentState.IDLE,
    },
    AgentState.CANCELLED: {
        AgentState.IDLE,
    },
}


@dataclass
class StateTransition:
    """Record of a state transition"""

    from_state: AgentState
    to_state: AgentState
    timestamp: datetime = None
    reason: str = ""
    metadata: dict = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class StateMachine:
    """
    Agent state machine with transition validation.

    Prevents invalid state transitions and tracks history.
    """

    def __init__(self, initial_state: AgentState = AgentState.IDLE):
        self._current_state = initial_state
        self._history: list[StateTransition] = []
        self._created_at = datetime.utcnow()

    @property
    def current_state(self) -> AgentState:
        """Get current state"""
        return self._current_state

    @property
    def history(self) -> list[StateTransition]:
        """Get transition history"""
        return self._history.copy()

    def can_transition_to(self, target_state: AgentState) -> bool:
        """Check if transition is valid"""
        return target_state in VALID_TRANSITIONS.get(self._current_state, set())

    def transition_to(
        self,
        target_state: AgentState,
        reason: str = "",
        metadata: dict = None
    ) -> None:
        """
        Transition to a new state.

        Raises StateTransitionError if transition is invalid.
        """
        if not self.can_transition_to(target_state):
            raise StateTransitionError(
                f"Cannot transition from {self._current_state.value} "
                f"to {target_state.value}"
            )

        transition = StateTransition(
            from_state=self._current_state,
            to_state=target_state,
            reason=reason,
            metadata=metadata or {},
        )

        self._history.append(transition)
        self._current_state = target_state

    def get_valid_next_states(self) -> set[AgentState]:
        """Get all valid next states from current state"""
        return VALID_TRANSITIONS.get(self._current_state, set()).copy()

    def reset(self) -> None:
        """Reset to initial state"""
        if self._current_state != AgentState.IDLE:
            self.transition_to(AgentState.IDLE, reason="reset")

    def duration_ms(self) -> float:
        """Get duration since creation"""
        return (datetime.utcnow() - self._created_at).total_seconds() * 1000

    def time_in_state_ms(self) -> float:
        """Get duration in current state"""
        if not self._history:
            return self.duration_ms()
        last_transition = self._history[-1]
        return (datetime.utcnow() - last_transition.timestamp).total_seconds() * 1000

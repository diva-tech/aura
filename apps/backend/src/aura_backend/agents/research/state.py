"""State machine for ResearchAgent."""

from enum import Enum
from typing import Dict, Set


class AgentState(str, Enum):
    """Agent execution state"""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchAgentState:
    """State machine for ResearchAgent with explicit transitions"""

    # Valid state transitions
    TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
        AgentState.IDLE: {AgentState.PLANNING, AgentState.CANCELLED},
        AgentState.PLANNING: {AgentState.EXECUTING, AgentState.FAILED, AgentState.CANCELLED},
        AgentState.EXECUTING: {AgentState.REFLECTING, AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED},
        AgentState.REFLECTING: {AgentState.EXECUTING, AgentState.REPLANNING, AgentState.COMPLETED, AgentState.FAILED},
        AgentState.REPLANNING: {AgentState.EXECUTING, AgentState.FAILED, AgentState.CANCELLED},
        AgentState.COMPLETED: set(),
        AgentState.FAILED: set(),
        AgentState.CANCELLED: set(),
    }

    def __init__(self, initial_state: AgentState = AgentState.IDLE):
        self.current_state = initial_state
        self.history: list[AgentState] = [initial_state]

    def transition(self, next_state: AgentState) -> bool:
        """Attempt state transition"""
        if next_state not in self.TRANSITIONS.get(self.current_state, set()):
            return False
        self.current_state = next_state
        self.history.append(next_state)
        return True

    def is_terminal(self) -> bool:
        return self.current_state in {AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED}

    def can_continue(self) -> bool:
        return not self.is_terminal()

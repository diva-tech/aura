"""
AURA AI Framework.

Comprehensive framework for building AI agents without implementation details.
Provides:
- Goal and planning abstractions
- Memory interfaces
- Tool framework
- Provider contracts
- Execution engine
- Prompt system
- Lifecycle management
- Event integration
"""

from aura_backend.ai.agents import BaseAgent
from aura_backend.ai.context import AgentContext, ExecutionStep
from aura_backend.ai.goals import Goal, GoalPriority, GoalStatus, GoalResult, GoalMetadata
from aura_backend.ai.memory import WorkingMemory, LongTermMemory, SemanticMemory, EpisodicMemory, ConversationMemory, MemoryStore
from aura_backend.ai.state import AgentState, StateMachine, StateTransitionError
from aura_backend.ai.tools import Tool, ToolRegistry, ToolCapability, ToolParameter, ToolResult
from aura_backend.ai.providers import LLMProvider, VisionProvider, EmbeddingProvider, SpeechProvider, ImageGenerationProvider, PromptRenderer
from aura_backend.ai.execution import ExecutionContext, ExecutionPipeline, ExecutionPolicy, ExecutionResult
from aura_backend.ai.planning import Planner, Plan, PlanStep, PlanResult, ExecutionStrategy
from aura_backend.ai.prompts import PromptTemplate, PromptLibrary, PromptVariables, PromptVersion
from aura_backend.ai.sessions import Session, SessionManager, SessionStatus

__all__ = [
    "BaseAgent",
    "AgentContext",
    "ExecutionStep",
    "Goal",
    "GoalPriority",
    "GoalStatus",
    "GoalResult",
    "GoalMetadata",
    "WorkingMemory",
    "LongTermMemory",
    "SemanticMemory",
    "EpisodicMemory",
    "ConversationMemory",
    "MemoryStore",
    "AgentState",
    "StateMachine",
    "StateTransitionError",
    "Tool",
    "ToolRegistry",
    "ToolCapability",
    "ToolParameter",
    "ToolResult",
    "LLMProvider",
    "VisionProvider",
    "EmbeddingProvider",
    "SpeechProvider",
    "ImageGenerationProvider",
    "PromptRenderer",
    "ExecutionContext",
    "ExecutionPipeline",
    "ExecutionPolicy",
    "ExecutionResult",
    "Planner",
    "Plan",
    "PlanStep",
    "PlanResult",
    "ExecutionStrategy",
    "PromptTemplate",
    "PromptLibrary",
    "PromptVariables",
    "PromptVersion",
    "Session",
    "SessionManager",
    "SessionStatus",
]

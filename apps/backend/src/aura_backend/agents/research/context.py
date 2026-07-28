"""Execution context for ResearchAgent."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ExecutionContext:
    """Maintains execution state and working memory"""

    goal_id: str
    goal_description: str

    working_memory: Dict[str, Any] = field(default_factory=dict)
    tool_outputs: Dict[str, Any] = field(default_factory=dict)
    llm_responses: List[Dict[str, Any]] = field(default_factory=list)

    current_step_id: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)

    total_tokens_used: int = 0
    total_cost: float = 0.0
    planning_time_ms: float = 0.0
    execution_time_ms: float = 0.0
    reflection_time_ms: float = 0.0

    reflection_count: int = 0
    replan_count: int = 0
    tool_call_count: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_tool_output(self, tool_name: str, output: Any) -> None:
        key = f"{tool_name}_{len(self.tool_outputs)}"
        self.tool_outputs[key] = {
            "tool": tool_name,
            "output": output,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def add_llm_response(self, response: Dict[str, Any]) -> None:
        self.llm_responses.append({
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def update_memory(self, key: str, value: Any) -> None:
        self.working_memory[key] = value
        self.last_updated_at = datetime.utcnow()

    def get_memory(self, key: str, default: Any = None) -> Any:
        return self.working_memory.get(key, default)

    def summary(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "steps_completed": len(self.completed_steps),
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "planning_time_ms": self.planning_time_ms,
            "execution_time_ms": self.execution_time_ms,
            "reflection_time_ms": self.reflection_time_ms,
            "tool_calls": self.tool_call_count,
            "reflections": self.reflection_count,
            "replans": self.replan_count,
        }

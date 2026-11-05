"""Execution policies evaluated before agent execution."""

from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class ExecutionPolicy:
    """Policies that constrain agent execution"""

    # Token constraints
    max_tokens: Optional[int] = None  # Max tokens for single execution
    max_total_tokens: Optional[int] = None  # Max tokens for goal

    # Time constraints
    max_runtime_seconds: Optional[int] = None  # Max execution time
    timeout_seconds: Optional[int] = 3600  # Hard timeout (1 hour default)

    # Cost constraints
    max_cost_dollars: Optional[float] = None  # Max monetary cost
    cost_alert_threshold: Optional[float] = None  # Alert when approaching limit

    # Retry constraints
    max_retries: int = 3
    max_retry_cost_dollars: Optional[float] = None

    # Tool constraints
    max_tool_calls: Optional[int] = None
    allowed_tools: Optional[Set[str]] = None  # If set, only these tools allowed
    blocked_tools: Set[str] = field(default_factory=set)

    # Provider constraints
    allowed_providers: Optional[Set[str]] = None  # If set, only these providers
    blocked_providers: Set[str] = field(default_factory=set)

    # Approval constraints
    approval_required: bool = False
    approval_timeout_seconds: int = 3600

    def is_compliant(self, execution_stats: dict) -> bool:
        """Check if execution stats comply with this policy"""
        if self.max_tokens and execution_stats.get("tokens_used", 0) > self.max_tokens:
            return False

        if self.max_cost_dollars and execution_stats.get("cost", 0) > self.max_cost_dollars:
            return False

        if self.max_tool_calls and execution_stats.get("tool_calls", 0) > self.max_tool_calls:
            return False

        return True

    def to_dict(self) -> dict:
        return {
            "max_tokens": self.max_tokens,
            "max_total_tokens": self.max_total_tokens,
            "max_runtime_seconds": self.max_runtime_seconds,
            "timeout_seconds": self.timeout_seconds,
            "max_cost_dollars": self.max_cost_dollars,
            "max_retries": self.max_retries,
            "max_tool_calls": self.max_tool_calls,
            "approval_required": self.approval_required,
        }


@dataclass
class MemoryPolicy:
    """Policies governing memory storage and lifecycle"""

    # Size constraints
    max_working_memory_items: int = 50
    max_short_term_items: int = 200
    max_episodic_items: int = 10000
    max_semantic_items: int = 100000
    max_procedural_items: int = 5000

    # Context constraints
    max_context_tokens: int = 8000  # For LLM context building
    max_working_memory_tokens: int = 2000

    # Retention policies
    working_memory_ttl_minutes: int = 30
    short_term_memory_ttl_hours: int = 24
    conversation_memory_ttl_days: int = 30

    # Importance thresholds
    min_importance_to_retain: float = 0.1  # Below this, can be forgotten
    min_importance_to_include_in_context: float = 0.5

    # Archival policies
    archive_after_days: Optional[int] = 90
    auto_archive_low_importance: bool = True
    auto_archive_threshold: float = 0.2

    def should_retain(self, importance: float, age_days: int) -> bool:
        """Determine if memory should be retained"""
        if importance < self.min_importance_to_retain:
            return False

        if self.archive_after_days and age_days > self.archive_after_days:
            if self.auto_archive_low_importance and importance < self.auto_archive_threshold:
                return False

        return True

    def to_dict(self) -> dict:
        return {
            "max_working_memory_items": self.max_working_memory_items,
            "max_short_term_items": self.max_short_term_items,
            "max_context_tokens": self.max_context_tokens,
            "working_memory_ttl_minutes": self.working_memory_ttl_minutes,
            "short_term_memory_ttl_hours": self.short_term_memory_ttl_hours,
        }

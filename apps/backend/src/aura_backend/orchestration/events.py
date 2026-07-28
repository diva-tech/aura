"""Orchestration events for observability.

12 event types covering full task lifecycle and coordination.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class OrchestrationEvent:
    """Base orchestration event"""
    event_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskCreatedEvent(OrchestrationEvent):
    """Task created in execution plan"""
    task_id: str = ""
    goal: str = ""
    priority: int = 0


@dataclass
class TaskStartedEvent(OrchestrationEvent):
    """Task execution started"""
    task_id: str = ""
    agent_id: str = ""


@dataclass
class TaskPausedEvent(OrchestrationEvent):
    """Task execution paused"""
    task_id: str = ""
    reason: str = ""


@dataclass
class TaskResumedEvent(OrchestrationEvent):
    """Task execution resumed"""
    task_id: str = ""


@dataclass
class TaskCompletedEvent(OrchestrationEvent):
    """Task execution completed successfully"""
    task_id: str = ""
    result: str = ""
    duration_seconds: float = 0.0


@dataclass
class TaskFailedEvent(OrchestrationEvent):
    """Task execution failed"""
    task_id: str = ""
    error: str = ""
    attempt_number: int = 1


@dataclass
class TaskCancelledEvent(OrchestrationEvent):
    """Task execution cancelled"""
    task_id: str = ""
    reason: str = ""


@dataclass
class AgentAssignedEvent(OrchestrationEvent):
    """Agent assigned to task"""
    task_id: str = ""
    agent_id: str = ""
    capabilities: list = field(default_factory=list)


@dataclass
class CheckpointCreatedEvent(OrchestrationEvent):
    """Execution checkpoint saved"""
    checkpoint_id: str = ""
    task_id: str = ""
    state_snapshot: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalRequestedEvent(OrchestrationEvent):
    """Human approval requested"""
    task_id: str = ""
    approval_required_for: str = ""


@dataclass
class ApprovalGrantedEvent(OrchestrationEvent):
    """Human approval granted"""
    task_id: str = ""
    approved_by: str = ""


@dataclass
class ApprovalRejectedEvent(OrchestrationEvent):
    """Human approval rejected"""
    task_id: str = ""
    rejected_by: str = ""
    reason: str = ""

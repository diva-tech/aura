"""M14 Phase 3: Learning Orchestration – Stages and Failures.

Immutable models for learning pipeline stages and failure handling.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class StageType(StrEnum):
    """Learning pipeline stage types."""

    VALIDATE = "validate"
    AUTH = "authenticate"
    RETRIEVE_METRICS = "retrieve_metrics"
    ANALYZE_RETENTION = "analyze_retention"
    ANALYZE_AUDIENCE = "analyze_audience"
    ANALYZE_REVENUE = "analyze_revenue"
    GENERATE_RECOMMENDATIONS = "generate_recommendations"
    UPDATE_PROFILE = "update_profile"
    UPDATE_MEMORY = "update_memory"
    FINALIZE = "finalize"


class LearningStageStatus(StrEnum):
    """Learning stage execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class LearningStage:
    """A stage in the learning pipeline."""

    id: str = ""
    job_id: str = ""
    stage_type: StageType = StageType.VALIDATE
    status: LearningStageStatus = LearningStageStatus.PENDING
    platform: str = ""
    provider_name: str = ""
    depends_on: tuple[str, ...] = None
    is_optional: bool = False
    objectives: tuple[str, ...] = None
    inputs: dict = None
    outputs: dict = None
    retry_policy: dict | None = None
    fallback_provider: str | None = None
    created_at: datetime = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.depends_on is None:
            object.__setattr__(self, "depends_on", ())
        if self.objectives is None:
            object.__setattr__(self, "objectives", ())
        if self.inputs is None:
            object.__setattr__(self, "inputs", {})
        if self.outputs is None:
            object.__setattr__(self, "outputs", {})
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "platform": self.platform,
            "provider_name": self.provider_name,
            "depends_on": list(self.depends_on) if self.depends_on else [],
            "is_optional": self.is_optional,
            "objectives": list(self.objectives) if self.objectives else [],
            "inputs": self.inputs or {},
            "outputs": self.outputs or {},
            "retry_policy": self.retry_policy,
            "fallback_provider": self.fallback_provider,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass(frozen=True)
class LearningFailure:
    """Structured learning failure record."""

    id: str = ""
    job_id: str = ""
    stage_id: str = ""
    stage_type: StageType = StageType.VALIDATE
    platform: str = ""
    provider_name: str = ""
    objective: str = ""
    exception_type: str = ""
    error_message: str = ""
    is_recoverable: bool = False
    retry_count: int = 0
    max_retries: int = 3
    fallback_provider: str | None = None
    can_use_fallback: bool = False
    diagnostics: dict = None
    timestamp: datetime = None

    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, "id", str(uuid4()))
        if self.diagnostics is None:
            object.__setattr__(self, "diagnostics", {})
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "stage_id": self.stage_id,
            "stage_type": self.stage_type.value,
            "platform": self.platform,
            "provider_name": self.provider_name,
            "objective": self.objective,
            "exception_type": self.exception_type,
            "error_message": self.error_message,
            "is_recoverable": self.is_recoverable,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "fallback_provider": self.fallback_provider,
            "can_use_fallback": self.can_use_fallback,
            "diagnostics": self.diagnostics or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

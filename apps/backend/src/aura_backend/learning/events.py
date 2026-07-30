"""M14 Phase 3: Learning Orchestration – Lifecycle Events.

Immutable events for learning pipeline execution tracking.
"""

from dataclasses import dataclass
from datetime import datetime

from .stages import LearningFailure, StageType


@dataclass(frozen=True)
class LearningEvent:
    """Base learning event."""

    event_id: str = ""
    job_id: str = ""
    event_type: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.utcnow())

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "job_id": self.job_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass(frozen=True)
class LearningStarted(LearningEvent):
    """Learning job started event."""

    stage_count: int = 0
    platforms: tuple[str, ...] = None

    def __post_init__(self):
        if self.platforms is None:
            object.__setattr__(self, "platforms", ())
        super().__post_init__()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_count": self.stage_count,
                "platforms": list(self.platforms) if self.platforms else [],
            }
        )
        return d


@dataclass(frozen=True)
class StageStarted(LearningEvent):
    """Learning stage started event."""

    stage_type: StageType = StageType.VALIDATE
    stage_id: str = ""
    platform: str = ""
    provider_name: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_type": self.stage_type.value,
                "stage_id": self.stage_id,
                "platform": self.platform,
                "provider_name": self.provider_name,
            }
        )
        return d


@dataclass(frozen=True)
class StageCompleted(LearningEvent):
    """Learning stage completed event."""

    stage_type: StageType = StageType.VALIDATE
    stage_id: str = ""
    duration_seconds: float = 0.0
    output_data: dict = None

    def __post_init__(self):
        if self.output_data is None:
            object.__setattr__(self, "output_data", {})
        super().__post_init__()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_type": self.stage_type.value,
                "stage_id": self.stage_id,
                "duration_seconds": self.duration_seconds,
                "output_data": self.output_data or {},
            }
        )
        return d


@dataclass(frozen=True)
class StageFailed(LearningEvent):
    """Learning stage failed event."""

    failure: LearningFailure | None = None
    will_retry: bool = False
    retry_count: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "failure": self.failure.to_dict() if self.failure else None,
                "will_retry": self.will_retry,
                "retry_count": self.retry_count,
            }
        )
        return d


@dataclass(frozen=True)
class LearningCompleted(LearningEvent):
    """Learning job completed event."""

    is_success: bool = False
    successful_platforms: tuple[str, ...] = None
    failed_platforms: tuple[str, ...] = None
    recommendations_generated: int = 0
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.successful_platforms is None:
            object.__setattr__(self, "successful_platforms", ())
        if self.failed_platforms is None:
            object.__setattr__(self, "failed_platforms", ())
        super().__post_init__()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "is_success": self.is_success,
                "successful_platforms": (
                    list(self.successful_platforms) if self.successful_platforms else []
                ),
                "failed_platforms": list(self.failed_platforms) if self.failed_platforms else [],
                "recommendations_generated": self.recommendations_generated,
                "duration_seconds": self.duration_seconds,
            }
        )
        return d


@dataclass(frozen=True)
class LearningMetricsEvent(LearningEvent):
    """Learning metrics snapshot event."""

    job_id: str = ""
    stage_count: int = 0
    completed_stages: int = 0
    failed_stages: int = 0
    recommendations_count: int = 0
    average_confidence: float = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_count": self.stage_count,
                "completed_stages": self.completed_stages,
                "failed_stages": self.failed_stages,
                "recommendations_count": self.recommendations_count,
                "average_confidence": self.average_confidence,
            }
        )
        return d

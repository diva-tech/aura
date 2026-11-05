"""M13 Phase 3: Publishing Orchestration — Lifecycle Events.

Immutable event models for publishing lifecycle tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .models import PublishingMetrics
from .stages import PublishingFailure


@dataclass(frozen=True)
class PublishingEvent:
    """Base publishing event"""

    event_id: str = ""
    job_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: str = ""

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "job_id": self.job_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class PublishingStarted(PublishingEvent):
    """Publishing job started"""

    event_type: str = "publishing_started"
    stage_count: int = 0
    platforms: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"stage_count": self.stage_count, "platforms": self.platforms})
        return d


@dataclass(frozen=True)
class StageStarted(PublishingEvent):
    """Publishing stage started"""

    event_type: str = "stage_started"
    stage_type: str = ""
    stage_id: str = ""
    platform: str = ""
    provider: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_type": self.stage_type,
                "stage_id": self.stage_id,
                "platform": self.platform,
                "provider": self.provider,
            }
        )
        return d


@dataclass(frozen=True)
class StageCompleted(PublishingEvent):
    """Publishing stage completed"""

    event_type: str = "stage_completed"
    stage_type: str = ""
    stage_id: str = ""
    platform: str = ""
    duration_seconds: float = 0.0
    output_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_type": self.stage_type,
                "stage_id": self.stage_id,
                "platform": self.platform,
                "duration_seconds": self.duration_seconds,
            }
        )
        return d


@dataclass(frozen=True)
class StageFailed(PublishingEvent):
    """Publishing stage failed"""

    event_type: str = "stage_failed"
    stage_type: str = ""
    stage_id: str = ""
    platform: str = ""
    failure: PublishingFailure | None = None
    will_retry: bool = False
    retry_count: int = 0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "stage_type": self.stage_type,
                "stage_id": self.stage_id,
                "platform": self.platform,
                "will_retry": self.will_retry,
                "retry_count": self.retry_count,
                "failure": self.failure.to_dict() if self.failure else None,
            }
        )
        return d


@dataclass(frozen=True)
class PublishingCompleted(PublishingEvent):
    """Publishing job completed"""

    event_type: str = "publishing_completed"
    is_success: bool = False
    successful_platforms: tuple[str, ...] = ()
    failed_platforms: tuple[str, ...] = ()
    skipped_platforms: tuple[str, ...] = ()
    total_duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update(
            {
                "is_success": self.is_success,
                "successful_platforms": self.successful_platforms,
                "failed_platforms": self.failed_platforms,
                "total_duration_seconds": self.total_duration_seconds,
            }
        )
        return d


@dataclass(frozen=True)
class PublishingMetricsEvent(PublishingEvent):
    """Publishing metrics snapshot"""

    event_type: str = "publishing_metrics"
    metrics: PublishingMetrics | None = None

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["metrics"] = self.metrics.to_dict() if self.metrics else None
        return d

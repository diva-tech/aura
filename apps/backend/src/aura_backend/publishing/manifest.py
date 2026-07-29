"""M13 Phase 1: Publishing Foundation — Publishing Manifest.

Immutable manifest containing complete publishing job specification and results.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .models import PublishingJob, PublishingMetrics, PublishingTask
from .reports import JobReport, PublishingReport, PublishingSummary


@dataclass(frozen=True)
class PublishingManifest:
    """Immutable publishing manifest"""

    id: str = ""
    job: PublishingJob = field(default_factory=PublishingJob)
    tasks: tuple[PublishingTask, ...] = ()
    reports: tuple[PublishingReport, ...] = ()
    job_report: JobReport | None = None
    summary: PublishingSummary | None = None
    metrics: PublishingMetrics | None = None
    artifact_bundle_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job": self.job.to_dict(),
            "task_count": len(self.tasks),
            "report_count": len(self.reports),
            "artifact_bundle_id": self.artifact_bundle_id,
            "status": self.job.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "job_report": self.job_report.to_dict() if self.job_report else None,
            "summary": self.summary.to_dict() if self.summary else None,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }

    def get_task_count(self) -> int:
        """Get total task count"""
        return len(self.tasks)

    def get_report_count(self) -> int:
        """Get total report count"""
        return len(self.reports)

    def get_successful_tasks(self) -> tuple[PublishingTask, ...]:
        """Get successful tasks"""
        if not self.tasks or not self.reports:
            return ()
        successful_task_ids = {
            r.task_id for r in self.reports if r.publish_status.value == "published"
        }
        return tuple(t for t in self.tasks if t.id in successful_task_ids)

    def get_failed_tasks(self) -> tuple[PublishingTask, ...]:
        """Get failed tasks"""
        if not self.tasks or not self.reports:
            return ()
        failed_task_ids = {r.task_id for r in self.reports if r.publish_status.value == "failed"}
        return tuple(t for t in self.tasks if t.id in failed_task_ids)

    def get_pending_tasks(self) -> tuple[PublishingTask, ...]:
        """Get pending tasks"""
        if not self.tasks or not self.reports:
            return ()
        pending_task_ids = {
            r.task_id for r in self.reports if r.publish_status.value in ("pending", "queued")
        }
        return tuple(t for t in self.tasks if t.id in pending_task_ids)

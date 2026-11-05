"""M13 Phase 4: Publishing – Dashboard and Performance Optimization."""

from dataclasses import dataclass
from datetime import datetime

from .metrics import MetricsAggregator


@dataclass(frozen=True)
class JobProgress:
    """Job progress snapshot"""

    job_id: str = ""
    total_stages: int = 0
    completed_stages: int = 0
    failed_stages: int = 0
    progress_percent: float = 0.0
    current_stage: str = ""
    estimated_remaining_seconds: float = 0.0


class PublishingDashboard:
    """Publishing dashboard provider"""

    def __init__(self, metrics_aggregator: MetricsAggregator):
        self._metrics = metrics_aggregator
        self._active_jobs: dict[str, dict] = {}
        self._queue: list[dict] = []
        self._provider_status: dict[str, dict] = {}

    def register_job(self, job_id: str, platforms: list[str]) -> None:
        """Register job for tracking"""
        self._active_jobs[job_id] = {
            "job_id": job_id,
            "platforms": platforms,
            "created_at": datetime.utcnow(),
            "completed_stages": 0,
        }

    def get_job_progress(self, job_id: str) -> JobProgress | None:
        """Get job progress"""
        job = self._active_jobs.get(job_id)
        if not job:
            return None

        completed = job.get("completed_stages", 0)
        total = len(job.get("platforms", [])) * 7  # Rough estimate

        return JobProgress(
            job_id=job_id,
            total_stages=total,
            completed_stages=completed,
            progress_percent=(completed / total * 100) if total > 0 else 0.0,
        )

    def get_queue_status(self) -> dict:
        """Get queue status"""
        return {
            "queued_jobs": len(self._queue),
            "active_jobs": len(self._active_jobs),
            "avg_wait_seconds": self._calculate_avg_wait(),
        }

    def get_provider_status(self) -> dict[str, dict]:
        """Get provider health status"""
        return {
            provider: {
                "status": "available",
                "success_rate": status.get("success_rate", 100.0),
                "avg_duration": status.get("avg_duration", 0.0),
                "queue_depth": status.get("queue_depth", 0),
            }
            for provider, status in self._provider_status.items()
        }

    def get_dashboard_summary(self) -> dict:
        """Get dashboard summary"""
        summary = self._metrics.get_summary_report()

        return {
            "summary": summary,
            "queue": self.get_queue_status(),
            "providers": self.get_provider_status(),
            "active_jobs": len(self._active_jobs),
        }

    def _calculate_avg_wait(self) -> float:
        """Calculate average queue wait"""
        if not self._queue:
            return 0.0
        now = datetime.utcnow()
        waits = [(now - job.get("queued_at", now)).total_seconds() for job in self._queue]
        return sum(waits) / len(waits) if waits else 0.0


class PerformanceOptimizer:
    """Optimize publishing performance"""

    @staticmethod
    def select_best_provider(
        platforms: list[str],
        provider_metrics: dict[str, dict],
    ) -> str:
        """Select best provider for publishing"""
        if not provider_metrics:
            return "mock"

        best_provider = "mock"
        best_score = -1

        for provider, metrics in provider_metrics.items():
            # Score: success_rate * 100 - avg_duration
            score = metrics.get("success_rate", 0) * 100 - metrics.get("avg_duration", 0)

            if score > best_score:
                best_score = score
                best_provider = provider

        return best_provider

    @staticmethod
    def calculate_parallel_jobs(queue_depth: int, max_concurrent: int) -> int:
        """Calculate jobs to execute in parallel"""
        return min(queue_depth, max_concurrent)

    @staticmethod
    def optimize_retry_backoff(retry_count: int, base_delay: int = 1) -> int:
        """Calculate exponential backoff for retry"""
        return base_delay * (2**retry_count)

    @staticmethod
    def estimate_queue_clearance(
        queue_depth: int,
        avg_duration_seconds: float,
        concurrent_jobs: int = 1,
    ) -> float:
        """Estimate time to clear queue"""
        if concurrent_jobs <= 0 or avg_duration_seconds <= 0:
            return 0.0
        batches = (queue_depth + concurrent_jobs - 1) // concurrent_jobs
        return batches * avg_duration_seconds

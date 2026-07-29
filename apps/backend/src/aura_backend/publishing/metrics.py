"""M13 Phase 4: Publishing – Metrics Aggregation and Analysis."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean


@dataclass(frozen=True)
class ProviderMetrics:
    """Per-provider publishing metrics"""

    provider_name: str = ""
    total_jobs: int = 0
    successful_jobs: int = 0
    failed_jobs: int = 0
    avg_upload_seconds: float = 0.0
    avg_publish_seconds: float = 0.0
    avg_queue_wait_seconds: float = 0.0
    peak_queue_depth: int = 0
    retry_rate: float = 0.0
    api_latency_ms: float = 0.0
    availability_percent: float = 100.0

    @property
    def success_rate(self) -> float:
        if self.total_jobs == 0:
            return 0.0
        return (self.successful_jobs / self.total_jobs) * 100.0

    def to_dict(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "total_jobs": self.total_jobs,
            "success_rate": self.success_rate,
            "avg_upload_seconds": self.avg_upload_seconds,
            "avg_publish_seconds": self.avg_publish_seconds,
            "availability_percent": self.availability_percent,
        }


@dataclass(frozen=True)
class ThroughputMetrics:
    """Job throughput metrics"""

    period_seconds: int = 3600
    jobs_completed: int = 0
    jobs_queued: int = 0
    jobs_per_hour: float = 0.0
    avg_queue_wait_seconds: float = 0.0
    peak_concurrent_jobs: int = 0


class MetricsAggregator:
    """Aggregates and analyzes publishing metrics"""

    def __init__(self, retention_hours: int = 24):
        self._retention_hours = retention_hours
        self._metrics_history: list[dict] = []
        self._failure_history: list[dict] = []
        self._queue_stats: list[dict] = []

    def add_metrics(self, metrics: dict) -> None:
        """Add job metrics"""
        metrics["timestamp"] = datetime.utcnow()
        self._metrics_history.append(metrics)
        self._cleanup_old_metrics()

    def add_failure(self, failure: dict) -> None:
        """Add failure record"""
        failure["timestamp"] = datetime.utcnow()
        self._failure_history.append(failure)

    def add_queue_event(self, depth: int, provider: str) -> None:
        """Track queue depth over time"""
        self._queue_stats.append(
            {
                "timestamp": datetime.utcnow(),
                "depth": depth,
                "provider": provider,
            }
        )

    def get_provider_metrics(self, provider_name: str) -> ProviderMetrics | None:
        """Analyze metrics for provider"""
        provider_jobs = [m for m in self._metrics_history if m.get("provider") == provider_name]

        if not provider_jobs:
            return None

        durations = [m.get("upload_seconds", 0) for m in provider_jobs]
        successful = sum(1 for m in provider_jobs if m.get("success", False))

        return ProviderMetrics(
            provider_name=provider_name,
            total_jobs=len(provider_jobs),
            successful_jobs=successful,
            failed_jobs=len(provider_jobs) - successful,
            avg_upload_seconds=mean(durations) if durations else 0.0,
            success_rate=(successful / len(provider_jobs) * 100) if provider_jobs else 0.0,
        )

    def get_throughput_metrics(self, period_seconds: int = 3600) -> ThroughputMetrics:
        """Calculate throughput"""
        cutoff = datetime.utcnow() - timedelta(seconds=period_seconds)
        recent = [
            m for m in self._metrics_history if m.get("timestamp", datetime.utcnow()) >= cutoff
        ]

        return ThroughputMetrics(
            period_seconds=period_seconds,
            jobs_completed=len(recent),
            jobs_per_hour=(len(recent) * 3600 / period_seconds) if recent else 0.0,
        )

    def get_failure_rate(self) -> float:
        """Get overall failure rate"""
        if not self._metrics_history:
            return 0.0
        failed = sum(1 for m in self._metrics_history if not m.get("success", False))
        return (failed / len(self._metrics_history)) * 100.0

    def get_retry_statistics(self) -> dict[str, float]:
        """Analyze retry statistics"""
        retry_counts = [m.get("retry_count", 0) for m in self._metrics_history]
        if not retry_counts:
            return {"avg": 0.0, "max": 0, "total": 0}

        return {
            "avg": mean(retry_counts),
            "max": max(retry_counts),
            "total": sum(retry_counts),
        }

    def get_summary_report(self) -> dict:
        """Generate comprehensive summary"""
        throughput = self.get_throughput_metrics()
        failure_rate = self.get_failure_rate()
        retries = self.get_retry_statistics()

        return {
            "period": "1 hour",
            "jobs_completed": throughput.jobs_completed,
            "throughput_per_hour": throughput.jobs_per_hour,
            "failure_rate_percent": failure_rate,
            "avg_retries": retries.get("avg", 0.0),
            "total_retries": retries.get("total", 0),
        }

    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics beyond retention"""
        cutoff = datetime.utcnow() - timedelta(hours=self._retention_hours)
        self._metrics_history = [
            m for m in self._metrics_history if m.get("timestamp", datetime.utcnow()) >= cutoff
        ]

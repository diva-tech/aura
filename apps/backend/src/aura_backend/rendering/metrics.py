"""M12 Phase 4: Advanced Metrics Aggregation and Analysis.

Real-time metrics tracking, analysis, and provider comparison.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean
from typing import Any

from .stages import RenderFailure, RenderingMetrics


@dataclass(frozen=True)
class ProviderMetrics:
    """Metrics for a specific rendering provider"""

    provider_name: str = ""
    total_jobs: int = 0
    successful_jobs: int = 0
    failed_jobs: int = 0

    # Timing
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0

    # Resources
    avg_memory_mb: int = 0
    peak_memory_mb: int = 0
    avg_cpu_percent: float = 0.0
    avg_gpu_percent: float = 0.0

    # Reliability
    success_rate: float = 0.0
    retry_rate: float = 0.0
    avg_retries_per_failure: float = 0.0

    # Quality
    avg_validation_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "total_jobs": self.total_jobs,
            "success_rate": self.success_rate,
            "avg_duration_seconds": self.avg_duration_seconds,
            "peak_memory_mb": self.peak_memory_mb,
        }


@dataclass(frozen=True)
class ThroughputMetrics:
    """Job throughput and queue metrics"""

    period_seconds: int = 3600  # 1 hour
    jobs_completed: int = 0
    jobs_queued: int = 0
    avg_queue_time_seconds: float = 0.0
    throughput_jobs_per_hour: float = 0.0
    peak_concurrent_jobs: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "period_seconds": self.period_seconds,
            "jobs_completed": self.jobs_completed,
            "throughput_jobs_per_hour": self.throughput_jobs_per_hour,
            "avg_queue_time_seconds": self.avg_queue_time_seconds,
        }


@dataclass(frozen=True)
class ResourceUtilization:
    """System resource utilization metrics"""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    total_memory_mb: int = 0
    used_memory_mb: int = 0
    total_disk_mb: int = 0
    used_disk_mb: int = 0
    total_gpu_memory_mb: int = 0
    used_gpu_memory_mb: int = 0

    # Percentages
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    gpu_memory_percent: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "memory_percent": self.memory_percent,
            "disk_percent": self.disk_percent,
            "gpu_memory_percent": self.gpu_memory_percent,
        }


class MetricsAggregator:
    """Aggregates and analyzes rendering metrics."""

    def __init__(self, retention_hours: int = 24):
        self._retention_hours = retention_hours
        self._metrics_history: list[RenderingMetrics] = []
        self._failure_history: list[RenderFailure] = []

    def add_metrics(self, metrics: RenderingMetrics) -> None:
        """Add metrics to aggregator"""
        self._metrics_history.append(metrics)
        self._cleanup_old_metrics()

    def add_failure(self, failure: RenderFailure) -> None:
        """Add failure record"""
        self._failure_history.append(failure)
        self._cleanup_old_failures()

    def get_provider_metrics(self, provider_name: str) -> ProviderMetrics | None:
        """Analyze metrics for specific provider"""
        provider_metrics = [
            m
            for m in self._metrics_history
            if hasattr(m, "provider_name") and m.provider_name == provider_name
        ]

        if not provider_metrics:
            return None

        durations = [m.total_duration_seconds for m in provider_metrics]
        memories = [m.peak_memory_mb for m in provider_metrics]

        return ProviderMetrics(
            provider_name=provider_name,
            total_jobs=len(provider_metrics),
            successful_jobs=sum(1 for m in provider_metrics if m.validation_passed),
            failed_jobs=len(provider_metrics)
            - sum(1 for m in provider_metrics if m.validation_passed),
            avg_duration_seconds=mean(durations) if durations else 0.0,
            min_duration_seconds=min(durations) if durations else 0.0,
            max_duration_seconds=max(durations) if durations else 0.0,
            avg_memory_mb=int(mean(memories)) if memories else 0,
            peak_memory_mb=max(memories) if memories else 0,
        )

    def get_throughput_metrics(self, period_seconds: int = 3600) -> ThroughputMetrics:
        """Calculate throughput metrics"""
        cutoff = datetime.utcnow() - timedelta(seconds=period_seconds)

        recent = [m for m in self._metrics_history if m.created_at >= cutoff]

        completed = len(recent)
        durations = [m.total_duration_seconds for m in recent]

        return ThroughputMetrics(
            period_seconds=period_seconds,
            jobs_completed=completed,
            throughput_jobs_per_hour=completed * (3600 / period_seconds),
            avg_queue_time_seconds=mean(durations) if durations else 0.0,
        )

    def get_failure_rate(self) -> float:
        """Calculate overall failure rate"""
        if not self._metrics_history:
            return 0.0

        failed = sum(1 for m in self._metrics_history if not m.validation_passed)
        return (failed / len(self._metrics_history)) * 100.0

    def get_retry_statistics(self) -> dict[str, float]:
        """Analyze retry statistics"""
        retries = [m.successful_retries + m.failed_retries for m in self._metrics_history]

        if not retries:
            return {"avg": 0.0, "max": 0, "total": 0}

        return {
            "avg": mean(retries),
            "max": max(retries),
            "total": sum(retries),
        }

    def get_provider_comparison(self) -> dict[str, ProviderMetrics]:
        """Compare metrics across providers"""
        providers = set()
        for m in self._metrics_history:
            if hasattr(m, "provider_name"):
                providers.add(m.provider_name)

        comparison = {}
        for provider in providers:
            metrics = self.get_provider_metrics(provider)
            if metrics:
                comparison[provider] = metrics

        return comparison

    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics beyond retention"""
        cutoff = datetime.utcnow() - timedelta(hours=self._retention_hours)
        self._metrics_history = [m for m in self._metrics_history if m.created_at >= cutoff]

    def _cleanup_old_failures(self) -> None:
        """Remove old failures beyond retention"""
        cutoff = datetime.utcnow() - timedelta(hours=self._retention_hours)
        self._failure_history = [f for f in self._failure_history if f.timestamp >= cutoff]

    def get_summary_report(self) -> dict[str, Any]:
        """Generate comprehensive metrics summary"""
        throughput = self.get_throughput_metrics()
        failure_rate = self.get_failure_rate()
        retries = self.get_retry_statistics()
        providers = self.get_provider_comparison()

        return {
            "period": "1 hour",
            "jobs_completed": throughput.jobs_completed,
            "throughput_per_hour": throughput.throughput_jobs_per_hour,
            "failure_rate_percent": failure_rate,
            "avg_retries": retries.get("avg", 0.0),
            "total_retries": retries.get("total", 0),
            "providers": {name: metrics.to_dict() for name, metrics in providers.items()},
        }

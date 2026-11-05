"""M14 Phase 4: Operational Metrics Aggregator.

Runtime metrics for learning orchestration: latency, throughput, provider performance.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StageDurationMetric:
    """Stage execution duration metric."""

    stage_type: str
    platform: str
    duration_ms: float
    timestamp: datetime
    provider_name: str = ""
    success: bool = True


@dataclass(frozen=True)
class ProviderLatencyMetric:
    """Provider call latency metric."""

    provider_name: str
    method: str
    latency_ms: float
    timestamp: datetime
    success: bool
    error_type: str = ""


@dataclass(frozen=True)
class RecommendationMetric:
    """Recommendation generation metric."""

    job_id: str
    count: int
    avg_confidence: float
    generation_time_ms: float
    timestamp: datetime
    by_category: dict[str, int] = None

    def __post_init__(self):
        if self.by_category is None:
            object.__setattr__(self, "by_category", {})


@dataclass(frozen=True)
class ConfidenceDistribution:
    """Distribution of recommendation confidence levels."""

    timestamp: datetime
    high_confidence: int  # >= 0.8
    medium_confidence: int  # 0.5 - 0.8
    low_confidence: int  # < 0.5
    avg_confidence: float


@dataclass(frozen=True)
class ObjectiveCompletionMetric:
    """Objective completion tracking."""

    job_id: str
    objectives: dict[str, bool]  # Objective -> completed
    completion_percent: float
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "objectives": self.objectives,
            "completion_percent": self.completion_percent,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class LearningThroughputMetric:
    """Learning job throughput metric."""

    timestamp: datetime
    jobs_completed: int
    jobs_in_progress: int
    jobs_failed: int
    avg_duration_seconds: float
    success_rate: float


class OperationalMetricsAggregator:
    """Aggregate and analyze operational metrics from learning execution."""

    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self._stage_durations: list[StageDurationMetric] = []
        self._provider_latencies: list[ProviderLatencyMetric] = []
        self._recommendations: list[RecommendationMetric] = []
        self._objective_completions: list[ObjectiveCompletionMetric] = []
        self._throughput_snapshots: list[LearningThroughputMetric] = []

    def record_stage_duration(self, metric: StageDurationMetric) -> None:
        """Record stage execution duration."""
        self._stage_durations.append(metric)
        if len(self._stage_durations) > self.max_history:
            self._stage_durations = self._stage_durations[-self.max_history :]

    def record_provider_latency(self, metric: ProviderLatencyMetric) -> None:
        """Record provider call latency."""
        self._provider_latencies.append(metric)
        if len(self._provider_latencies) > self.max_history:
            self._provider_latencies = self._provider_latencies[-self.max_history :]

    def record_recommendation_metric(self, metric: RecommendationMetric) -> None:
        """Record recommendation generation metric."""
        self._recommendations.append(metric)
        if len(self._recommendations) > self.max_history:
            self._recommendations = self._recommendations[-self.max_history :]

    def record_objective_completion(self, metric: ObjectiveCompletionMetric) -> None:
        """Record objective completion."""
        self._objective_completions.append(metric)
        if len(self._objective_completions) > self.max_history:
            self._objective_completions = self._objective_completions[-self.max_history :]

    def record_throughput_snapshot(self, metric: LearningThroughputMetric) -> None:
        """Record throughput snapshot."""
        self._throughput_snapshots.append(metric)
        if len(self._throughput_snapshots) > self.max_history:
            self._throughput_snapshots = self._throughput_snapshots[-self.max_history :]

    def get_stage_duration_stats(self, stage_type: str | None = None) -> dict:
        """Get stage duration statistics."""
        durations = self._stage_durations
        if stage_type:
            durations = [d for d in durations if d.stage_type == stage_type]

        if not durations:
            return {
                "count": 0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "success_rate": 0.0,
            }

        times = [d.duration_ms for d in durations]
        successful = sum(1 for d in durations if d.success)

        return {
            "count": len(durations),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "success_rate": successful / len(durations),
            "by_platform": self._stage_duration_by_platform(durations),
        }

    def get_provider_latency_stats(self, provider_name: str | None = None) -> dict:
        """Get provider latency statistics."""
        latencies = self._provider_latencies
        if provider_name:
            latencies = [latency for latency in latencies if latency.provider_name == provider_name]

        if not latencies:
            return {
                "count": 0,
                "avg_ms": 0.0,
                "min_ms": 0.0,
                "max_ms": 0.0,
                "success_rate": 0.0,
                "by_method": {},
            }

        times = [latency.latency_ms for latency in latencies]
        successful = sum(1 for latency in latencies if latency.success)

        # Group by method
        by_method: dict[str, list[float]] = {}
        for latency in latencies:
            if latency.method not in by_method:
                by_method[latency.method] = []
            by_method[latency.method].append(latency.latency_ms)

        method_stats = {
            method: {
                "avg_ms": sum(times_list) / len(times_list),
                "count": len(times_list),
            }
            for method, times_list in by_method.items()
        }

        return {
            "count": len(latencies),
            "avg_ms": sum(times) / len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "success_rate": successful / len(latencies),
            "by_method": method_stats,
        }

    def get_recommendation_stats(self) -> dict:
        """Get recommendation generation statistics."""
        if not self._recommendations:
            return {
                "total_generated": 0,
                "avg_confidence": 0.0,
                "avg_generation_time_ms": 0.0,
                "by_category": {},
            }

        total_count = sum(r.count for r in self._recommendations)
        avg_confidence = sum(r.avg_confidence for r in self._recommendations) / len(
            self._recommendations
        )
        avg_time = sum(r.generation_time_ms for r in self._recommendations) / len(
            self._recommendations
        )

        # Aggregate by category
        category_totals: dict[str, int] = {}
        for rec in self._recommendations:
            for category, count in (rec.by_category or {}).items():
                category_totals[category] = category_totals.get(category, 0) + count

        return {
            "total_generated": total_count,
            "avg_confidence": avg_confidence,
            "avg_generation_time_ms": avg_time,
            "by_category": category_totals,
            "jobs_with_recommendations": len(self._recommendations),
        }

    def get_confidence_distribution(self) -> dict:
        """Get confidence distribution across all recommendations."""
        if not self._recommendations:
            return {
                "high": 0,
                "medium": 0,
                "low": 0,
                "avg_confidence": 0.0,
            }

        high = 0
        medium = 0
        low = 0
        total_confidence = 0.0

        for rec in self._recommendations:
            if rec.avg_confidence >= 0.8:
                high += rec.count
            elif rec.avg_confidence >= 0.5:
                medium += rec.count
            else:
                low += rec.count
            total_confidence += rec.avg_confidence

        total = high + medium + low
        avg = total_confidence / len(self._recommendations) if self._recommendations else 0

        return {
            "high": high,
            "medium": medium,
            "low": low,
            "total": total,
            "avg_confidence": avg,
            "high_percent": (high / total * 100) if total > 0 else 0,
            "medium_percent": (medium / total * 100) if total > 0 else 0,
            "low_percent": (low / total * 100) if total > 0 else 0,
        }

    def get_objective_completion_stats(self) -> dict:
        """Get objective completion statistics."""
        if not self._objective_completions:
            return {
                "jobs_completed": 0,
                "avg_completion_percent": 0.0,
                "fully_completed": 0,
            }

        fully_completed = sum(
            1 for oc in self._objective_completions if oc.completion_percent >= 100.0
        )
        avg_completion = sum(oc.completion_percent for oc in self._objective_completions) / len(
            self._objective_completions
        )

        return {
            "jobs_tracked": len(self._objective_completions),
            "avg_completion_percent": avg_completion,
            "fully_completed": fully_completed,
            "partial_completion": len(self._objective_completions) - fully_completed,
        }

    def get_throughput_stats(self) -> dict:
        """Get throughput statistics."""
        if not self._throughput_snapshots:
            return {
                "total_completed": 0,
                "total_failed": 0,
                "avg_success_rate": 0.0,
                "avg_duration_seconds": 0.0,
            }

        total_completed = sum(s.jobs_completed for s in self._throughput_snapshots)
        total_failed = sum(s.jobs_failed for s in self._throughput_snapshots)
        avg_success_rate = sum(s.success_rate for s in self._throughput_snapshots) / len(
            self._throughput_snapshots
        )
        avg_duration = sum(s.avg_duration_seconds for s in self._throughput_snapshots) / len(
            self._throughput_snapshots
        )

        return {
            "total_completed": total_completed,
            "total_failed": total_failed,
            "total_in_progress": (
                sum(s.jobs_in_progress for s in self._throughput_snapshots[-1:])
                if self._throughput_snapshots
                else 0
            ),
            "avg_success_rate": avg_success_rate,
            "avg_duration_seconds": avg_duration,
            "snapshots": len(self._throughput_snapshots),
        }

    def get_comprehensive_report(self) -> dict:
        """Get comprehensive metrics report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stage_duration": self.get_stage_duration_stats(),
            "provider_latency": self.get_provider_latency_stats(),
            "recommendations": self.get_recommendation_stats(),
            "confidence_distribution": self.get_confidence_distribution(),
            "objective_completion": self.get_objective_completion_stats(),
            "throughput": self.get_throughput_stats(),
        }

    def _stage_duration_by_platform(self, durations: list[StageDurationMetric]) -> dict[str, dict]:
        """Get stage duration breakdown by platform."""
        by_platform: dict[str, list[float]] = {}
        for duration in durations:
            if duration.platform not in by_platform:
                by_platform[duration.platform] = []
            by_platform[duration.platform].append(duration.duration_ms)

        return {
            platform: {
                "avg_ms": sum(times) / len(times),
                "count": len(times),
            }
            for platform, times in by_platform.items()
        }

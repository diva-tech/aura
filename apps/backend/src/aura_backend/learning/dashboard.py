"""M14 Phase 4: Learning Dashboard – Operational Monitoring.

Real-time dashboard for learning queue, provider health, analytics progress.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ProviderHealthStatus(StrEnum):
    """Provider health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProviderHealth:
    """Provider health snapshot."""

    provider_name: str
    status: ProviderHealthStatus
    last_check: datetime
    success_rate: float
    avg_latency_ms: float
    total_requests: int
    failed_requests: int
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "provider_name": self.provider_name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "error_message": self.error_message,
        }


@dataclass(frozen=True)
class LearningQueueItem:
    """Item in learning execution queue."""

    job_id: str
    creator_id: str
    platform: str
    queued_at: datetime
    estimated_duration_seconds: int
    priority: int = 0  # Higher = more urgent


@dataclass(frozen=True)
class AnalyticsProgress:
    """Progress tracking for analytics collection."""

    job_id: str
    platform: str
    stage_type: str
    progress_percent: int
    started_at: datetime
    estimated_completion: datetime | None = None
    current_step: str = ""


@dataclass(frozen=True)
class RecommendationSummary:
    """Summary of generated recommendations."""

    job_id: str
    total_count: int
    high_priority: int
    medium_priority: int
    low_priority: int
    avg_confidence: float
    categories: dict[str, int]  # Category -> count

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "total_count": self.total_count,
            "high_priority": self.high_priority,
            "medium_priority": self.medium_priority,
            "low_priority": self.low_priority,
            "avg_confidence": self.avg_confidence,
            "categories": self.categories,
        }


@dataclass(frozen=True)
class CreatorProfileEvolution:
    """Creator profile changes over time."""

    creator_id: str
    timestamp: datetime
    profile_version: int
    fields_updated: int
    learning_version: str = ""
    avg_video_length_change: float = 0.0
    topic_diversity_change: float = 0.0

    def to_dict(self) -> dict:
        return {
            "creator_id": self.creator_id,
            "timestamp": self.timestamp.isoformat(),
            "profile_version": self.profile_version,
            "fields_updated": self.fields_updated,
            "learning_version": self.learning_version,
            "avg_video_length_change": self.avg_video_length_change,
            "topic_diversity_change": self.topic_diversity_change,
        }


@dataclass(frozen=True)
class MemoryStatistics:
    """Learning memory usage statistics."""

    creator_id: str
    total_experiments: int
    recent_experiments: int
    total_recommendations_seen: int
    accepted_recommendations: int
    acceptance_rate: float
    last_optimization: datetime | None = None
    memory_size_kb: float = 0.0

    def to_dict(self) -> dict:
        return {
            "creator_id": self.creator_id,
            "total_experiments": self.total_experiments,
            "recent_experiments": self.recent_experiments,
            "total_recommendations_seen": self.total_recommendations_seen,
            "accepted_recommendations": self.accepted_recommendations,
            "acceptance_rate": self.acceptance_rate,
            "last_optimization": (
                self.last_optimization.isoformat() if self.last_optimization else None
            ),
            "memory_size_kb": self.memory_size_kb,
        }


class LearningDashboard:
    """Real-time learning dashboard for operations monitoring."""

    def __init__(self):
        self._queue: list[LearningQueueItem] = []
        self._provider_health: dict[str, ProviderHealth] = {}
        self._analytics_progress: dict[str, AnalyticsProgress] = {}
        self._recommendations: dict[str, RecommendationSummary] = {}
        self._creator_evolution: dict[str, CreatorProfileEvolution] = {}
        self._memory_stats: dict[str, MemoryStatistics] = {}

    def add_to_queue(self, item: LearningQueueItem) -> None:
        """Add job to learning queue."""
        self._queue.append(item)
        self._queue.sort(key=lambda x: x.priority, reverse=True)

    def get_queue(self, limit: int = 50) -> list[LearningQueueItem]:
        """Get learning queue."""
        return self._queue[:limit]

    def remove_from_queue(self, job_id: str) -> None:
        """Remove job from queue."""
        self._queue = [item for item in self._queue if item.job_id != job_id]

    def update_provider_health(self, health: ProviderHealth) -> None:
        """Update provider health status."""
        self._provider_health[health.provider_name] = health

    def get_provider_health(self) -> dict[str, ProviderHealth]:
        """Get all provider health status."""
        return dict(self._provider_health)

    def get_healthy_providers(self) -> list[str]:
        """Get list of healthy providers."""
        return [
            name
            for name, health in self._provider_health.items()
            if health.status == ProviderHealthStatus.HEALTHY
        ]

    def update_analytics_progress(self, progress: AnalyticsProgress) -> None:
        """Update analytics collection progress."""
        self._analytics_progress[progress.job_id] = progress

    def get_analytics_progress(self, job_id: str) -> AnalyticsProgress | None:
        """Get analytics progress for job."""
        return self._analytics_progress.get(job_id)

    def get_all_progress(self) -> list[AnalyticsProgress]:
        """Get all active analytics progress."""
        return list(self._analytics_progress.values())

    def update_recommendations(self, summary: RecommendationSummary) -> None:
        """Update recommendation summary."""
        self._recommendations[summary.job_id] = summary

    def get_recommendations(self, job_id: str) -> RecommendationSummary | None:
        """Get recommendations for job."""
        return self._recommendations.get(job_id)

    def update_creator_evolution(self, evolution: CreatorProfileEvolution) -> None:
        """Update creator profile evolution."""
        key = f"{evolution.creator_id}:{evolution.timestamp.isoformat()}"
        self._creator_evolution[key] = evolution

    def get_creator_history(
        self, creator_id: str, limit: int = 10
    ) -> list[CreatorProfileEvolution]:
        """Get creator profile evolution history."""
        evolutions = [e for e in self._creator_evolution.values() if e.creator_id == creator_id]
        evolutions.sort(key=lambda x: x.timestamp, reverse=True)
        return evolutions[:limit]

    def update_memory_statistics(self, stats: MemoryStatistics) -> None:
        """Update learning memory statistics."""
        self._memory_stats[stats.creator_id] = stats

    def get_memory_statistics(self, creator_id: str) -> MemoryStatistics | None:
        """Get memory statistics for creator."""
        return self._memory_stats.get(creator_id)

    def get_dashboard_snapshot(self) -> dict:
        """Get complete dashboard snapshot."""
        queue_size = len(self._queue)
        avg_queue_priority = (
            sum(item.priority for item in self._queue) / queue_size if queue_size > 0 else 0
        )

        provider_stats = {name: health.to_dict() for name, health in self._provider_health.items()}

        healthy_count = len(self.get_healthy_providers())
        total_providers = len(self._provider_health)

        active_jobs = len(self._analytics_progress)
        avg_progress = (
            sum(p.progress_percent for p in self._analytics_progress.values()) / active_jobs
            if active_jobs > 0
            else 0
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "queue": {
                "size": queue_size,
                "avg_priority": avg_queue_priority,
                "items": [
                    {
                        "job_id": item.job_id,
                        "platform": item.platform,
                        "priority": item.priority,
                        "wait_time_seconds": (datetime.utcnow() - item.queued_at).total_seconds(),
                    }
                    for item in self._queue[:10]
                ],
            },
            "provider_health": {
                "total": total_providers,
                "healthy": healthy_count,
                "degraded": sum(
                    1
                    for h in self._provider_health.values()
                    if h.status == ProviderHealthStatus.DEGRADED
                ),
                "unavailable": sum(
                    1
                    for h in self._provider_health.values()
                    if h.status == ProviderHealthStatus.UNAVAILABLE
                ),
                "providers": provider_stats,
            },
            "analytics_progress": {
                "active_jobs": active_jobs,
                "avg_progress_percent": avg_progress,
                "by_platform": self._progress_by_platform(),
            },
            "recommendations": {
                "total_generated": sum(r.total_count for r in self._recommendations.values()),
                "avg_confidence": self._avg_recommendation_confidence(),
            },
            "creators": {
                "tracked": len(self._memory_stats),
                "active": len([s for s in self._memory_stats.values() if s.acceptance_rate > 0.1]),
            },
        }

    def _progress_by_platform(self) -> dict[str, float]:
        """Get average progress by platform."""
        by_platform: dict[str, list[int]] = {}
        for progress in self._analytics_progress.values():
            if progress.platform not in by_platform:
                by_platform[progress.platform] = []
            by_platform[progress.platform].append(progress.progress_percent)

        return {
            platform: sum(progresses) / len(progresses)
            for platform, progresses in by_platform.items()
        }

    def _avg_recommendation_confidence(self) -> float:
        """Get average recommendation confidence."""
        if not self._recommendations:
            return 0.0
        total_confidence = sum(r.avg_confidence for r in self._recommendations.values())
        return total_confidence / len(self._recommendations)

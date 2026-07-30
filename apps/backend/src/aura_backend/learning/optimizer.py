"""M14 Phase 4: Performance Optimizer.

Optimization strategies for learning orchestration: parallel execution, caching, retry logic.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .context import LearningContext
from .providers import AnalyticsProvider


@dataclass(frozen=True)
class ProviderSelection:
    """Provider selection decision."""

    primary_provider: str
    fallback_provider: str | None = None
    reason: str = ""
    required_capabilities: tuple[str, ...] = None

    def __post_init__(self):
        if self.required_capabilities is None:
            object.__setattr__(self, "required_capabilities", ())


@dataclass(frozen=True)
class RecommendationCacheEntry:
    """Cached recommendation for reuse."""

    job_id: str
    creator_id: str
    platform: str
    recommendations: dict
    generated_at: datetime
    expires_at: datetime
    confidence: float = 0.0

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def is_valid_for(self, context: LearningContext) -> bool:
        """Check if cache entry is valid for given context."""
        if self.is_expired():
            return False
        if self.creator_id != context.creator_id:
            return False
        if self.platform != context.platform:
            return False
        return True


@dataclass(frozen=True)
class QueueOptimizationDecision:
    """Queue optimization decision."""

    job_id: str
    reorder: bool = False
    new_priority: int = 0
    parallel_threshold: int = 3
    reason: str = ""


class CapabilityBasedProviderSelector:
    """Select providers based on required capabilities."""

    def __init__(self, provider_registry=None):
        self.provider_registry = provider_registry

    def select_provider(
        self,
        context: LearningContext,
        required_capabilities: tuple[str, ...],
        providers: dict[str, AnalyticsProvider],
    ) -> ProviderSelection:
        """Select best provider for required capabilities."""
        candidates = []

        for provider_name, provider in providers.items():
            if not hasattr(provider, "get_capabilities"):
                continue

            # Check if provider supports all required capabilities
            capabilities = provider.get_capabilities()
            supports_all = all(
                cap in [c.name for c in capabilities.supported_features]
                for cap in required_capabilities
            )

            if supports_all:
                # Check rate limits
                if capabilities.rate_limit_per_hour > 0:
                    candidates.append((provider_name, capabilities.rate_limit_per_hour))

        if not candidates:
            # Fallback to primary provider
            primary = context.platform or "mock"
            return ProviderSelection(
                primary_provider=primary,
                reason="No capable provider found, using default",
            )

        # Sort by rate limit (higher is better)
        candidates.sort(key=lambda x: x[1], reverse=True)
        primary = candidates[0][0]
        fallback = candidates[1][0] if len(candidates) > 1 else None

        return ProviderSelection(
            primary_provider=primary,
            fallback_provider=fallback,
            required_capabilities=required_capabilities,
            reason=f"Selected {primary} based on capability support",
        )


class RecommendationCacheManager:
    """Manage recommendation caching to avoid redundant work."""

    def __init__(self, ttl_minutes: int = 60, max_entries: int = 1000):
        self.ttl_minutes = ttl_minutes
        self.max_entries = max_entries
        self._cache: dict[str, RecommendationCacheEntry] = {}

    def get(self, context: LearningContext) -> dict | None:
        """Get cached recommendations if valid."""
        cache_key = f"{context.creator_id}:{context.platform}"
        entry = self._cache.get(cache_key)

        if entry and entry.is_valid_for(context):
            return entry.recommendations

        # Clean up expired entry
        if entry and entry.is_expired():
            del self._cache[cache_key]

        return None

    def set(
        self,
        context: LearningContext,
        recommendations: dict,
        confidence: float = 0.8,
    ) -> None:
        """Cache recommendations."""
        cache_key = f"{context.creator_id}:{context.platform}"

        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_entries:
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].generated_at,
            )
            del self._cache[oldest_key]

        now = datetime.utcnow()
        entry = RecommendationCacheEntry(
            job_id=context.job_id,
            creator_id=context.creator_id,
            platform=context.platform,
            recommendations=recommendations,
            generated_at=now,
            expires_at=now + timedelta(minutes=self.ttl_minutes),
            confidence=confidence,
        )

        self._cache[cache_key] = entry

    def invalidate(self, creator_id: str, platform: str | None = None) -> int:
        """Invalidate cache entries."""
        keys_to_remove = []
        for key, entry in self._cache.items():
            if entry.creator_id == creator_id:
                if platform is None or entry.platform == platform:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        return len(keys_to_remove)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        valid_entries = sum(1 for e in self._cache.values() if not e.is_expired())
        expired_entries = len(self._cache) - valid_entries

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "capacity_used_percent": (len(self._cache) / self.max_entries * 100),
        }


class QueueOptimizer:
    """Optimize learning job queue for better throughput."""

    def __init__(self, max_parallel_jobs: int = 10):
        self.max_parallel_jobs = max_parallel_jobs
        self._active_jobs: dict[str, datetime] = {}

    def should_process_immediately(self, job_id: str, priority: int) -> bool:
        """Decide if job should be processed immediately."""
        active_count = sum(
            1
            for timestamp in self._active_jobs.values()
            if (datetime.utcnow() - timestamp).total_seconds() < 300  # 5 min timeout
        )

        if active_count >= self.max_parallel_jobs:
            # Check if high priority
            return priority >= 8  # Allow high priority even if at capacity

        return True

    def mark_job_active(self, job_id: str) -> None:
        """Mark job as actively processing."""
        self._active_jobs[job_id] = datetime.utcnow()

    def mark_job_complete(self, job_id: str) -> None:
        """Mark job as complete."""
        self._active_jobs.pop(job_id, None)

    def get_active_count(self) -> int:
        """Get count of active jobs."""
        now = datetime.utcnow()
        active = [ts for ts in self._active_jobs.values() if (now - ts).total_seconds() < 300]
        return len(active)

    def optimize_queue(self, queue_items: list[tuple[str, int]]) -> list[QueueOptimizationDecision]:
        """Generate queue optimization decisions."""
        decisions = []
        active = self.get_active_count()

        for job_id, priority in queue_items:
            if active >= self.max_parallel_jobs:
                # Keep high priority items, reorder low priority
                if priority < 5:
                    decisions.append(
                        QueueOptimizationDecision(
                            job_id=job_id,
                            reorder=True,
                            new_priority=priority - 1,
                            reason="Deprioritized to free resources for higher priority jobs",
                        )
                    )
            else:
                # Can process in parallel
                decisions.append(
                    QueueOptimizationDecision(
                        job_id=job_id,
                        reorder=False,
                        reason="Can be processed in parallel",
                    )
                )

        return decisions


class RetryOptimizer:
    """Optimize retry logic based on failure patterns."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._failure_counts: dict[str, int] = {}
        self._last_failure_time: dict[str, datetime] = {}

    def should_retry(self, stage_id: str, error_type: str, retry_count: int) -> tuple[bool, float]:
        """Decide if should retry and get backoff delay."""
        if retry_count >= self.max_retries:
            return False, 0.0

        # Transient errors should always retry
        transient_errors = {"timeout", "rate_limit", "temporary", "connection"}
        if any(err in error_type.lower() for err in transient_errors):
            backoff = min(2**retry_count, 60)  # Exponential backoff, max 60s
            return True, backoff

        # Permanent errors shouldn't retry
        permanent_errors = {"auth", "invalid", "not_found", "permission"}
        if any(err in error_type.lower() for err in permanent_errors):
            return False, 0.0

        # Unknown errors get limited retries
        if retry_count < 2:
            return True, min(2**retry_count, 30)

        return False, 0.0

    def get_retry_strategy(self, provider_name: str, success_rate: float) -> dict[str, int]:
        """Get retry strategy based on provider reliability."""
        if success_rate >= 0.95:
            return {"max_retries": 1, "backoff_base": 1}
        elif success_rate >= 0.85:
            return {"max_retries": 2, "backoff_base": 2}
        else:
            return {"max_retries": 3, "backoff_base": 3}


class ParallelAnalyticsCollector:
    """Coordinate parallel analytics collection from multiple providers."""

    def __init__(self, max_parallel: int = 5):
        self.max_parallel = max_parallel
        self._active_collections: dict[str, list[str]] = {}  # job_id -> [platforms]

    def can_collect_in_parallel(self, job_id: str, platforms: list[str]) -> bool:
        """Check if can collect from all platforms in parallel."""
        active_platforms = self._active_collections.get(job_id, [])
        return len(active_platforms) + len(platforms) <= self.max_parallel

    def start_collection(self, job_id: str, platforms: list[str]) -> list[str]:
        """Start parallel collection and return platforms to collect."""
        if job_id not in self._active_collections:
            self._active_collections[job_id] = []

        platforms_to_collect = []
        for platform in platforms:
            if len(self._active_collections[job_id]) < self.max_parallel:
                self._active_collections[job_id].append(platform)
                platforms_to_collect.append(platform)

        return platforms_to_collect

    def finish_collection(self, job_id: str, platform: str) -> None:
        """Mark collection as finished."""
        if job_id in self._active_collections:
            self._active_collections[job_id] = [
                p for p in self._active_collections[job_id] if p != platform
            ]
            if not self._active_collections[job_id]:
                del self._active_collections[job_id]

    def get_collection_summary(self, job_id: str) -> dict:
        """Get collection summary."""
        return {
            "job_id": job_id,
            "active_platforms": self._active_collections.get(job_id, []),
            "parallel_capacity_used": len(self._active_collections.get(job_id, [])),
            "max_parallel": self.max_parallel,
        }

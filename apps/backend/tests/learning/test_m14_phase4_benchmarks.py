"""M14 Phase 4 Benchmarks: Performance and Scalability.

Benchmark suite for throughput, scalability, provider comparison, and latency.
"""

import time

from aura_backend.learning import (
    LearningContext,
    LearningJob,
    LearningPlanner,
    create_default_learning_agent_registry,
    create_default_provider_registry,
)
from aura_backend.learning.dashboard import LearningDashboard, LearningQueueItem
from aura_backend.learning.operational_metrics import (
    OperationalMetricsAggregator,
    StageDurationMetric,
)
from aura_backend.learning.optimizer import (
    RecommendationCacheManager,
)


class BenchmarkMetrics:
    """Collect benchmark metrics."""

    def __init__(self):
        self.results = {}

    def record(self, name: str, duration_ms: float, ops: int = 1):
        """Record benchmark result."""
        if name not in self.results:
            self.results[name] = []
        self.results[name].append({"duration_ms": duration_ms, "ops": ops})

    def summarize(self):
        """Summarize benchmark results."""
        summary = {}
        for name, measurements in self.results.items():
            durations = [m["duration_ms"] for m in measurements]
            ops_list = [m["ops"] for m in measurements]

            summary[name] = {
                "count": len(measurements),
                "avg_ms": sum(durations) / len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "total_ops": sum(ops_list),
                "ops_per_second": (
                    (sum(ops_list) / (sum(durations) / 1000)) if sum(durations) > 0 else 0
                ),
            }

        return summary


# ============================================================================
# THROUGHPUT BENCHMARKS
# ============================================================================


class TestThroughputBenchmarks:
    """Benchmark learning job throughput."""

    def test_dag_generation_throughput(self):
        """Benchmark DAG generation throughput."""
        metrics = BenchmarkMetrics()
        planner = LearningPlanner()

        for i in range(100):
            job = LearningJob(creator_id=f"creator-{i}")
            context = LearningContext(
                job_id=job.id,
                creator_id=f"creator-{i}",
                platform="youtube" if i % 3 == 0 else "tiktok",
            )

            start = time.time()
            planner.create_stage_dag(job, context, None)
            elapsed_ms = (time.time() - start) * 1000

            metrics.record("dag_generation", elapsed_ms)

        summary = metrics.summarize()
        print("\nDAG Generation Throughput:")
        print(f"  Operations: {summary['dag_generation']['total_ops']}")
        print(f"  Ops/sec: {summary['dag_generation']['ops_per_second']:.1f}")
        print(f"  Avg: {summary['dag_generation']['avg_ms']:.2f}ms")

        # Assertion: DAG generation should be fast
        assert summary["dag_generation"]["avg_ms"] < 50, "DAG generation too slow"

    def test_stage_conversion_throughput(self):
        """Benchmark stage to M8 task conversion throughput."""
        metrics = BenchmarkMetrics()
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")
        context = LearningContext(
            job_id=job.id,
            creator_id="creator-1",
            platform="youtube",
        )

        stages = planner.create_stage_dag(job, context, None)

        for _ in range(100):
            start = time.time()
            planner.stages_to_m8_tasks(stages)
            elapsed_ms = (time.time() - start) * 1000

            metrics.record("stage_conversion", elapsed_ms)

        summary = metrics.summarize()
        print("\nStage Conversion Throughput:")
        print(f"  Ops/sec: {summary['stage_conversion']['ops_per_second']:.1f}")
        print(f"  Avg: {summary['stage_conversion']['avg_ms']:.2f}ms")

        assert summary["stage_conversion"]["avg_ms"] < 10, "Stage conversion too slow"

    def test_queue_operations_throughput(self):
        """Benchmark queue operations throughput."""
        metrics = BenchmarkMetrics()
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        # Add items
        start = time.time()
        for i in range(1000):
            item = LearningQueueItem(
                job_id=f"job-{i}",
                creator_id=f"creator-{i}",
                platform="youtube" if i % 3 == 0 else "tiktok",
                queued_at=now,
                estimated_duration_seconds=60,
                priority=i % 10,
            )
            dashboard.add_to_queue(item)
        elapsed_ms = (time.time() - start) * 1000
        metrics.record("queue_add", elapsed_ms, ops=1000)

        # Get queue
        start = time.time()
        for _ in range(100):
            dashboard.get_queue(limit=100)
        elapsed_ms = (time.time() - start) * 1000
        metrics.record("queue_get", elapsed_ms, ops=100)

        summary = metrics.summarize()
        print("\nQueue Operations Throughput:")
        print(f"  Add Ops/sec: {summary['queue_add']['ops_per_second']:.1f}")
        print(f"  Get Ops/sec: {summary['queue_get']['ops_per_second']:.1f}")

        assert summary["queue_add"]["ops_per_second"] > 5000, "Queue add throughput too low"


# ============================================================================
# SCALABILITY BENCHMARKS
# ============================================================================


class TestScalabilityBenchmarks:
    """Benchmark system scalability."""

    def test_dashboard_scalability(self):
        """Test dashboard scalability with large queues."""
        dashboard = LearningDashboard()
        now = __import__("datetime").datetime.utcnow()

        # Build large queue
        for i in range(5000):
            dashboard.add_to_queue(
                LearningQueueItem(
                    job_id=f"job-{i}",
                    creator_id=f"creator-{i % 100}",
                    platform="youtube" if i % 3 == 0 else "tiktok",
                    queued_at=now,
                    estimated_duration_seconds=60,
                    priority=i % 10,
                )
            )

        # Retrieve queue snapshot
        start = time.time()
        dashboard.get_dashboard_snapshot()
        elapsed_ms = (time.time() - start) * 1000

        print(f"\nDashboard Snapshot with 5000 items: {elapsed_ms:.2f}ms")
        assert elapsed_ms < 100, "Dashboard snapshot too slow at scale"

    def test_metrics_aggregator_scalability(self):
        """Test metrics aggregator scalability."""
        aggregator = OperationalMetricsAggregator(max_history=50000)
        now = __import__("datetime").datetime.utcnow()

        # Record many metrics
        start = time.time()
        for i in range(10000):
            aggregator.record_stage_duration(
                StageDurationMetric(
                    stage_type="retrieve_metrics" if i % 2 == 0 else "analyze_retention",
                    platform="youtube" if i % 3 == 0 else "tiktok",
                    duration_ms=100.0 + (i % 200),
                    timestamp=now,
                    success=i % 50 != 0,  # 98% success rate
                )
            )
        elapsed_ms = (time.time() - start) * 1000

        print(f"\nRecording 10000 metrics: {elapsed_ms:.2f}ms")

        # Retrieve stats
        start = time.time()
        stats = aggregator.get_stage_duration_stats()
        elapsed_ms = (time.time() - start) * 1000

        print(f"Retrieving stats from 10000 metrics: {elapsed_ms:.2f}ms")
        assert stats["count"] == 10000

    def test_cache_scalability(self):
        """Test recommendation cache scalability."""
        cache = RecommendationCacheManager(max_entries=10000)

        # Fill cache
        start = time.time()
        for i in range(5000):
            context = LearningContext(
                job_id=f"job-{i}",
                creator_id=f"creator-{i}",
                platform="youtube" if i % 3 == 0 else "tiktok",
            )
            cache.set(context, {"data": f"rec-{i}"}, confidence=0.8 + (i % 20) * 0.01)
        elapsed_ms = (time.time() - start) * 1000

        print(f"\nFilling cache with 5000 entries: {elapsed_ms:.2f}ms")

        # Retrieve from cache
        start = time.time()
        for i in range(1000):
            context = LearningContext(
                job_id=f"job-{i}",
                creator_id=f"creator-{i}",
                platform="youtube" if i % 3 == 0 else "tiktok",
            )
            cache.get(context)
        elapsed_ms = (time.time() - start) * 1000

        print(f"Cache lookups (1000): {elapsed_ms:.2f}ms")


# ============================================================================
# PROVIDER COMPARISON BENCHMARKS
# ============================================================================


class TestProviderComparisonBenchmarks:
    """Benchmark provider performance."""

    def test_provider_registry_lookup(self):
        """Benchmark provider registry lookup performance."""
        registry = create_default_provider_registry()
        providers = registry.get_providers()

        metrics = BenchmarkMetrics()

        # Lookup each provider multiple times
        for _ in range(1000):
            start = time.time()
            for provider_name in ["youtube", "tiktok", "instagram", "mock"]:
                provider = providers.get(provider_name)
                assert provider is not None
            elapsed_ms = (time.time() - start) * 1000
            metrics.record("provider_lookup", elapsed_ms, ops=4)

        summary = metrics.summarize()
        print("\nProvider Lookup Performance:")
        print(f"  Ops/sec: {summary['provider_lookup']['ops_per_second']:.1f}")
        print(f"  Avg per lookup: {summary['provider_lookup']['avg_ms'] / 4:.3f}ms")

    def test_provider_count(self):
        """Verify provider count."""
        registry = create_default_provider_registry()
        providers = registry.get_providers()

        print(f"\nRegistered Providers: {len(providers)}")
        for name in providers.keys():
            print(f"  - {name}")

        assert len(providers) >= 4, "Should have at least 4 providers"


# ============================================================================
# LATENCY BENCHMARKS
# ============================================================================


class TestLatencyBenchmarks:
    """Benchmark operation latencies."""

    def test_agent_registry_access_latency(self):
        """Benchmark agent registry access latency."""
        registry = create_default_learning_agent_registry()
        agents = registry.list_agents()

        metrics = BenchmarkMetrics()

        # Lookup each agent type
        for _ in range(1000):
            start = time.time()
            for agent_id in agents[:5]:  # Test first 5 agents
                agent = registry.get(agent_id)
                assert agent is not None
            elapsed_ms = (time.time() - start) * 1000
            metrics.record("agent_lookup", elapsed_ms)

        summary = metrics.summarize()
        print("\nAgent Lookup Latency:")
        print(f"  Avg: {summary['agent_lookup']['avg_ms']:.3f}ms")

    def test_stage_dag_generation_latency(self):
        """Benchmark stage DAG generation latency."""
        planner = LearningPlanner()
        job = LearningJob(creator_id="creator-1")

        metrics = BenchmarkMetrics()

        for platform in ["youtube", "tiktok", "instagram", "linkedin", "podcast"]:
            for _ in range(100):
                context = LearningContext(
                    job_id=job.id,
                    creator_id="creator-1",
                    platform=platform,
                )

                start = time.time()
                planner.create_stage_dag(job, context, None)
                elapsed_ms = (time.time() - start) * 1000

                metrics.record(f"dag_{platform}", elapsed_ms)

        summary = metrics.summarize()
        print("\nDAG Generation Latency by Platform:")
        for platform in ["youtube", "tiktok", "instagram", "linkedin", "podcast"]:
            key = f"dag_{platform}"
            if key in summary:
                avg_ms = summary[key]["avg_ms"]
                max_ms = summary[key]["max_ms"]
                print(f"  {platform}: {avg_ms:.2f}ms (P99: {max_ms:.2f}ms)")


# ============================================================================
# MEMORY AND RESOURCE BENCHMARKS
# ============================================================================


class TestResourceBenchmarks:
    """Benchmark resource usage."""

    def test_metrics_memory_footprint(self):
        """Test metrics aggregator memory footprint."""
        import sys

        aggregator = OperationalMetricsAggregator(max_history=10000)
        now = __import__("datetime").datetime.utcnow()

        # Record metrics
        for i in range(1000):
            aggregator.record_stage_duration(
                StageDurationMetric(
                    stage_type="retrieve_metrics",
                    platform="youtube",
                    duration_ms=100.0 + i,
                    timestamp=now,
                    success=True,
                )
            )

        size = sys.getsizeof(aggregator._stage_durations)
        print(f"\nMetrics Storage (1000 entries): ~{size / 1024:.1f}KB")

    def test_cache_memory_efficiency(self):
        """Test cache memory efficiency."""
        import sys

        cache = RecommendationCacheManager(max_entries=1000)

        # Fill cache
        for i in range(500):
            context = LearningContext(
                job_id=f"job-{i}",
                creator_id=f"creator-{i}",
                platform="youtube",
            )
            cache.set(context, {"data": f"rec-{i}"})

        size = sys.getsizeof(cache._cache)
        print(f"\nCache Storage (500 entries): ~{size / 1024:.1f}KB")


# ============================================================================
# END-TO-END WORKFLOW BENCHMARKS
# ============================================================================


class TestEndToEndBenchmarks:
    """End-to-end workflow benchmarks."""

    def test_complete_learning_workflow_latency(self):
        """Benchmark complete learning workflow latency."""
        metrics = BenchmarkMetrics()
        planner = LearningPlanner()

        for i in range(50):
            job = LearningJob(creator_id=f"creator-{i}")
            context = LearningContext(
                job_id=job.id,
                creator_id=f"creator-{i}",
                platform="youtube" if i % 2 == 0 else "tiktok",
            )

            start = time.time()

            # DAG generation
            stages = planner.create_stage_dag(job, context, None)

            # Stage conversion
            planner.stages_to_m8_tasks(stages)

            elapsed_ms = (time.time() - start) * 1000
            metrics.record("complete_workflow", elapsed_ms)

        summary = metrics.summarize()
        print("\nComplete Learning Workflow Latency:")
        print(f"  Avg: {summary['complete_workflow']['avg_ms']:.2f}ms")
        print(f"  P99: {max(m['duration_ms'] for m in self.results['complete_workflow']):.2f}ms")
        print(f"  Ops/sec: {summary['complete_workflow']['ops_per_second']:.1f}")

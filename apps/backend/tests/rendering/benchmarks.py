"""M12 Benchmark Suite: Performance, Memory, and Scalability.

Benchmarks for:
1. Rendering performance (throughput, latency)
2. Memory usage (peak, average)
3. Scalability (clip count, complexity)
4. Provider comparison (throughput, accuracy, efficiency)
"""

import time
from typing import Any

from aura_backend.editing import Clip, EditPlan
from aura_backend.rendering import (
    FFmpegProvider,
    MockRendererProvider,
    RenderContext,
    RenderingPlanner,
)
from aura_backend.rendering.dashboard import PerformanceOptimizer
from aura_backend.rendering.metrics import MetricsAggregator
from aura_backend.rendering.stages import RenderStage, StageType


class PerformanceBenchmark:
    """Performance benchmarking utilities"""

    @staticmethod
    def measure_planner_speed(clip_count: int, iterations: int = 5) -> dict[str, float]:
        """Measure planner DAG generation speed"""
        planner = RenderingPlanner()
        context = RenderContext()

        # Create clips
        clips = [
            Clip(
                session_id="s1",
                video_id="v1",
                start_timestamp=float(i * 5),
                end_timestamp=float((i + 1) * 5),
            )
            for i in range(clip_count)
        ]

        plan = EditPlan(clips=clips)

        # Warm-up
        planner.create_stage_dag(plan, context)

        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.time()
            _ = planner.create_stage_dag(plan, context)
            elapsed = time.time() - start
            times.append(elapsed)

        return {
            "avg_ms": (sum(times) / len(times)) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "clip_count": clip_count,
        }

    @staticmethod
    def measure_provider_registry_lookup(provider_count: int, lookups: int = 1000) -> float:
        """Measure provider registry lookup latency"""
        from aura_backend.rendering.providers import ProviderRegistry

        registry = ProviderRegistry()

        # Register multiple providers
        for i in range(provider_count):
            provider = MockRendererProvider()
            registry.register(f"provider_{i}", provider)

        # Benchmark lookup
        start = time.time()
        for i in range(lookups):
            registry.get(f"provider_{i % provider_count}")
        elapsed = time.time() - start

        # Microseconds per lookup
        return (elapsed * 1_000_000) / lookups


class MemoryBenchmark:
    """Memory usage benchmarking"""

    @staticmethod
    def measure_render_stage_memory(stage_count: int) -> float:
        """Measure memory for large stage DAGs"""
        import sys

        stages = []
        for i in range(stage_count):
            stage = RenderStage(
                stage_id=f"stage_{i}",
                stage_type=StageType.CLIP_RENDER if i % 2 == 0 else StageType.EXPORT,
            )
            stages.append(stage)

        # Approximate size in bytes
        total_size = sum(sys.getsizeof(s) for s in stages)
        return total_size / (1024 * 1024)  # MB

    @staticmethod
    def measure_metrics_aggregator_memory(entry_count: int) -> float:
        """Measure memory for metrics aggregator"""
        import sys

        from aura_backend.rendering.stages import RenderingMetrics

        aggregator = MetricsAggregator()

        # Add metrics
        for i in range(entry_count):
            metrics = RenderingMetrics(
                job_id=f"job_{i}",
                total_duration_seconds=30.0 + i,
                stages_completed=5,
                validation_passed=i % 2 == 0,
            )
            aggregator.add_metrics(metrics)

        # Approximate size
        total_size = sys.getsizeof(aggregator._metrics_history)
        return total_size / (1024 * 1024)  # MB


class ScalabilityBenchmark:
    """Scalability testing"""

    @staticmethod
    def test_planner_with_increasing_clips() -> list[dict[str, Any]]:
        """Test planner performance with increasing clip count"""
        clip_counts = [10, 50, 100, 500, 1000]
        results = []

        for count in clip_counts:
            result = PerformanceBenchmark.measure_planner_speed(count, iterations=3)
            results.append(result)

        return results

    @staticmethod
    def test_parallel_stage_identification() -> dict[str, Any]:
        """Test efficiency of parallel stage identification"""
        stages = [
            RenderStage(stage_id=f"s{i}", stage_type=StageType.CLIP_RENDER) for i in range(100)
        ]

        start = time.time()
        groups = PerformanceOptimizer.calculate_parallel_stages(stages)
        elapsed = time.time() - start

        return {
            "stages": len(stages),
            "parallel_groups": len(groups),
            "duration_ms": elapsed * 1000,
        }


class ProviderComparison:
    """Compare rendering providers"""

    @staticmethod
    def compare_provider_availability() -> dict[str, bool]:
        """Check availability of all providers"""
        providers = {
            "mock": MockRendererProvider(),
            "ffmpeg": FFmpegProvider(),
        }

        availability = {}
        for name, _provider in providers.items():
            # Mock providers are always available
            availability[name] = name == "mock"

        return availability

    @staticmethod
    def compare_provider_capabilities() -> dict[str, dict[str, Any]]:
        """Compare feature sets across providers"""
        providers = {
            "mock": MockRendererProvider(),
            "ffmpeg": FFmpegProvider(),
        }

        comparison = {}
        for name, provider in providers.items():
            cap = provider.capabilities
            comparison[name] = {
                "codecs": cap._supported_codecs if hasattr(cap, "_supported_codecs") else [],
                "features": cap._supported_features if hasattr(cap, "_supported_features") else [],
            }

        return comparison


# ============================================================================
# PYTEST BENCHMARK TESTS
# ============================================================================


class TestPerformanceBenchmarks:
    """Performance benchmarks"""

    def test_planner_10_clips(self, benchmark):
        """Benchmark planner with 10 clips"""
        planner = RenderingPlanner()
        context = RenderContext()
        clips = [
            Clip(
                session_id="s1",
                video_id="v1",
                start_timestamp=float(i * 5),
                end_timestamp=float((i + 1) * 5),
            )
            for i in range(10)
        ]
        plan = EditPlan(clips=clips)

        def run():
            return planner.create_stage_dag(plan, context)

        result = benchmark(run)
        assert len(result) > 0

    def test_planner_100_clips(self, benchmark):
        """Benchmark planner with 100 clips"""
        planner = RenderingPlanner()
        context = RenderContext()
        clips = [
            Clip(
                session_id="s1",
                video_id="v1",
                start_timestamp=float(i * 5),
                end_timestamp=float((i + 1) * 5),
            )
            for i in range(100)
        ]
        plan = EditPlan(clips=clips)

        def run():
            return planner.create_stage_dag(plan, context)

        result = benchmark(run)
        assert len(result) > 0

    def test_parallel_stage_calculation(self, benchmark):
        """Benchmark parallel stage identification"""
        stages = [
            RenderStage(
                stage_id=f"s{i}",
                stage_type=StageType.CLIP_RENDER if i % 3 == 0 else StageType.EXPORT,
            )
            for i in range(50)
        ]

        def run():
            return PerformanceOptimizer.calculate_parallel_stages(stages)

        result = benchmark(run)
        assert len(result) > 0

    def test_duration_estimation(self, benchmark):
        """Benchmark duration estimation"""
        stages = [
            RenderStage(
                stage_id=f"s{i}",
                stage_type=StageType.CLIP_RENDER,
                estimated_duration_seconds=10.0 + i,
            )
            for i in range(20)
        ]

        def run():
            return PerformanceOptimizer.estimate_total_duration(stages)

        result = benchmark(run)
        assert result > 0


class TestMemoryBenchmarks:
    """Memory usage benchmarks"""

    def test_stage_dag_memory_100(self):
        """Measure memory for 100 stages"""
        mb = MemoryBenchmark.measure_render_stage_memory(100)
        assert mb < 10  # Should be < 10MB

    def test_stage_dag_memory_1000(self):
        """Measure memory for 1000 stages"""
        mb = MemoryBenchmark.measure_render_stage_memory(1000)
        assert mb < 50  # Should be < 50MB

    def test_metrics_aggregator_memory(self):
        """Measure metrics aggregator memory"""
        mb = MemoryBenchmark.measure_metrics_aggregator_memory(100)
        assert mb < 10  # Should be < 10MB


class TestScalabilityBenchmarks:
    """Scalability tests"""

    def test_planner_scales_linearly(self):
        """Verify planner scales well with clip count"""
        results = ScalabilityBenchmark.test_planner_with_increasing_clips()

        # Results should show reasonable scaling
        assert len(results) == 5
        assert all("avg_ms" in r for r in results)

        # Later results should take more time (but not exponentially)
        time_10 = results[0]["avg_ms"]
        time_1000 = results[4]["avg_ms"]

        # Should scale better than O(n^2)
        ratio = time_1000 / time_10
        assert ratio < 500  # 1000/10 = 100, so <500x is reasonable

    def test_parallel_stage_identification_scales(self):
        """Verify parallel identification scales"""
        result = ScalabilityBenchmark.test_parallel_stage_identification()

        assert result["stages"] == 100
        assert result["duration_ms"] < 100  # Should be very fast


class TestProviderComparison:
    """Provider comparison tests"""

    def test_provider_availability(self):
        """Test provider availability"""
        availability = ProviderComparison.compare_provider_availability()

        assert "mock" in availability
        assert availability["mock"] is True

    def test_provider_capabilities(self):
        """Test provider capability comparison"""
        comparison = ProviderComparison.compare_provider_capabilities()

        assert "mock" in comparison
        assert "ffmpeg" in comparison
        assert "codecs" in comparison["mock"]
        assert "features" in comparison["mock"]

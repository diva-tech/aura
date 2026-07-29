"""M12 Phase 4: Rendering Dashboard and Performance Optimizations.

Real-time dashboard data and performance optimization logic.
"""

from dataclasses import dataclass
from typing import Any

from .context import RenderCapability
from .metrics import MetricsAggregator, ProviderMetrics
from .stages import RenderStage, StageType


@dataclass
class DashboardStageView:
    """Dashboard view of a rendering stage"""

    stage_id: str
    stage_type: str
    status: str  # pending, running, completed, failed
    progress_percent: float
    provider: str
    estimated_remaining_seconds: float
    resource_usage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_type": self.stage_type,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "provider": self.provider,
        }


class DashboardProvider:
    """Provides real-time dashboard data"""

    def __init__(self, metrics_aggregator: MetricsAggregator):
        self._metrics = metrics_aggregator
        self._active_jobs: dict[str, list[RenderStage]] = {}

    def register_job(self, job_id: str, stages: list[RenderStage]) -> None:
        """Register job for dashboard tracking"""
        self._active_jobs[job_id] = stages

    def get_job_progress(self, job_id: str) -> dict[str, Any]:
        """Get job progress snapshot"""
        if job_id not in self._active_jobs:
            return {}

        stages = self._active_jobs[job_id]
        completed = sum(1 for s in stages if hasattr(s, "status") and s.status == "completed")

        return {
            "job_id": job_id,
            "total_stages": len(stages),
            "completed_stages": completed,
            "progress_percent": (completed / len(stages) * 100) if stages else 0,
            "stages": [
                {
                    "stage_id": s.stage_id,
                    "stage_type": s.stage_type.value,
                    "estimated_duration": s.estimated_duration_seconds,
                }
                for s in stages
            ],
        }

    def get_provider_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all providers"""
        comparison = self._metrics.get_provider_comparison()

        return {
            name: {
                "status": "available",
                "success_rate": metrics.success_rate,
                "avg_duration": metrics.avg_duration_seconds,
                "peak_memory_mb": metrics.peak_memory_mb,
                "total_jobs": metrics.total_jobs,
            }
            for name, metrics in comparison.items()
        }

    def get_throughput_chart(self) -> dict[str, Any]:
        """Get throughput data for charting"""
        throughput = self._metrics.get_throughput_metrics()

        return {
            "jobs_per_hour": throughput.throughput_jobs_per_hour,
            "jobs_completed": throughput.jobs_completed,
            "avg_queue_time": throughput.avg_queue_time_seconds,
        }

    def get_performance_summary(self) -> dict[str, Any]:
        """Get overall performance summary"""
        return self._metrics.get_summary_report()


class PerformanceOptimizer:
    """Optimizes rendering execution"""

    @staticmethod
    def select_best_provider(
        stage: RenderStage,
        provider_capabilities: dict[str, RenderCapability],
        provider_metrics: dict[str, ProviderMetrics],
    ) -> str:
        """Select best provider for stage based on capabilities and metrics"""

        # Check capability requirements
        capable_providers = []
        for provider_name, capability in provider_capabilities.items():
            if PerformanceOptimizer._provider_supports_stage(capability, stage):
                capable_providers.append(provider_name)

        if not capable_providers:
            return stage.preferred_provider

        # Score by recent performance
        best_provider = stage.preferred_provider
        best_score = -1

        for provider in capable_providers:
            metrics = provider_metrics.get(provider)
            if not metrics:
                continue

            # Score: success_rate * 100 - avg_duration
            score = (metrics.success_rate * 100) - metrics.avg_duration_seconds

            if score > best_score:
                best_score = score
                best_provider = provider

        return best_provider

    @staticmethod
    def _provider_supports_stage(capability: RenderCapability, stage: RenderStage) -> bool:
        """Check if provider supports stage requirements"""

        stage_requirements = {
            StageType.CLIP_RENDER: {"h264", "mp4"},
            StageType.SUBTITLE: {"subtitle_support"},
            StageType.AUDIO: {"audio_mixing_supported"},
            StageType.COMPOSITE: {"h264"},
        }

        if stage.stage_type not in stage_requirements:
            return True

        required = stage_requirements[stage.stage_type]

        for req in required:
            if req in {"h264", "h265"}:
                if not capability.supports_codec(req):
                    return False
            else:
                if not capability.supports_feature(req):
                    return False

        return True

    @staticmethod
    def calculate_parallel_stages(stages: list[RenderStage]) -> dict[str, list[str]]:
        """Identify stages that can execute in parallel"""
        parallel_groups = {}
        wave = 1

        # Group stages by dependency depth
        visited = set()
        current_wave = set()

        for stage in stages:
            if not stage.depends_on:
                current_wave.add(stage.stage_id)

        while current_wave:
            parallel_groups[f"wave_{wave}"] = list(current_wave)
            visited.update(current_wave)

            # Find next wave
            next_wave = set()
            for stage in stages:
                if stage.stage_id not in visited:
                    # Check if all dependencies are met
                    if all(dep_id in visited for dep_id in stage.depends_on):
                        next_wave.add(stage.stage_id)

            current_wave = next_wave
            wave += 1

        return parallel_groups

    @staticmethod
    def estimate_total_duration(stages: list[RenderStage]) -> float:
        """Estimate total rendering duration based on parallel execution"""
        if not stages:
            return 0.0

        parallel_groups = PerformanceOptimizer.calculate_parallel_stages(stages)
        total_duration = 0.0

        for group_stages in parallel_groups.values():
            # In each wave, longest-running stage determines duration
            stage_map = {s.stage_id: s for s in stages}
            wave_duration = max(stage_map[sid].estimated_duration_seconds for sid in group_stages)
            total_duration += wave_duration

        return total_duration

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, datetime

from aura_backend.api.v1.schemas.health import ComponentHealth, HealthResponse, HealthState
from aura_backend.config.settings import Settings
from aura_backend.core.runtime import RuntimeState
from aura_backend.repositories.health_repository import HealthRepository
from aura_backend.utils.system import get_disk_metric, get_gpu_metric, get_memory_metric


class HealthService:
    def __init__(
        self,
        repository: HealthRepository,
        settings: Settings,
        runtime_state: RuntimeState,
    ) -> None:
        self._repository = repository
        self._settings = settings
        self._runtime_state = runtime_state

    async def collect_health_status(self) -> HealthResponse:
        database, redis, rabbitmq, gpu, disk, memory = await asyncio.gather(
            self._repository.check_database(),
            self._repository.check_redis(),
            self._repository.check_rabbitmq(),
            asyncio.to_thread(get_gpu_metric),
            asyncio.to_thread(get_disk_metric, str(self._settings.health_disk_path)),
            asyncio.to_thread(get_memory_metric),
        )
        backend = ComponentHealth(status="healthy", message="backend is running")
        statuses = [
            backend.status,
            database.status,
            redis.status,
            rabbitmq.status,
            gpu.status,
            disk.status,
            memory.status,
        ]

        overall = self._derive_overall_status(statuses)

        return HealthResponse(
            service=self._settings.project_name,
            environment=self._settings.environment,
            version=self._runtime_state.version,
            status=overall,
            timestamp=datetime.now(UTC),
            backend=backend,
            database=database,
            redis=redis,
            rabbitmq=rabbitmq,
            gpu=gpu,
            disk=disk,
            memory=memory,
            uptime_seconds=round(self._runtime_state.uptime_seconds(), 2),
        )

    def _derive_overall_status(self, statuses: Sequence[HealthState]) -> HealthState:
        if any(status == "unhealthy" for status in statuses):
            return "unhealthy"
        if any(status in {"unavailable", "degraded"} for status in statuses):
            return "degraded"
        return "healthy"

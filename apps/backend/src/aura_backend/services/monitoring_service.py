from __future__ import annotations

from aura_backend.api.v1.schemas.health import ComponentHealth, HealthResponse
from aura_backend.core.runtime import RuntimeState
from aura_backend.services.health_service import HealthService


class MonitoringService:
    def __init__(
        self,
        health_service: HealthService,
        runtime_state: RuntimeState,
    ) -> None:
        self._health_service = health_service
        self._runtime_state = runtime_state

    async def live(self) -> ComponentHealth:
        return ComponentHealth(
            status="healthy",
            message="application process is live",
            details={
                "version": self._runtime_state.version,
                "started_at": self._runtime_state.started_at.isoformat(),
            },
        )

    async def ready(self) -> HealthResponse:
        return await self._health_service.collect_health_status()

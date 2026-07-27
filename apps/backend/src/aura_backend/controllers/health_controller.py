from __future__ import annotations

from aura_backend.api.v1.schemas.health import HealthResponse
from aura_backend.services.health_service import HealthService


class HealthController:
    def __init__(self, service: HealthService) -> None:
        self._service = service

    async def get_health_status(self) -> HealthResponse:
        return await self._service.collect_health_status()

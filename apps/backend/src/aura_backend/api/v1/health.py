from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import Response

from aura_backend.api.dependencies import get_health_controller, get_monitoring_service
from aura_backend.api.v1.schemas.health import ComponentHealth, HealthResponse
from aura_backend.controllers.health_controller import HealthController
from aura_backend.services.metrics_service import MetricsService
from aura_backend.services.monitoring_service import MonitoringService

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Platform health status")
async def health_check(
    controller: Annotated[HealthController, Depends(get_health_controller)],
) -> HealthResponse:
    return await controller.get_health_status()


@router.get("/health/live", response_model=ComponentHealth, summary="Liveness probe")
async def liveness_check(
    monitoring_service: Annotated[MonitoringService, Depends(get_monitoring_service)],
) -> ComponentHealth:
    return await monitoring_service.live()


@router.get("/health/ready", response_model=HealthResponse, summary="Readiness probe")
async def readiness_check(
    monitoring_service: Annotated[MonitoringService, Depends(get_monitoring_service)],
) -> HealthResponse:
    return await monitoring_service.ready()


@router.get("/metrics", summary="Prometheus metrics")
async def metrics() -> Response:
    return Response(
        content=MetricsService.get_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )

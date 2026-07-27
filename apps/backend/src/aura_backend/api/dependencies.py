from __future__ import annotations

from fastapi import Request

from aura_backend.controllers.health_controller import HealthController
from aura_backend.core.container import ApplicationContainer
from aura_backend.services.monitoring_service import MonitoringService


def get_container(request: Request) -> ApplicationContainer:
    return request.app.state.container  # type: ignore[no-any-return]


def get_health_controller(request: Request) -> HealthController:
    container = get_container(request)
    return container.health_controller


def get_monitoring_service(request: Request) -> MonitoringService:
    container = get_container(request)
    return container.monitoring_service

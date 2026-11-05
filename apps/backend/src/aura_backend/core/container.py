from __future__ import annotations

from functools import cached_property

from aura_backend.config.logging import get_logger
from aura_backend.config.settings import Settings
from aura_backend.controllers.health_controller import HealthController
from aura_backend.core.clients import InfrastructureClients
from aura_backend.core.runtime import RuntimeState
from aura_backend.repositories.audit_repository import AuditRepository
from aura_backend.repositories.health_repository import HealthRepository
from aura_backend.services.audit_service import AuditService
from aura_backend.services.health_service import HealthService
from aura_backend.services.monitoring_service import MonitoringService
from aura_backend.services.rate_limit_service import RateLimitService


class ApplicationContainer:
    def __init__(
        self,
        settings: Settings,
        infrastructure: InfrastructureClients,
        runtime_state: RuntimeState,
    ) -> None:
        self.settings = settings
        self.infrastructure = infrastructure
        self.runtime_state = runtime_state
        self.logger = get_logger(__name__)

    @cached_property
    def health_repository(self) -> HealthRepository:
        return HealthRepository(
            database_engine=self.infrastructure.database_engine,
            redis_client=self.infrastructure.redis_client,
            rabbitmq_url=self.settings.rabbitmq_url,
            timeout_seconds=self.settings.health_timeout_seconds,
        )

    @cached_property
    def health_service(self) -> HealthService:
        return HealthService(
            repository=self.health_repository,
            settings=self.settings,
            runtime_state=self.runtime_state,
        )

    @cached_property
    def audit_repository(self) -> AuditRepository:
        return AuditRepository(session_factory=self.infrastructure.session_factory)

    @cached_property
    def audit_service(self) -> AuditService:
        return AuditService(repository=self.audit_repository)

    @cached_property
    def monitoring_service(self) -> MonitoringService:
        return MonitoringService(
            health_service=self.health_service,
            runtime_state=self.runtime_state,
        )

    @cached_property
    def rate_limit_service(self) -> RateLimitService:
        return RateLimitService(
            self.infrastructure.redis_client,
            requests=self.settings.rate_limit_requests,
            window_seconds=self.settings.rate_limit_window_seconds,
        )

    @cached_property
    def health_controller(self) -> HealthController:
        return HealthController(service=self.health_service)

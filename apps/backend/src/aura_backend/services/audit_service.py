from __future__ import annotations

from aura_backend.config.logging import get_logger
from aura_backend.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def record_event(
        self,
        *,
        event_name: str,
        actor: str,
        correlation_id: str,
        resource: str,
        action: str,
        status: str,
        event_metadata: dict[str, str | int | float | bool | None],
    ) -> None:
        self._logger.info(
            "audit_event",
            extra={
                "event_name": event_name,
                "actor": actor,
                "resource": resource,
                "action": action,
                "status": status,
                "audit_correlation_id": correlation_id,
                "audit_metadata": event_metadata,
            },
        )
        await self._repository.create(
            event_name=event_name,
            actor=actor,
            correlation_id=correlation_id,
            resource=resource,
            action=action,
            status=status,
            event_metadata=event_metadata,
        )

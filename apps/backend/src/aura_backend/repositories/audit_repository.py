from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from aura_backend.config.logging import get_logger
from aura_backend.models.audit import AuditLog


class AuditRepository:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory
        self._logger = get_logger(__name__)

    async def create(
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
        statement = insert(AuditLog).values(
            event_name=event_name,
            actor=actor,
            correlation_id=correlation_id,
            resource=resource,
            action=action,
            status=status,
            event_metadata=event_metadata,
            created_at=datetime.now(UTC),
        )

        try:
            async with self._session_factory() as session:
                await session.execute(statement)
                await session.commit()
        except SQLAlchemyError:
            self._logger.warning(
                "audit_log_persist_failed",
                extra={
                    "event_name": event_name,
                    "resource": resource,
                    "action": action,
                },
            )

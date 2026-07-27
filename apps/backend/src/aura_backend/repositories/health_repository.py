from __future__ import annotations

import asyncio
import time

import aio_pika
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from aura_backend.api.v1.schemas.health import ComponentHealth
from aura_backend.config.logging import get_logger


class HealthRepository:
    def __init__(
        self,
        database_engine: AsyncEngine,
        redis_client: Redis,
        rabbitmq_url: str,
        timeout_seconds: float,
    ) -> None:
        self._database_engine = database_engine
        self._redis_client = redis_client
        self._rabbitmq_url = rabbitmq_url
        self._timeout_seconds = timeout_seconds
        self._logger = get_logger(__name__)

    async def check_database(self) -> ComponentHealth:
        started_at = time.perf_counter()
        try:
            async with self._database_engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            latency_ms = (time.perf_counter() - started_at) * 1000
            return ComponentHealth(
                status="healthy",
                message="database connection successful",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            return self._failed_component("database", exc)

    async def check_redis(self) -> ComponentHealth:
        started_at = time.perf_counter()
        try:
            await self._redis_client.ping()
            latency_ms = (time.perf_counter() - started_at) * 1000
            return ComponentHealth(
                status="healthy",
                message="redis connection successful",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            return self._failed_component("redis", exc)

    async def check_rabbitmq(self) -> ComponentHealth:
        started_at = time.perf_counter()
        connection: aio_pika.abc.AbstractRobustConnection | None = None
        try:
            connection = await asyncio.wait_for(
                aio_pika.connect_robust(self._rabbitmq_url),
                timeout=self._timeout_seconds,
            )
            latency_ms = (time.perf_counter() - started_at) * 1000
            return ComponentHealth(
                status="healthy",
                message="rabbitmq connection successful",
                latency_ms=round(latency_ms, 2),
            )
        except Exception as exc:
            return self._failed_component("rabbitmq", exc)
        finally:
            if connection is not None:
                await connection.close()

    def _failed_component(self, component: str, exc: Exception) -> ComponentHealth:
        self._logger.warning(
            "health_check_failed",
            extra={
                "component": component,
                "error_type": type(exc).__name__,
            },
        )
        return ComponentHealth(
            status="unhealthy",
            message=f"{component} connectivity failed",
            details={"error_type": type(exc).__name__},
        )

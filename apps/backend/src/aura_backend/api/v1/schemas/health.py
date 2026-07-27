from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

HealthState = Literal["healthy", "degraded", "unhealthy", "unavailable"]


class ComponentHealth(BaseModel):
    status: HealthState = Field(
        examples=["healthy"],
        description="Health status of the component",
    )
    message: str = Field(
        examples=["database connection established"],
        description="Human-readable status message",
    )
    latency_ms: float | None = Field(
        default=None,
        examples=[15.3],
        description="Response latency in milliseconds",
    )
    details: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict,
        examples=[{"version": "14.0", "pool_size": 10}],
        description="Additional component-specific details",
    )


class ResourceMetric(BaseModel):
    status: HealthState = Field(
        examples=["healthy"],
        description="Resource health status",
    )
    total: int | None = Field(
        default=None,
        examples=[1099511627776],
        description="Total resource capacity (bytes/count)",
    )
    used: int | None = Field(
        default=None,
        examples=[549755813888],
        description="Resource usage (bytes/count)",
    )
    free: int | None = Field(
        default=None,
        examples=[549755813888],
        description="Available resource (bytes/count)",
    )
    percent: float | None = Field(
        default=None,
        examples=[50.0],
        description="Usage percentage (0-100)",
    )
    details: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict,
        examples=[{"mounted": "/", "type": "ext4"}],
        description="Additional resource-specific details",
    )


class HealthResponse(BaseModel):
    service: str = Field(
        examples=["aura"],
        description="Service identifier",
    )
    environment: str = Field(
        examples=["production"],
        description="Deployment environment",
    )
    version: str = Field(
        examples=["0.1.0"],
        description="Service version",
    )
    status: HealthState = Field(
        examples=["healthy"],
        description="Overall health status",
    )
    timestamp: datetime = Field(
        examples=["2024-01-15T10:30:00Z"],
        description="Health check timestamp (ISO 8601)",
    )
    backend: ComponentHealth = Field(
        description="Backend service health",
    )
    database: ComponentHealth = Field(
        description="Database service health",
    )
    redis: ComponentHealth = Field(
        description="Redis service health",
    )
    rabbitmq: ComponentHealth = Field(
        description="RabbitMQ service health",
    )
    gpu: ResourceMetric = Field(
        description="GPU resource metrics",
    )
    disk: ResourceMetric = Field(
        description="Disk resource metrics",
    )
    memory: ResourceMetric = Field(
        description="Memory resource metrics",
    )
    uptime_seconds: float = Field(
        examples=[3600.5],
        description="Service uptime in seconds",
    )

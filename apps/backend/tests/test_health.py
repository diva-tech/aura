from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from aura_backend.api.dependencies import get_health_controller
from aura_backend.api.v1.schemas.health import ComponentHealth, HealthResponse, ResourceMetric
from aura_backend.main import app


class StubHealthController:
    async def get_health_status(self) -> HealthResponse:
        component = ComponentHealth(status="healthy", message="ok", latency_ms=1.0)
        resource = ResourceMetric(status="healthy", total=100, used=10, free=90, percent=10.0)
        return HealthResponse(
            service="AURA",
            environment="test",
            version="0.1.0",
            status="healthy",
            timestamp=datetime.now(UTC),
            backend=component,
            database=component,
            redis=component,
            rabbitmq=component,
            gpu=resource,
            disk=resource,
            memory=resource,
            uptime_seconds=1.0,
        )


class StubRateLimitService:
    async def enforce(self, *, key: str, scope: str) -> None:
        return None


class StubAuditService:
    async def record_event(self, **_: object) -> None:
        return None


@pytest.mark.anyio
async def test_health_endpoint_returns_expected_shape() -> None:
    app.dependency_overrides[get_health_controller] = lambda: StubHealthController()
    app.state.container = SimpleNamespace(
        rate_limit_service=StubRateLimitService(),
        audit_service=StubAuditService(),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/health", headers={"x-request-id": "test-request-id"})

        assert response.status_code == 200
        payload = response.json()

        assert payload["service"] == "AURA"
        assert payload["status"] == "healthy"
        assert payload["version"] == "0.1.0"
        assert "backend" in payload
        assert "database" in payload
        assert "redis" in payload
        assert "rabbitmq" in payload
        assert "gpu" in payload
        assert "disk" in payload
        assert "memory" in payload
        assert response.headers["x-request-id"] == "test-request-id"
    app.dependency_overrides.clear()

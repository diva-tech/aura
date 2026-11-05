from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        container = request.app.state.container
        correlation_id = getattr(request.state, "request_id", "-")
        actor = request.headers.get("x-user-id", "system")

        await container.audit_service.record_event(
            event_name="http_request",
            actor=actor,
            correlation_id=correlation_id,
            resource=str(request.url.path),
            action=request.method,
            status=str(response.status_code),
            event_metadata={
                "query": str(request.url.query),
                "client_ip": request.client.host if request.client is not None else "unknown",
            },
        )
        return response

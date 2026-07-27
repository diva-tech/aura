from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        container = request.app.state.container
        client_ip = request.client.host if request.client is not None else "unknown"
        key = f"{client_ip}:{request.url.path}"
        scope = f"{request.method} {request.url.path}"
        await container.rate_limit_service.enforce(key=key, scope=scope)
        return await call_next(request)

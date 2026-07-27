from __future__ import annotations

import time
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from aura_backend.services.metrics_service import (
    active_requests,
    exceptions_raised,
    request_count,
    request_duration,
    request_size,
    response_size,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        endpoint = request.url.path
        method = request.method

        active_requests.inc()
        start_time = time.perf_counter()

        try:
            request_size.labels(method=method, endpoint=endpoint).observe(
                len(await request.body()) if request.method in ("POST", "PUT") else 0
            )
        except Exception:
            pass

        try:
            response = await call_next(request)
        except Exception as exc:
            exceptions_raised.labels(exception_type=type(exc).__name__).inc()
            raise
        finally:
            active_requests.dec()

        duration = time.perf_counter() - start_time
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        request_count.labels(
            method=method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()

        try:
            response_size.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
            ).observe(len(response.body) if hasattr(response, "body") else 0)
        except Exception:
            pass

        return response

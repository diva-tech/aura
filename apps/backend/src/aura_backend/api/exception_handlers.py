from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from aura_backend.api.v1.schemas.common import ErrorResponse
from aura_backend.config.logging import get_logger
from aura_backend.core.exceptions import AuraError, RateLimitExceededError
from aura_backend.core.request_context import get_request_id


def register_exception_handlers(application: FastAPI) -> None:
    logger = get_logger(__name__)

    @application.exception_handler(AuraError)
    async def aura_exception_handler(
        request: Request,
        exc: AuraError,
    ) -> JSONResponse:
        logger.warning(
            "application_exception",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "error_code": exc.error_code,
            },
        )
        payload = ErrorResponse(
            detail=exc.message,
            correlation_id=get_request_id(),
            error_code=exc.error_code,
            timestamp=datetime.now(UTC),
            details=exc.details,
        )
        response = JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(mode="json"),
        )
        if isinstance(exc, RateLimitExceededError):
            response.headers["retry-after"] = str(exc.details["retry_after_seconds"])
        return response

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "request_validation_failed",
            extra={
                "path": str(request.url.path),
                "method": request.method,
            },
        )
        payload = ErrorResponse(
            detail="Request validation failed.",
            correlation_id=get_request_id(),
            error_code="request_validation_failed",
            timestamp=datetime.now(UTC),
            details={"error_count": len(exc.errors())},
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            extra={
                "path": str(request.url.path),
                "method": request.method,
            },
        )
        payload = ErrorResponse(
            detail="An internal server error occurred.",
            correlation_id=get_request_id(),
            error_code="internal_server_error",
            timestamp=datetime.now(UTC),
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))

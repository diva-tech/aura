from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from aura_backend.api.exception_handlers import register_exception_handlers
from aura_backend.api.router import api_router
from aura_backend.config.logging import configure_logging, get_logger
from aura_backend.config.settings import get_settings
from aura_backend.core.clients import close_infrastructure_clients, create_infrastructure_clients
from aura_backend.core.container import ApplicationContainer
from aura_backend.core.openapi import configure_openapi
from aura_backend.core.runtime import RuntimeState
from aura_backend.middleware.audit_logging import AuditLoggingMiddleware
from aura_backend.middleware.metrics import MetricsMiddleware
from aura_backend.middleware.rate_limit import RateLimitMiddleware
from aura_backend.middleware.request_id import RequestIdMiddleware
from aura_backend.middleware.request_logging import RequestLoggingMiddleware
from aura_backend.middleware.security_headers import SecurityHeadersMiddleware

APPLICATION_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    infrastructure = await create_infrastructure_clients(settings)
    runtime_state = RuntimeState.create(version=APPLICATION_VERSION)
    app.state.container = ApplicationContainer(
        settings=settings,
        infrastructure=infrastructure,
        runtime_state=runtime_state,
    )
    logger = get_logger(__name__)
    logger.info("application_starting", extra={"environment": settings.environment})
    yield
    await close_infrastructure_clients(infrastructure)
    logger.info("application_stopping")


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=APPLICATION_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        contact={
            "name": "AURA Support",
            "url": "https://github.com/dilippottigari/aura",
            "email": "vasudha.samudrala@divatech.in",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        terms_of_service="https://github.com/dilippottigari/aura/blob/main/LICENSE",
    )
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(MetricsMiddleware)
    application.add_middleware(AuditLoggingMiddleware)
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(RequestIdMiddleware)
    application.include_router(api_router, prefix="/api")
    configure_openapi(application)
    register_exception_handlers(application)
    return application


app = create_application()

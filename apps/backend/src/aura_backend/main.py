from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from aura_backend.agents.editor_agent import EditorAgent
from aura_backend.agents.seo_agent import SEOAgent
from aura_backend.api.exception_handlers import register_exception_handlers
from aura_backend.api.router import api_router
from aura_backend.config.logging import configure_logging, get_logger
from aura_backend.config.settings import get_settings
from aura_backend.core.bootstrap import Runtime
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
from aura_backend.plugins.logging_plugin import LoggingPlugin
from aura_backend.plugins.storage_plugin import StoragePlugin

APPLICATION_VERSION = "0.2.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)
    infrastructure = await create_infrastructure_clients(settings)
    runtime_state = RuntimeState.create(version=APPLICATION_VERSION)
    app.state.container = ApplicationContainer(
        settings=settings,
        infrastructure=infrastructure,
        runtime_state=runtime_state,
    )

    # Initialize AURA Runtime
    aura_runtime = Runtime(version=APPLICATION_VERSION)
    aura_runtime.plugins.register(LoggingPlugin())
    aura_runtime.plugins.register(StoragePlugin())
    aura_runtime.agents.register_instance(EditorAgent())
    aura_runtime.agents.register_instance(SEOAgent())

    logger.info("application_starting", extra={"environment": settings.environment})
    await aura_runtime.startup()
    app.state.aura_runtime = aura_runtime

    yield

    await aura_runtime.shutdown()
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

    # Serve dashboard
    @application.get("/")
    def dashboard():
        """Serve AURA dashboard."""
        static_path = Path(__file__).parent.parent.parent / "static" / "index.html"
        if static_path.exists():
            return FileResponse(str(static_path), media_type="text/html")
        return {"message": "AURA v1.0 - Dashboard not available"}

    # Mount static files
    static_dir = Path(__file__).parent.parent.parent / "static"
    if static_dir.exists():
        application.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    configure_openapi(application)
    register_exception_handlers(application)
    return application


app = create_application()

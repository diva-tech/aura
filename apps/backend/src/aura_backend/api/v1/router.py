from fastapi import APIRouter

from aura_backend.api.v1.dashboard import router as dashboard_router
from aura_backend.api.v1.health import router as health_router
from aura_backend.api.v1.runtime import router as runtime_router

v1_router = APIRouter()
v1_router.include_router(health_router, tags=["health"])
v1_router.include_router(runtime_router, tags=["runtime"])
v1_router.include_router(dashboard_router, tags=["dashboard"])

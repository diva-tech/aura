from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get("/runtime/status", summary="Get AURA runtime status")
async def get_runtime_status(request: Request) -> Dict[str, Any]:
    """
    Returns complete AURA runtime status including:
    - Runtime version and uptime
    - Registered services with stats
    - Loaded plugins with metadata
    - Registered agents with status
    - Event bus statistics
    """
    aura_runtime = getattr(request.app.state, "aura_runtime", None)
    if aura_runtime is None:
        return {
            "status": "unavailable",
            "message": "AURA Runtime not initialized",
        }

    health = await aura_runtime.health()
    return health


@router.get("/runtime/info", summary="Get AURA runtime information")
async def get_runtime_info(request: Request) -> Dict[str, Any]:
    """
    Returns detailed AURA runtime information including:
    - Version and status
    - Service registry summary
    - Plugin registry summary
    - Agent registry summary
    - Event bus statistics
    """
    aura_runtime = getattr(request.app.state, "aura_runtime", None)
    if aura_runtime is None:
        return {
            "version": "0.0.0",
            "status": "unavailable",
            "message": "AURA Runtime not initialized",
        }

    return aura_runtime.get_info()

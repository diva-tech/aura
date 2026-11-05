from __future__ import annotations

from fastapi import FastAPI


def configure_openapi(application: FastAPI) -> None:
    application.openapi_tags = [
        {
            "name": "health",
            "description": "Platform liveness, readiness, and dependency health endpoints.",
        }
    ]

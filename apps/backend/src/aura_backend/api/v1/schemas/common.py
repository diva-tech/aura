from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str
    correlation_id: str
    error_code: str
    timestamp: datetime
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)

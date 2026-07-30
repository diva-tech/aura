"""Render schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RenderLogResponse(BaseModel):
    """Render log entry response."""

    id: str
    render_id: str
    stage: str
    status: str
    message: Optional[str]
    progress_percent: Optional[float]
    duration: Optional[int]
    error_code: Optional[str]
    timestamp: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RenderAssetResponse(BaseModel):
    """Render asset response."""

    id: str
    render_id: str
    asset_type: str
    file_path: str
    file_size: Optional[int]
    file_format: Optional[str]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RenderMetadataResponse(BaseModel):
    """Render metadata response."""

    id: str
    render_id: str
    total_frames: Optional[int]
    frames_processed: int
    gpu_usage_peak: Optional[float]
    cpu_usage_peak: Optional[float]
    memory_usage_peak: Optional[int]
    bitrate_actual: Optional[str]
    actual_fps: Optional[float]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RenderResponse(BaseModel):
    """Render response."""

    id: str
    project_id: str
    preview_id: str
    edit_plan_id: str
    status: str
    quality: str
    platform: Optional[str]
    priority: int
    output_path: Optional[str]
    output_size: Optional[int]
    duration: Optional[int]
    fps: Optional[int]
    resolution: Optional[str]
    codec: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_time: Optional[int]
    elapsed_time: int
    progress_percent: float
    current_stage: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RenderDetailResponse(BaseModel):
    """Render detail response with all related data."""

    render: RenderResponse
    logs: list[RenderLogResponse] = []
    assets: list[RenderAssetResponse] = []
    metadata: Optional[RenderMetadataResponse]

    class Config:
        """Pydantic config."""

        from_attributes = True


class StartRenderRequest(BaseModel):
    """Start render request."""

    quality: str = "standard"  # draft, standard, high, ultra
    platform: Optional[str] = None
    priority: int = 5


class RenderCancelRequest(BaseModel):
    """Cancel render request."""

    cancel: bool = True


class RenderRetryRequest(BaseModel):
    """Retry failed render request."""

    retry: bool = True

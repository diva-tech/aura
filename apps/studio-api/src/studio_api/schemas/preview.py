"""Preview schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class RenderSettingsResponse(BaseModel):
    """Render settings response."""

    id: str
    project_id: str
    resolution: str
    fps: int
    codec: str
    bitrate: str
    platform: Optional[str]
    audio_bitrate: str
    audio_codec: str
    quality_level: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RenderEstimateResponse(BaseModel):
    """Render estimate response."""

    id: str
    project_id: str
    edit_plan_id: str
    estimated_duration: Optional[int]
    estimated_render_time: Optional[int]
    estimated_output_size: Optional[int]
    gpu_usage_percent: Optional[float]
    cpu_usage_percent: Optional[float]
    operations_count: int
    effects_count: int
    captions_count: int
    transitions_count: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PreviewValidationError(BaseModel):
    """Validation error."""

    type: str
    message: str
    severity: str  # error, warning


class PreviewValidationResponse(BaseModel):
    """Preview validation response."""

    id: str
    preview_id: str
    is_valid: bool
    errors: list[PreviewValidationError] = []
    warnings: list[PreviewValidationError] = []
    checked_assets: bool
    checked_operations: bool
    checked_audio: bool
    checked_fonts: bool
    checked_overlays: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PreviewFrameCommentResponse(BaseModel):
    """Preview frame comment response."""

    id: str
    preview_id: str
    timestamp: int
    text: str
    author: Optional[str]
    resolved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PreviewResponse(BaseModel):
    """Preview response."""

    id: str
    project_id: str
    edit_plan_id: str
    version: int
    status: str
    quality: str
    approved: bool
    file_path: Optional[str]
    duration: Optional[int]
    filesize: Optional[int]
    estimated_render_time: Optional[int]
    estimated_output_size: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PreviewDetailResponse(BaseModel):
    """Preview detail response with all related data."""

    preview: PreviewResponse
    settings: RenderSettingsResponse
    estimate: RenderEstimateResponse
    validation: Optional[PreviewValidationResponse]
    comments: list[PreviewFrameCommentResponse] = []

    class Config:
        """Pydantic config."""

        from_attributes = True


class GeneratePreviewRequest(BaseModel):
    """Generate preview request."""

    quality: str = "medium"  # low, medium, high
    include_effects: bool = True
    generate_proxy: bool = True


class PreviewSettingsUpdateRequest(BaseModel):
    """Update preview settings request."""

    resolution: Optional[str] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    bitrate: Optional[str] = None
    platform: Optional[str] = None
    quality_level: Optional[int] = None


class ApprovePreviewRequest(BaseModel):
    """Approve preview request."""

    approved: bool = True


class PreviewCommentRequest(BaseModel):
    """Add preview comment request."""

    timestamp: int
    text: str
    author: Optional[str] = None

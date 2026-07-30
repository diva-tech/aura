"""Edit plan schemas."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class EditOperationResponse(BaseModel):
    """Edit operation response."""

    id: str
    edit_plan_id: str
    clip_id: Optional[str]
    operation_type: str
    start_time: int
    end_time: int
    title: str
    description: Optional[str]
    reason: Optional[str]
    suggestion_id: Optional[str]
    enabled: bool
    applied: bool
    order: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimelineClipResponse(BaseModel):
    """Timeline clip response."""

    id: str
    track_id: str
    start_time: int
    end_time: int
    source_start: Optional[int]
    source_end: Optional[int]
    clip_type: str
    title: Optional[str]
    description: Optional[str]
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimelineTrackResponse(BaseModel):
    """Timeline track response."""

    id: str
    edit_plan_id: str
    track_type: str
    order: int
    height: int
    locked: bool
    visible: bool
    label: Optional[str]
    clips: list[TimelineClipResponse] = []
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransitionResponse(BaseModel):
    """Transition response."""

    id: str
    edit_plan_id: str
    from_clip_id: str
    to_clip_id: str
    transition_type: str
    duration: int
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CaptionResponse(BaseModel):
    """Caption response."""

    id: str
    edit_plan_id: str
    start_time: int
    end_time: int
    text: str
    style: Optional[str]
    font_size: int
    position: str
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class OverlayResponse(BaseModel):
    """Overlay response."""

    id: str
    edit_plan_id: str
    start_time: int
    end_time: int
    overlay_type: str
    title: str
    data: Optional[str]
    position: str
    opacity: float
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ZoomEffectResponse(BaseModel):
    """Zoom effect response."""

    id: str
    edit_plan_id: str
    clip_id: str
    start_time: int
    end_time: int
    zoom_level: float
    pan_x: float
    pan_y: float
    easing: str
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MusicTrackResponse(BaseModel):
    """Music track response."""

    id: str
    edit_plan_id: str
    start_time: int
    end_time: int
    title: Optional[str]
    file_path: Optional[str]
    volume: float
    fade_in: int
    fade_out: int
    enabled: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class EditPlanCommentResponse(BaseModel):
    """Edit plan comment response."""

    id: str
    edit_plan_id: str
    timestamp: int
    text: str
    author: Optional[str]
    resolved: bool
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class EditPlanHistoryResponse(BaseModel):
    """Edit plan history response."""

    id: str
    edit_plan_id: str
    version: int
    change_type: str
    description: Optional[str]
    data: Optional[str]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class EditPlanResponse(BaseModel):
    """Edit plan response."""

    id: str
    project_id: str
    version: int
    status: str
    approved: bool
    estimated_duration: Optional[int]
    estimated_render_time: Optional[int]
    change_count: int
    tracks: list[TimelineTrackResponse] = []
    operations: list[EditOperationResponse] = []
    transitions: list[TransitionResponse] = []
    captions: list[CaptionResponse] = []
    overlays: list[OverlayResponse] = []
    zoom_effects: list[ZoomEffectResponse] = []
    music_tracks: list[MusicTrackResponse] = []
    comments: list[EditPlanCommentResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class EditPlanCreateRequest(BaseModel):
    """Create edit plan request."""

    pass


class EditPlanUpdateRequest(BaseModel):
    """Update edit plan request."""

    status: Optional[str] = None
    approved: Optional[bool] = None


class EditPlanApproveRequest(BaseModel):
    """Approve edit plan request."""

    approved: bool = True


class EditPlanRegenerateRequest(BaseModel):
    """Regenerate edit plan request."""

    prompt: str

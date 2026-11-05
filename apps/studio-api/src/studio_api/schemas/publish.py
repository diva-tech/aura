"""Publish schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlatformAccountResponse(BaseModel):
    """Platform account response."""

    id: str
    platform: str
    account_name: str
    account_id: str
    is_connected: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PublishMetadataResponse(BaseModel):
    """Publish metadata response."""

    id: str
    publish_job_id: str
    platform: str
    title: Optional[str]
    description: Optional[str]
    tags: Optional[str]
    caption: Optional[str]
    hashtags: Optional[str]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PublishJobResponse(BaseModel):
    """Publish job response."""

    id: str
    render_id: str
    project_id: str
    platform_account_id: str
    platform: str
    status: str
    scheduled_time: Optional[datetime]
    published_at: Optional[datetime]
    platform_video_id: Optional[str]
    platform_url: Optional[str]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PublishHistoryResponse(BaseModel):
    """Publish history response."""

    id: str
    publish_job_id: str
    event_type: str
    status: str
    message: Optional[str]
    timestamp: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PlatformHealthResponse(BaseModel):
    """Platform health response."""

    id: str
    platform: str
    is_healthy: bool
    last_check: datetime
    response_time_ms: Optional[int]
    error_message: Optional[str]
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class PublishRequest(BaseModel):
    """Publish request."""

    render_id: str
    platform_account_id: str
    platform: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    caption: Optional[str] = None
    hashtags: Optional[list[str]] = None
    scheduled_time: Optional[datetime] = None


class ConnectPlatformRequest(BaseModel):
    """Connect platform account request."""

    platform: str
    auth_code: str


class PublishRetryRequest(BaseModel):
    """Retry publish request."""

    retry: bool = True

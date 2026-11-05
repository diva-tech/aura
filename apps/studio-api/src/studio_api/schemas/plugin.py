"""Plugin SDK & Marketplace schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PluginResponse(BaseModel):
    """Plugin response."""

    id: str
    name: str
    version: str
    description: str
    author: str
    author_url: Optional[str] = None
    license: str
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    status: str
    icon_url: Optional[str] = None
    manifest: str
    api_types: str
    permissions: str
    settings_schema: Optional[str] = None
    sandbox_enabled: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PluginInstallationResponse(BaseModel):
    """Plugin installation response."""

    id: str
    plugin_id: str
    project_id: str
    version_installed: str
    status: str
    auto_update: str
    settings: Optional[str] = None
    installed_at: datetime
    enabled_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PluginAPIResponse(BaseModel):
    """Plugin API response."""

    id: str
    plugin_id: str
    api_type: str
    name: str
    description: str
    endpoint: str
    method: str
    version: str
    enabled: str
    created_at: datetime

    class Config:
        from_attributes = True


class PluginMarketplaceResponse(BaseModel):
    """Marketplace entry response."""

    id: str
    plugin_id: str
    downloads: int
    average_rating: float
    total_ratings: int
    featured: str
    category: Optional[str] = None
    tags: Optional[str] = None
    changelog: Optional[str] = None
    verified: str
    verified_at: Optional[datetime] = None
    published_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PluginRatingResponse(BaseModel):
    """Plugin rating response."""

    id: str
    plugin_id: str
    project_id: str
    rating: int
    title: Optional[str] = None
    review: Optional[str] = None
    helpful_count: int
    unhelpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PluginManifestRequest(BaseModel):
    """Plugin manifest submission."""

    id: str
    name: str
    version: str
    description: str
    author: str
    author_url: Optional[str] = None
    license: str = "MIT"
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    icon_url: Optional[str] = None
    permissions: list[str]
    apis: list[dict]  # API definitions
    settings_schema: Optional[dict] = None


class PluginInstallRequest(BaseModel):
    """Install plugin request."""

    version: Optional[str] = None  # if None, use latest
    auto_update: bool = True


class PluginSettingsUpdateRequest(BaseModel):
    """Update plugin settings."""

    settings: dict


class PluginRatingRequest(BaseModel):
    """Rate plugin request."""

    rating: int  # 1-5
    title: Optional[str] = None
    review: Optional[str] = None


class PluginOAuthRequest(BaseModel):
    """OAuth connection request."""

    provider: str
    code: str
    redirect_uri: str


class PluginDetailResponse(BaseModel):
    """Complete plugin details."""

    plugin: PluginResponse
    marketplace: Optional[PluginMarketplaceResponse] = None
    installation: Optional[PluginInstallationResponse] = None
    apis: list[PluginAPIResponse]
    rating: Optional[PluginRatingResponse] = None
    ratings_summary: dict  # {"average": 4.5, "count": 120}

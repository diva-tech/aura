"""AURA AI Copilot schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CopilotChatCreate(BaseModel):
    """Create chat message."""

    role: str
    message: str
    context: Optional[dict] = None


class CopilotChatResponse(BaseModel):
    """Chat message response."""

    id: str
    project_id: str
    role: str
    message: str
    context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CopilotMemoryCreate(BaseModel):
    """Create memory."""

    memory_type: str
    key: str
    value: dict


class CopilotMemoryResponse(BaseModel):
    """Memory response."""

    id: str
    project_id: str
    memory_type: str
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CopilotRecommendationCreate(BaseModel):
    """Create recommendation."""

    recommendation_type: str
    title: str
    description: str
    action: Optional[str] = None
    priority: int = 5


class CopilotRecommendationResponse(BaseModel):
    """Recommendation response."""

    id: str
    project_id: str
    recommendation_type: str
    title: str
    description: str
    action: Optional[str] = None
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True


class CopilotActionCreate(BaseModel):
    """Create action."""

    action_type: str
    title: str
    description: str
    metadata: Optional[dict] = None


class CopilotActionResponse(BaseModel):
    """Action response."""

    id: str
    project_id: str
    action_type: str
    title: str
    description: str
    metadata: Optional[str] = None
    completed: str
    created_at: datetime

    class Config:
        from_attributes = True


class CopilotChatRequest(BaseModel):
    """Chat request."""

    message: str
    context: Optional[dict] = None


class CopilotChatResponseWrapper(BaseModel):
    """Wrapped chat response."""

    user_message: CopilotChatResponse
    assistant_message: CopilotChatResponse
    orchestration_context: Optional[dict] = None

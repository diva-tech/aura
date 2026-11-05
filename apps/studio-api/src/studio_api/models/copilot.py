"""AURA AI Copilot models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from studio_api.database.base import Base


class CopilotChat(Base):
    """Copilot chat history."""

    __tablename__ = "copilot_chats"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)  # JSON with context data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CopilotMemory(Base):
    """Copilot user preferences and memory."""

    __tablename__ = "copilot_memory"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CopilotRecommendation(Base):
    """Copilot recommendations."""

    __tablename__ = "copilot_recommendations"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    recommendation_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    action = Column(String(50), nullable=True)  # generate_edit_plan, reanalyze, etc.
    priority = Column(Integer, default=5)  # 1-10
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CopilotAction(Base):
    """Copilot recommended actions."""

    __tablename__ = "copilot_actions"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON with action params
    completed = Column(String(50), default="pending")  # pending, completed, dismissed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

"""Edit plan models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from studio_api.database.base import Base


class EditOperationType(str, Enum):
    """Edit operation types."""

    CUT = "cut"
    TRIM = "trim"
    SPLIT = "split"
    MOVE = "move"
    DELETE = "delete"
    SPEED = "speed"
    FREEZE = "freeze"
    COLOR = "color"
    AUDIO = "audio"
    ZOOM = "zoom"
    CROP = "crop"
    ROTATE = "rotate"


class TrackType(str, Enum):
    """Track types in timeline."""

    VIDEO = "video"
    AUDIO = "audio"
    CAPTION = "caption"
    OVERLAY = "overlay"
    MUSIC = "music"
    TRANSITION = "transition"
    ZOOM = "zoom"


class EditPlan(Base):
    """Edit plan container."""

    __tablename__ = "edit_plans"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="draft")  # draft, pending_review, approved, rendering
    approved = Column(Boolean, default=False)
    estimated_duration = Column(Integer, nullable=True)  # milliseconds
    estimated_render_time = Column(Integer, nullable=True)  # seconds
    change_count = Column(Integer, default=0)  # track number of changes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class TimelineTrack(Base):
    """Timeline track container."""

    __tablename__ = "timeline_tracks"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    track_type = Column(SQLEnum(TrackType), nullable=False)
    order = Column(Integer, nullable=False)  # display order
    height = Column(Integer, default=80)  # px
    locked = Column(Boolean, default=False)
    visible = Column(Boolean, default=True)
    label = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TimelineClip(Base):
    """Clip on timeline."""

    __tablename__ = "timeline_clips"

    id = Column(String(36), primary_key=True, index=True)
    track_id = Column(String(36), ForeignKey("timeline_tracks.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # ms on timeline
    end_time = Column(Integer, nullable=False)
    source_start = Column(Integer, nullable=True)  # ms in source video
    source_end = Column(Integer, nullable=True)
    clip_type = Column(String(50), nullable=False)  # video, audio, text, effect, etc.
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class EditOperation(Base):
    """Single edit operation from AI suggestions."""

    __tablename__ = "edit_operations"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    clip_id = Column(String(36), ForeignKey("timeline_clips.id"), nullable=True)
    operation_type = Column(SQLEnum(EditOperationType), nullable=False)
    start_time = Column(Integer, nullable=False)  # ms
    end_time = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    suggestion_id = Column(String(36), nullable=True)  # from AI suggestions
    parameters = Column(Text, nullable=True)  # JSON with operation params
    enabled = Column(Boolean, default=True)
    applied = Column(Boolean, default=False)
    order = Column(Integer, nullable=False)  # execution order
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transition(Base):
    """Transition between clips."""

    __tablename__ = "transitions"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    from_clip_id = Column(String(36), ForeignKey("timeline_clips.id"), nullable=False)
    to_clip_id = Column(String(36), ForeignKey("timeline_clips.id"), nullable=False)
    transition_type = Column(String(50), nullable=False)  # fade, cut, crossfade, slide, etc.
    duration = Column(Integer, default=300)  # ms
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Caption(Base):
    """Caption on caption track."""

    __tablename__ = "captions"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # ms
    end_time = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    style = Column(String(50), nullable=True)  # font, color, position
    font_size = Column(Integer, default=24)
    position = Column(String(50), default="bottom")  # top, center, bottom
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Overlay(Base):
    """Overlay element."""

    __tablename__ = "overlays"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # ms
    end_time = Column(Integer, nullable=False)
    overlay_type = Column(String(50), nullable=False)  # image, text, logo, cta, etc.
    title = Column(String(255), nullable=False)
    data = Column(Text, nullable=True)  # JSON with overlay data
    position = Column(String(50), default="center")
    opacity = Column(Float, default=1.0)  # 0-1
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ZoomEffect(Base):
    """Zoom effect on clip."""

    __tablename__ = "zoom_effects"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    clip_id = Column(String(36), ForeignKey("timeline_clips.id"), nullable=False)
    start_time = Column(Integer, nullable=False)  # ms
    end_time = Column(Integer, nullable=False)
    zoom_level = Column(Float, default=1.0)  # 1.0 = no zoom
    pan_x = Column(Float, default=0.5)  # 0-1, horizontal position
    pan_y = Column(Float, default=0.5)  # 0-1, vertical position
    easing = Column(String(50), default="ease-in-out")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MusicTrack(Base):
    """Background music track."""

    __tablename__ = "music_tracks"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    start_time = Column(Integer, nullable=False)  # ms
    end_time = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    volume = Column(Float, default=0.8)  # 0-1
    fade_in = Column(Integer, default=0)  # ms
    fade_out = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EditPlanComment(Base):
    """Comments on edit plan."""

    __tablename__ = "edit_plan_comments"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    timestamp = Column(Integer, nullable=False)  # ms on timeline
    text = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EditPlanHistory(Base):
    """Change history for edit plans."""

    __tablename__ = "edit_plan_history"

    id = Column(String(36), primary_key=True, index=True)
    edit_plan_id = Column(String(36), ForeignKey("edit_plans.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False)  # ai_regenerate, manual_edit, undo, redo
    description = Column(Text, nullable=True)
    data = Column(Text, nullable=True)  # JSON snapshot of changes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

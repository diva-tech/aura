"""
Agent execution sessions.

Represents a single agent execution session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class SessionStatus(str, Enum):
    """Session status"""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Session:
    """Represents a single agent execution session"""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    goal_id: str = ""
    status: SessionStatus = SessionStatus.CREATED

    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Mark session as started"""
        self.started_at = datetime.utcnow()
        self.status = SessionStatus.RUNNING

    def complete(self) -> None:
        """Mark session as completed"""
        self.completed_at = datetime.utcnow()
        self.status = SessionStatus.COMPLETED

    def fail(self) -> None:
        """Mark session as failed"""
        self.completed_at = datetime.utcnow()
        self.status = SessionStatus.FAILED

    def cancel(self) -> None:
        """Mark session as cancelled"""
        self.completed_at = datetime.utcnow()
        self.status = SessionStatus.CANCELLED

    def duration_ms(self) -> Optional[float]:
        """Get session duration"""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.utcnow()
        return (end - self.started_at).total_seconds() * 1000


class SessionManager:
    """Manages agent execution sessions"""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._agent_sessions: Dict[str, list[str]] = {}

    def create_session(self, agent_id: str, goal_id: str) -> Session:
        """Create new session"""
        session = Session(agent_id=agent_id, goal_id=goal_id)
        self._sessions[session.session_id] = session

        if agent_id not in self._agent_sessions:
            self._agent_sessions[agent_id] = []
        self._agent_sessions[agent_id].append(session.session_id)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        return self._sessions.get(session_id)

    def list_sessions(self, agent_id: Optional[str] = None) -> list[Session]:
        """List sessions"""
        if agent_id:
            session_ids = self._agent_sessions.get(agent_id, [])
            return [self._sessions[sid] for sid in session_ids if sid in self._sessions]
        return list(self._sessions.values())

    def count_sessions(self, agent_id: Optional[str] = None, status: Optional[SessionStatus] = None) -> int:
        """Count sessions"""
        sessions = self.list_sessions(agent_id)
        if status:
            sessions = [s for s in sessions if s.status == status]
        return len(sessions)

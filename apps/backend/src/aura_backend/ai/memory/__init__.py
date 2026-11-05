"""
Memory abstractions.

Defines interfaces for agent memory without implementation.
No persistence or vector databases included - contracts only.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryItem:
    """Single memory item"""

    id: str
    content: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    embeddings: Optional[List[float]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class WorkingMemory(ABC):
    """
    Temporary memory for current execution.

    Short-lived, focused on immediate task state.
    """

    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Store value in working memory"""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from working memory"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all working memory"""
        pass

    @abstractmethod
    async def list_keys(self) -> List[str]:
        """List all keys in working memory"""
        pass


class LongTermMemory(ABC):
    """
    Persistent memory across executions.

    Long-lived, carries knowledge between sessions.
    """

    @abstractmethod
    async def store(self, item: MemoryItem) -> None:
        """Store memory item"""
        pass

    @abstractmethod
    async def retrieve(self, id: str) -> Optional[MemoryItem]:
        """Retrieve memory item by ID"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete memory item"""
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search memory items"""
        pass


class SemanticMemory(ABC):
    """
    Conceptual knowledge and relationships.

    Facts, concepts, and their relationships.
    """

    @abstractmethod
    async def store_concept(self, concept: str, description: str, metadata: Dict[str, Any] = None) -> None:
        """Store a concept"""
        pass

    @abstractmethod
    async def retrieve_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """Retrieve concept information"""
        pass

    @abstractmethod
    async def find_related(self, concept: str, limit: int = 10) -> List[str]:
        """Find related concepts"""
        pass


class EpisodicMemory(ABC):
    """
    Event-based memory of past executions.

    Episodes: specific execution sessions with full context.
    """

    @abstractmethod
    async def record_episode(self, episode_id: str, content: Dict[str, Any]) -> None:
        """Record an execution episode"""
        pass

    @abstractmethod
    async def retrieve_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve episode details"""
        pass

    @abstractmethod
    async def list_episodes(self, limit: int = 10) -> List[str]:
        """List recent episode IDs"""
        pass


class ConversationMemory(ABC):
    """
    Dialogue history and context.

    Messages, turns, and conversation state.
    """

    @abstractmethod
    async def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """Add message to conversation"""
        pass

    @abstractmethod
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages"""
        pass

    @abstractmethod
    async def get_context(self) -> Dict[str, Any]:
        """Get conversation context"""
        pass

    @abstractmethod
    async def clear_history(self) -> None:
        """Clear conversation history"""
        pass


class MemoryStore(ABC):
    """
    Unified memory interface.

    Coordinates all memory types for an agent.
    """

    @abstractmethod
    async def get_working_memory(self) -> WorkingMemory:
        """Get working memory"""
        pass

    @abstractmethod
    async def get_long_term_memory(self) -> LongTermMemory:
        """Get long-term memory"""
        pass

    @abstractmethod
    async def get_semantic_memory(self) -> SemanticMemory:
        """Get semantic memory"""
        pass

    @abstractmethod
    async def get_episodic_memory(self) -> EpisodicMemory:
        """Get episodic memory"""
        pass

    @abstractmethod
    async def get_conversation_memory(self) -> ConversationMemory:
        """Get conversation memory"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get memory health status"""
        pass

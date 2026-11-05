"""Memory type interfaces."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aura_backend.memory.knowledge.objects import MemoryItem, MemoryType


class MemoryTypeInterface(ABC):
    """Base interface for all memory types"""

    @property
    @abstractmethod
    def memory_type(self) -> MemoryType:
        """Return the memory type"""
        pass

    @property
    @abstractmethod
    def max_size(self) -> int:
        """Maximum number of items in this memory type"""
        pass

    @property
    @abstractmethod
    def default_ttl(self) -> Optional[timedelta]:
        """Default time-to-live for items"""
        pass

    @abstractmethod
    async def store(self, item: MemoryItem) -> None:
        """Store an item"""
        pass

    @abstractmethod
    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve an item by ID"""
        pass

    @abstractmethod
    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all items"""
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete an item"""
        pass

    @abstractmethod
    async def search(self, query: str) -> List[MemoryItem]:
        """Search for items by query"""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired items, return count removed"""
        pass


class WorkingMemory(MemoryTypeInterface):
    """Immediate, mutable working memory for current task"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.WORKING

    @property
    def max_size(self) -> int:
        return 50  # Keep recent items only

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return timedelta(minutes=30)  # Short TTL for working memory

    async def store(self, item: MemoryItem) -> None:
        """Store in working memory"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve from working memory"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all working memory items"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete from working memory"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search working memory"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup expired working memory items"""
        return 0


class ShortTermMemory(MemoryTypeInterface):
    """Recent memory for ongoing execution, slightly longer retention"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.SHORT_TERM

    @property
    def max_size(self) -> int:
        return 200  # More items than working memory

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return timedelta(hours=24)  # Day-long retention

    async def store(self, item: MemoryItem) -> None:
        """Store in short-term memory"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve from short-term memory"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all short-term items"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete from short-term memory"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search short-term memory"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup expired short-term items"""
        return 0


class EpisodicMemory(MemoryTypeInterface):
    """Experiences and events, linked to time/context"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.EPISODIC

    @property
    def max_size(self) -> int:
        return 10000  # Larger, permanent store

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return None  # Keep indefinitely

    async def store(self, item: MemoryItem) -> None:
        """Store experience/episode"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve episode"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all episodes"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete episode"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search episodes"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup (no-op for episodic)"""
        return 0


class SemanticMemory(MemoryTypeInterface):
    """Facts, concepts, semantic knowledge"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.SEMANTIC

    @property
    def max_size(self) -> int:
        return 100000  # Large knowledge base

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return None  # Keep indefinitely

    async def store(self, item: MemoryItem) -> None:
        """Store fact/concept"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve fact"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all facts"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete fact"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search semantic knowledge"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup (no-op for semantic)"""
        return 0


class ProceduralMemory(MemoryTypeInterface):
    """How-to knowledge, procedures, strategies"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.PROCEDURAL

    @property
    def max_size(self) -> int:
        return 5000  # Reasonable size for procedures

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return None  # Keep indefinitely

    async def store(self, item: MemoryItem) -> None:
        """Store procedure"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve procedure"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all procedures"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete procedure"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search procedures"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup (no-op for procedural)"""
        return 0


class ConversationMemory(MemoryTypeInterface):
    """Conversation history and context"""

    @property
    def memory_type(self) -> MemoryType:
        return MemoryType.CONVERSATION

    @property
    def max_size(self) -> int:
        return 1000  # Conversation turns

    @property
    def default_ttl(self) -> Optional[timedelta]:
        return timedelta(days=30)  # 30-day retention for conversations

    async def store(self, item: MemoryItem) -> None:
        """Store conversation turn"""
        pass

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve turn"""
        pass

    async def retrieve_all(self) -> List[MemoryItem]:
        """Retrieve all turns"""
        pass

    async def delete(self, item_id: str) -> bool:
        """Delete turn"""
        pass

    async def search(self, query: str) -> List[MemoryItem]:
        """Search conversation"""
        pass

    async def cleanup_expired(self) -> int:
        """Cleanup expired conversation"""
        return 0

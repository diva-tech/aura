"""Abstract memory store interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aura_backend.memory.knowledge.objects import (
    MemoryItem,
    Relationship,
    RelationshipType,
)


class MemoryStore(ABC):
    """Abstract interface for all memory storage implementations.

    No storage should be required - subclasses implement specific backends
    (SQLite, PostgreSQL, Redis, Qdrant, Milvus, Weaviate, Chroma, Filesystem, etc.)
    """

    @abstractmethod
    async def connect(self) -> None:
        """Connect to storage backend"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from storage backend"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Check store health and return status"""
        pass

    # Core operations

    @abstractmethod
    async def put(self, item: MemoryItem) -> str:
        """Store a memory item, return item ID"""
        pass

    @abstractmethod
    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID"""
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete a memory item, return success"""
        pass

    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        """Check if item exists"""
        pass

    # Batch operations

    @abstractmethod
    async def batch_put(self, items: List[MemoryItem]) -> List[str]:
        """Store multiple items, return list of IDs"""
        pass

    @abstractmethod
    async def batch_get(self, item_ids: List[str]) -> List[Optional[MemoryItem]]:
        """Retrieve multiple items, return list (with None for missing)"""
        pass

    @abstractmethod
    async def batch_delete(self, item_ids: List[str]) -> int:
        """Delete multiple items, return count deleted"""
        pass

    # Query operations

    @abstractmethod
    async def query(
        self,
        query_string: str,
        limit: int = 10,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Query by text search"""
        pass

    @abstractmethod
    async def query_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by metadata"""
        pass

    @abstractmethod
    async def query_by_importance(
        self,
        min_importance: float,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by importance threshold"""
        pass

    @abstractmethod
    async def query_by_recency(
        self,
        days: int,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query recent items"""
        pass

    @abstractmethod
    async def query_by_type(
        self,
        memory_type: str,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by memory type"""
        pass

    # Relationship operations

    @abstractmethod
    async def store_relationship(self, relationship: Relationship) -> str:
        """Store a relationship, return relationship ID"""
        pass

    @abstractmethod
    async def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
    ) -> List[Relationship]:
        """Get relationships with optional filtering"""
        pass

    @abstractmethod
    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship"""
        pass

    # Statistics

    @abstractmethod
    async def count(self) -> int:
        """Total item count"""
        pass

    @abstractmethod
    async def count_by_type(self, memory_type: str) -> int:
        """Count items of specific type"""
        pass

    @abstractmethod
    async def count_relationships(self) -> int:
        """Total relationship count"""
        pass

    # Expiration

    @abstractmethod
    async def expire_before(self, timestamp: float) -> int:
        """Delete items expired before timestamp, return count deleted"""
        pass

    # Archive

    @abstractmethod
    async def archive(self, item_id: str) -> bool:
        """Archive an item (soft delete)"""
        pass

    @abstractmethod
    async def restore(self, item_id: str) -> bool:
        """Restore an archived item"""
        pass

    # Cleanup

    @abstractmethod
    async def cleanup(self) -> Dict[str, int]:
        """Run maintenance cleanup, return stats"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all data (use with caution)"""
        pass


class MemoryStoreRegistry:
    """Registry for memory store implementations"""

    def __init__(self):
        self._stores: Dict[str, type] = {}

    def register(self, name: str, store_class: type) -> None:
        """Register a store implementation"""
        if not issubclass(store_class, MemoryStore):
            raise TypeError(f"{store_class} must extend MemoryStore")
        self._stores[name] = store_class

    def get(self, name: str) -> Optional[type]:
        """Get a registered store implementation"""
        return self._stores.get(name)

    def list(self) -> List[str]:
        """List all registered stores"""
        return list(self._stores.keys())

    def unregister(self, name: str) -> bool:
        """Unregister a store"""
        if name in self._stores:
            del self._stores[name]
            return True
        return False

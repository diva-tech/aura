"""Central Memory Manager - single entry point for all memory operations."""

import time
from typing import Any, Dict, List, Optional

from aura_backend.memory.knowledge.objects import (
    MemoryItem,
    MemoryType,
    Relationship,
    RelationshipType,
)
from aura_backend.memory.stores.store import MemoryStore, MemoryStoreRegistry
from aura_backend.memory.types import (
    ConversationMemory,
    EpisodicMemory,
    ProceduralMemory,
    SemanticMemory,
    ShortTermMemory,
    WorkingMemory,
)


class MemoryManager:
    """Universal memory runtime for all AURA agents.

    Single entry point for:
    - Storing memories (all types)
    - Retrieving memories (by type, query, metadata)
    - Updating memories
    - Deleting memories
    - Searching memories
    - Organizing relationships
    - Summarizing context
    - Archiving old memories
    - Expiring memories by TTL
    """

    def __init__(self, store: MemoryStore):
        """Initialize manager with a memory store backend"""
        self._backend = store

        # Memory type handlers
        self.working_memory = WorkingMemory()
        self.short_term_memory = ShortTermMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        self.conversation_memory = ConversationMemory()

        # Metrics
        self._store_count = 0
        self._retrieve_count = 0
        self._search_count = 0

    async def initialize(self) -> None:
        """Initialize the memory manager"""
        await self._backend.connect()

    async def shutdown(self) -> None:
        """Shutdown the memory manager"""
        await self._backend.disconnect()

    # Core storage operations

    async def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a memory item"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            summary=summary,
        )

        if metadata:
            for key, value in metadata.items():
                item.metadata.custom_fields[key] = value

        item_id = await self._backend.put(item)
        self._store_count += 1
        return item_id

    async def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID"""
        item = await self._backend.get(item_id)
        if item:
            self._retrieve_count += 1
        return item

    async def retrieve_all(self, memory_type: Optional[MemoryType] = None) -> List[MemoryItem]:
        """Retrieve all memories, optionally filtered by type"""
        if memory_type:
            return await self._backend.query_by_type(memory_type.value)
        return []  # Would retrieve all from store

    async def update(
        self,
        item_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update a memory item"""
        item = await self._backend.get(item_id)
        if not item:
            return False

        if content:
            item.content = content

        if metadata:
            for key, value in metadata.items():
                item.metadata.custom_fields[key] = value

        await self._backend.put(item)
        return True

    async def delete(self, item_id: str) -> bool:
        """Delete a memory item"""
        return await self._backend.delete(item_id)

    # Search operations

    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search memories by text query"""
        self._search_count += 1
        return await self._backend.query(query, limit=limit)

    async def search_by_importance(self, min_importance: float = 0.5, limit: int = 10) -> List[MemoryItem]:
        """Search by importance threshold"""
        return await self._backend.query_by_importance(min_importance, limit=limit)

    async def search_by_recency(self, days: int = 7, limit: int = 10) -> List[MemoryItem]:
        """Search recent memories"""
        return await self._backend.query_by_recency(days, limit=limit)

    async def search_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[MemoryItem]:
        """Search by memory type"""
        return await self._backend.query_by_type(memory_type.value, limit=limit)

    async def search_by_metadata(
        self, filters: Dict[str, Any], limit: int = 10
    ) -> List[MemoryItem]:
        """Search by metadata filters"""
        return await self._backend.query_by_metadata(filters, limit=limit)

    # Relationship operations

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float = 1.0,
    ) -> str:
        """Add a typed relationship between memories"""
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
        )
        return await self._backend.store_relationship(relationship)

    async def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
    ) -> List[Relationship]:
        """Get relationships with optional filtering"""
        return await self._backend.get_relationships(source_id, target_id, relationship_type)

    # Lifecycle operations

    async def summarize(self, item_ids: List[str]) -> Optional[str]:
        """Summarize multiple memories (stub)"""
        # Future: integrate with LLM Runtime for actual summarization
        items = await self._backend.batch_get(item_ids)
        if not items:
            return None
        return f"Summary of {len(items)} memories"

    async def archive(self, item_id: str) -> bool:
        """Archive a memory (soft delete)"""
        return await self._backend.archive(item_id)

    async def restore(self, item_id: str) -> bool:
        """Restore an archived memory"""
        return await self._backend.restore(item_id)

    async def expire(self, max_age_seconds: int) -> int:
        """Expire memories older than max_age_seconds"""
        current_timestamp = time.time()
        expiration_threshold = current_timestamp - max_age_seconds
        return await self._backend.expire_before(expiration_threshold)

    # Statistics

    async def count(self) -> int:
        """Total memory count"""
        return await self._backend.count()

    async def count_by_type(self, memory_type: MemoryType) -> int:
        """Count memories by type"""
        return await self._backend.count_by_type(memory_type.value)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get memory manager metrics"""
        total = await self._backend.count()
        return {
            "total_items": total,
            "store_operations": self._store_count,
            "retrieve_operations": self._retrieve_count,
            "search_operations": self._search_count,
            "relationships": await self._backend.count_relationships(),
        }

    async def health(self) -> Dict[str, Any]:
        """Check system health"""
        store_health = await self._backend.health()
        return {
            "status": "healthy" if store_health.get("status") == "healthy" else "unhealthy",
            "store": store_health,
            "memory_count": await self._backend.count(),
        }

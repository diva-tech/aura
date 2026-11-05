"""In-memory reference implementation of MemoryStore.

This is a reference implementation to validate the MemoryStore abstraction.
It is suitable for testing and local development, but NOT recommended for production.

Thread-safe, async-first, in-memory storage with support for:
- Basic CRUD operations
- Batch operations
- Text and metadata queries
- Relationships with typed graph support
- Archiving (soft delete)
- TTL-based expiration
- Full relationship traversal
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from aura_backend.memory.knowledge.objects import MemoryItem, Relationship, RelationshipType
from aura_backend.memory.stores.store import MemoryStore


class InMemoryStore(MemoryStore):
    """In-memory reference implementation of MemoryStore.

    Provides thread-safe, async-first storage for memory items and relationships.
    Designed to validate the MemoryStore abstraction.

    Not recommended for production. Use PostgreSQL, SQLite, or other production
    backends for actual deployments.
    """

    def __init__(self):
        """Initialize the in-memory store."""
        self._items: Dict[str, MemoryItem] = {}
        self._archived: Dict[str, MemoryItem] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._lock = asyncio.Lock()
        self._connected = False

    async def connect(self) -> None:
        """Connect to storage backend (no-op for in-memory)."""
        async with self._lock:
            self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from storage backend (no-op for in-memory)."""
        async with self._lock:
            self._connected = False

    async def health(self) -> Dict[str, Any]:
        """Check store health and return status."""
        async with self._lock:
            return {
                "status": "healthy" if self._connected else "disconnected",
                "items": len(self._items),
                "archived": len(self._archived),
                "relationships": len(self._relationships),
                "store_type": "in_memory",
            }

    # Core operations

    async def put(self, item: MemoryItem) -> str:
        """Store a memory item, return item ID."""
        async with self._lock:
            if not item.id:
                item.id = str(uuid4())
            self._items[item.id] = item
            return item.id

    async def get(self, item_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by ID."""
        async with self._lock:
            return self._items.get(item_id)

    async def delete(self, item_id: str) -> bool:
        """Delete a memory item, return success."""
        async with self._lock:
            if item_id in self._items:
                del self._items[item_id]
                # Also delete related relationships
                rels_to_delete = [
                    rel_id
                    for rel_id, rel in self._relationships.items()
                    if rel.source_id == item_id or rel.target_id == item_id
                ]
                for rel_id in rels_to_delete:
                    del self._relationships[rel_id]
                return True
            return False

    async def exists(self, item_id: str) -> bool:
        """Check if item exists."""
        async with self._lock:
            return item_id in self._items

    # Batch operations

    async def batch_put(self, items: List[MemoryItem]) -> List[str]:
        """Store multiple items, return list of IDs."""
        ids = []
        for item in items:
            item_id = await self.put(item)
            ids.append(item_id)
        return ids

    async def batch_get(self, item_ids: List[str]) -> List[Optional[MemoryItem]]:
        """Retrieve multiple items, return list (with None for missing)."""
        async with self._lock:
            return [self._items.get(item_id) for item_id in item_ids]

    async def batch_delete(self, item_ids: List[str]) -> int:
        """Delete multiple items, return count deleted."""
        count = 0
        for item_id in item_ids:
            if await self.delete(item_id):
                count += 1
        return count

    # Query operations

    async def query(
        self,
        query_string: str,
        limit: int = 10,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Query by text search (simple substring matching)."""
        async with self._lock:
            query_lower = query_string.lower()
            matches = [
                item
                for item in self._items.values()
                if query_lower in item.content.lower()
                or (item.summary and query_lower in item.summary.lower())
            ]
            matches.sort(
                key=lambda x: x.metadata.created_at, reverse=True
            )
            return matches[offset : offset + limit]

    async def query_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by metadata filters."""
        async with self._lock:
            matches = []
            for item in self._items.values():
                if self._matches_metadata_filters(item, metadata_filters):
                    matches.append(item)
            matches.sort(
                key=lambda x: x.metadata.created_at, reverse=True
            )
            return matches[:limit]

    async def query_by_importance(
        self,
        min_importance: float,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by importance threshold."""
        async with self._lock:
            matches = [
                item
                for item in self._items.values()
                if item.metadata.importance >= min_importance
            ]
            matches.sort(
                key=lambda x: x.metadata.importance, reverse=True
            )
            return matches[:limit]

    async def query_by_recency(
        self,
        days: int,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query recent items (created within last N days)."""
        async with self._lock:
            cutoff = datetime.utcnow() - timedelta(days=days)
            matches = [
                item
                for item in self._items.values()
                if item.metadata.created_at >= cutoff
            ]
            matches.sort(
                key=lambda x: x.metadata.created_at, reverse=True
            )
            return matches[:limit]

    async def query_by_type(
        self,
        memory_type: str,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """Query by memory type."""
        async with self._lock:
            matches = [
                item
                for item in self._items.values()
                if item.memory_type.value == memory_type
            ]
            matches.sort(
                key=lambda x: x.metadata.created_at, reverse=True
            )
            return matches[:limit]

    # Relationship operations

    async def store_relationship(self, relationship: Relationship) -> str:
        """Store a relationship, return relationship ID."""
        async with self._lock:
            if not relationship.id:
                relationship.id = str(uuid4())
            self._relationships[relationship.id] = relationship
            return relationship.id

    async def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
    ) -> List[Relationship]:
        """Get relationships with optional filtering."""
        async with self._lock:
            matches = []
            for rel in self._relationships.values():
                if source_id and rel.source_id != source_id:
                    continue
                if target_id and rel.target_id != target_id:
                    continue
                if relationship_type and rel.relationship_type != relationship_type:
                    continue
                matches.append(rel)
            return matches

    async def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        async with self._lock:
            if relationship_id in self._relationships:
                del self._relationships[relationship_id]
                return True
            return False

    # Statistics

    async def count(self) -> int:
        """Total item count."""
        async with self._lock:
            return len(self._items)

    async def count_by_type(self, memory_type: str) -> int:
        """Count items of specific type."""
        async with self._lock:
            return sum(
                1
                for item in self._items.values()
                if item.memory_type.value == memory_type
            )

    async def count_relationships(self) -> int:
        """Total relationship count."""
        async with self._lock:
            return len(self._relationships)

    # Expiration

    async def expire_before(self, timestamp: float) -> int:
        """Delete items expired before timestamp, return count deleted."""
        async with self._lock:
            cutoff = datetime.fromtimestamp(timestamp)
            expired_ids = [
                item_id
                for item_id, item in self._items.items()
                if item.metadata.created_at < cutoff
            ]
            for item_id in expired_ids:
                del self._items[item_id]
                # Also delete related relationships
                rels_to_delete = [
                    rel_id
                    for rel_id, rel in self._relationships.items()
                    if rel.source_id == item_id or rel.target_id == item_id
                ]
                for rel_id in rels_to_delete:
                    del self._relationships[rel_id]
            return len(expired_ids)

    # Archive

    async def archive(self, item_id: str) -> bool:
        """Archive an item (soft delete)."""
        async with self._lock:
            if item_id in self._items:
                item = self._items.pop(item_id)
                self._archived[item_id] = item
                return True
            return False

    async def restore(self, item_id: str) -> bool:
        """Restore an archived item."""
        async with self._lock:
            if item_id in self._archived:
                item = self._archived.pop(item_id)
                self._items[item_id] = item
                return True
            return False

    # Cleanup

    async def cleanup(self) -> Dict[str, int]:
        """Run maintenance cleanup, return stats."""
        async with self._lock:
            # For in-memory store, cleanup just reports stats
            return {
                "active_items": len(self._items),
                "archived_items": len(self._archived),
                "relationships": len(self._relationships),
            }

    async def clear(self) -> None:
        """Clear all data (use with caution)."""
        async with self._lock:
            self._items.clear()
            self._archived.clear()
            self._relationships.clear()

    # Helper methods

    def _matches_metadata_filters(
        self,
        item: MemoryItem,
        filters: Dict[str, Any],
    ) -> bool:
        """Check if item matches all metadata filters."""
        for key, value in filters.items():
            if key == "importance" and item.metadata.importance != value:
                return False
            elif key == "confidence" and item.metadata.confidence != value:
                return False
            elif key == "tags" and not set(value).intersection(item.metadata.tags):
                return False
            elif key == "created_by" and item.metadata.created_by != value:
                return False
            elif key == "source" and item.metadata.source != value:
                return False
        return True

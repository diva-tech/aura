"""Events published by the Memory Platform."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class MemoryEvent:
    """Base event for memory platform"""
    event_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class MemoryCreatedEvent(MemoryEvent):
    """Memory item created"""
    item_id: str
    memory_type: str
    content_length: int


@dataclass
class MemoryUpdatedEvent(MemoryEvent):
    """Memory item updated"""
    item_id: str
    fields_updated: list


@dataclass
class MemoryDeletedEvent(MemoryEvent):
    """Memory item deleted"""
    item_id: str
    memory_type: str


@dataclass
class MemoryRetrievedEvent(MemoryEvent):
    """Memory item retrieved"""
    item_id: str
    retrieval_method: str
    latency_ms: float


@dataclass
class KnowledgeStoredEvent(MemoryEvent):
    """Knowledge stored"""
    knowledge_type: str
    item_count: int


@dataclass
class KnowledgeArchivedEvent(MemoryEvent):
    """Knowledge archived"""
    item_ids: list
    archive_count: int


@dataclass
class ContextBuiltEvent(MemoryEvent):
    """Context built for LLM"""
    context_tokens: int
    compression_ratio: float
    items_included: int


@dataclass
class CompressionCompletedEvent(MemoryEvent):
    """Compression completed"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_method: str


@dataclass
class PolicyViolationEvent(MemoryEvent):
    """Policy violation detected"""
    policy_name: str
    violation_type: str
    details: Dict[str, Any]


@dataclass
class RelationshipCreatedEvent(MemoryEvent):
    """Relationship created"""
    source_id: str
    target_id: str
    relationship_type: str
    strength: float


@dataclass
class MemoryExpirationEvent(MemoryEvent):
    """Memory expiration triggered"""
    items_expired: int
    freed_space_mb: Optional[float]

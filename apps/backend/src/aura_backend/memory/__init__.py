"""AURA Memory & Knowledge Platform.

Universal memory runtime for all agents.

Provides:
- Memory Manager (central API)
- Memory types (working, short-term, episodic, semantic, procedural, conversation)
- Knowledge objects (items, documents, observations, facts, experiences)
- Memory store abstraction (provider-agnostic storage)
- Store plugins (SQLite, PostgreSQL, Redis, Qdrant, Milvus, Weaviate, Chroma, Filesystem)
- Relationships and knowledge graphs
- Context building
- Compression strategies
- Memory and execution policies
- Events and metrics
"""

from aura_backend.memory.compression.strategies import (
    ContextBuilder,
    WindowingStrategy,
)
from aura_backend.memory.events import (
    CompressionCompletedEvent,
    ContextBuiltEvent,
    KnowledgeArchivedEvent,
    KnowledgeStoredEvent,
    MemoryCreatedEvent,
    MemoryDeletedEvent,
    MemoryEvent,
    MemoryExpirationEvent,
    MemoryRetrievedEvent,
    MemoryUpdatedEvent,
    PolicyViolationEvent,
    RelationshipCreatedEvent,
)
from aura_backend.memory.knowledge import (
    ConversationTurn,
    Experience,
    Fact,
    KnowledgeDocument,
    MemoryItem,
    MemoryType,
    Metadata,
    Observation,
    Relationship,
    RelationshipType,
    Summary,
)
from aura_backend.memory.manager import MemoryManager
from aura_backend.memory.policies import ExecutionPolicy, MemoryPolicy
from aura_backend.memory.stores import InMemoryStore, MemoryStore, MemoryStoreRegistry
from aura_backend.memory.types import (
    ConversationMemory,
    EpisodicMemory,
    MemoryTypeInterface,
    ProceduralMemory,
    SemanticMemory,
    ShortTermMemory,
    WorkingMemory,
)

__all__ = [
    # Manager
    "MemoryManager",
    # Memory types
    "MemoryTypeInterface",
    "WorkingMemory",
    "ShortTermMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",
    "ConversationMemory",
    # Knowledge objects
    "MemoryType",
    "RelationshipType",
    "Metadata",
    "MemoryItem",
    "KnowledgeDocument",
    "Observation",
    "Fact",
    "Experience",
    "ConversationTurn",
    "Summary",
    "Relationship",
    # Stores
    "MemoryStore",
    "MemoryStoreRegistry",
    "InMemoryStore",
    # Policies
    "MemoryPolicy",
    "ExecutionPolicy",
    # Compression/Context
    "ContextBuilder",
    "WindowingStrategy",
    # Events
    "MemoryEvent",
    "MemoryCreatedEvent",
    "MemoryUpdatedEvent",
    "MemoryDeletedEvent",
    "MemoryRetrievedEvent",
    "KnowledgeStoredEvent",
    "KnowledgeArchivedEvent",
    "ContextBuiltEvent",
    "CompressionCompletedEvent",
    "PolicyViolationEvent",
    "RelationshipCreatedEvent",
    "MemoryExpirationEvent",
]

"""Core knowledge objects for the Memory & Knowledge Platform."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4


class MemoryType(str, Enum):
    """Memory type classification"""
    WORKING = "working"
    SHORT_TERM = "short_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CONVERSATION = "conversation"


class RelationshipType(str, Enum):
    """Typed relationships between knowledge objects"""
    DERIVED_FROM = "derived_from"
    CREATED_DURING = "created_during"
    RELATED_TO = "related_to"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    PART_OF = "part_of"
    CAUSES = "causes"
    CONSEQUENCE_OF = "consequence_of"
    SIMILAR_TO = "similar_to"
    GENERALIZES = "generalizes"
    SPECIALIZES = "specializes"


@dataclass
class Metadata:
    """Universal metadata for knowledge objects"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    source: Optional[str] = None
    importance: float = 0.5  # 0-1 scale
    confidence: float = 0.8  # 0-1 scale
    tags: Set[str] = field(default_factory=set)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "source": self.source,
            "importance": self.importance,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "custom_fields": self.custom_fields,
        }


@dataclass
class EmbeddingReference:
    """Reference to an embedding (not the embedding itself)"""
    model: str
    dimension: int
    provider: str
    embedding_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryItem:
    """Base memory object stored in the system"""
    id: str = field(default_factory=lambda: str(uuid4()))
    memory_type: MemoryType = MemoryType.WORKING
    content: str = ""
    summary: Optional[str] = None
    metadata: Metadata = field(default_factory=Metadata)
    embedding_ref: Optional[EmbeddingReference] = None
    relationships: List['Relationship'] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "summary": self.summary,
            "metadata": self.metadata.to_dict(),
            "embedding_ref": {
                "model": self.embedding_ref.model,
                "dimension": self.embedding_ref.dimension,
                "provider": self.embedding_ref.provider,
            } if self.embedding_ref else None,
            "relationship_count": len(self.relationships),
        }


@dataclass
class KnowledgeDocument:
    """Structured knowledge document"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: str = ""
    document_type: str = "general"
    sections: List[Dict[str, str]] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)
    embedding_ref: Optional[EmbeddingReference] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "document_type": self.document_type,
            "section_count": len(self.sections),
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class Observation:
    """Observation of the world/system during execution"""
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    observation_type: str = "general"
    goal_id: Optional[str] = None
    agent_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.observation_type,
            "goal_id": self.goal_id,
            "agent_id": self.agent_id,
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class Fact:
    """Factual knowledge extracted or learned"""
    id: str = field(default_factory=lambda: str(uuid4()))
    statement: str = ""
    fact_type: str = "general"
    evidence: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "type": self.fact_type,
            "evidence_count": len(self.evidence),
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class Experience:
    """Recorded experience from execution"""
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    goal_id: Optional[str] = None
    agent_id: Optional[str] = None
    steps_taken: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    lessons: List[str] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "agent_id": self.agent_id,
            "steps_count": len(self.steps_taken),
            "lessons_count": len(self.lessons),
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class ConversationTurn:
    """Single turn in a conversation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    conversation_id: str = ""
    role: str = "user"  # "user", "assistant", "system"
    content: str = ""
    turn_number: int = 0
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "turn_number": self.turn_number,
            "content_length": len(self.content),
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class Summary:
    """Summarized knowledge or context"""
    id: str = field(default_factory=lambda: str(uuid4()))
    summary_type: str = "general"
    summary_text: str = ""
    original_items: List[str] = field(default_factory=list)  # IDs of summarized items
    compression_ratio: float = 1.0  # original_tokens / summary_tokens
    compression_method: str = "abstractive"
    metadata: Metadata = field(default_factory=Metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.summary_type,
            "original_items_count": len(self.original_items),
            "compression_ratio": self.compression_ratio,
            "compression_method": self.compression_method,
            "metadata": self.metadata.to_dict(),
        }


@dataclass
class Relationship:
    """Typed relationship between knowledge objects"""
    id: str = field(default_factory=lambda: str(uuid4()))
    source_id: str = ""
    target_id: str = ""
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    strength: float = 1.0  # 0-1 scale
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "strength": self.strength,
            "created_at": self.created_at.isoformat(),
        }

"""Memory store plugin definitions.

These are interface stubs for future implementations.
Each plugin will implement the MemoryStore interface for a specific backend.
"""

from abc import ABC
from typing import Optional

from aura_backend.memory.stores.store import MemoryStore


class SQLiteMemoryStore(MemoryStore, ABC):
    """SQLite-based memory store implementation (STUB).

    Future implementation will use SQLite for local development.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path


class PostgreSQLMemoryStore(MemoryStore, ABC):
    """PostgreSQL-based memory store implementation (STUB).

    Future implementation will use PostgreSQL for production deployments.
    Supports full-text search, JSON operators, and relationships.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "aura_memory",
        user: str = "postgres",
        password: str = "",
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password


class RedisMemoryStore(MemoryStore, ABC):
    """Redis-based memory store implementation (STUB).

    Future implementation will use Redis for high-speed access.
    Ideal for working/short-term memory with TTL support.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password


class QdrantMemoryStore(MemoryStore, ABC):
    """Qdrant-based vector memory store (STUB).

    Future implementation will use Qdrant for semantic search.
    Designed for similarity-based retrieval with vector embeddings.
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        collection_name: str = "aura_memory",
    ):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name


class MilvusMemoryStore(MemoryStore, ABC):
    """Milvus-based vector memory store (STUB).

    Future implementation will use Milvus for large-scale vector search.
    Supports distributed deployments.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        collection_name: str = "aura_memory",
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name


class WeaviateMemoryStore(MemoryStore, ABC):
    """Weaviate-based memory store (STUB).

    Future implementation will use Weaviate for semantic search with knowledge graphs.
    Native support for relationships and semantic queries.
    """

    def __init__(
        self,
        url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        class_name: str = "AuraMemory",
    ):
        self.url = url
        self.api_key = api_key
        self.class_name = class_name


class ChromaMemoryStore(MemoryStore, ABC):
    """Chroma-based vector memory store (STUB).

    Future implementation will use Chroma for lightweight vector search.
    Good for development and local deployments.
    """

    def __init__(
        self,
        persist_directory: str = ".chroma",
        collection_name: str = "aura_memory",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name


class FilesystemMemoryStore(MemoryStore, ABC):
    """Filesystem-based memory store (STUB).

    Future implementation will use local filesystem with JSON/JSONL files.
    Useful for testing and local development.
    """

    def __init__(
        self,
        root_path: str = "./memory_store",
        format: str = "json",  # 'json' or 'jsonl'
    ):
        self.root_path = root_path
        self.format = format

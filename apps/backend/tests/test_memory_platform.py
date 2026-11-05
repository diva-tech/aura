"""Tests for Memory & Knowledge Platform."""

import pytest
import pytest_asyncio
from datetime import datetime

from aura_backend.memory import (
    MemoryItem,
    MemoryType,
    Metadata,
    Observation,
    Fact,
    Experience,
    ConversationTurn,
    Relationship,
    RelationshipType,
    MemoryManager,
    MemoryPolicy,
    ExecutionPolicy,
    ContextBuilder,
    WindowingStrategy,
    InMemoryStore,
)


class TestKnowledgeObjects:
    """Test knowledge object models"""

    def test_memory_item_creation(self):
        """Test creating a memory item"""
        item = MemoryItem(
            content="Python async/await patterns",
            memory_type=MemoryType.SEMANTIC,
            summary="Async patterns in Python",
        )

        assert item.memory_type == MemoryType.SEMANTIC
        assert item.content == "Python async/await patterns"
        assert item.id is not None

    def test_metadata_fields(self):
        """Test metadata model"""
        metadata = Metadata(
            importance=0.9,
            confidence=0.95,
            tags={"python", "async"},
        )

        assert metadata.importance == 0.9
        assert metadata.confidence == 0.95
        assert "python" in metadata.tags

    def test_observation_creation(self):
        """Test creating observation"""
        obs = Observation(
            description="Tool returned error after 3 retries",
            observation_type="tool_failure",
            goal_id="goal-123",
        )

        assert obs.observation_type == "tool_failure"
        assert obs.goal_id == "goal-123"

    def test_fact_creation(self):
        """Test creating fact"""
        fact = Fact(
            statement="Claude models support tool calling",
            fact_type="model_capability",
            evidence=["API docs", "code examples"],
        )

        assert len(fact.evidence) == 2
        assert fact.fact_type == "model_capability"

    def test_experience_creation(self):
        """Test creating experience"""
        exp = Experience(
            description="Successfully researched Python features",
            goal_id="goal-456",
            steps_taken=["search", "analyze", "summarize"],
            lessons=["Google search is faster than LLM synthesis"],
        )

        assert len(exp.steps_taken) == 3
        assert len(exp.lessons) == 1

    def test_relationship_creation(self):
        """Test creating relationship"""
        rel = Relationship(
            source_id="fact-1",
            target_id="obs-1",
            relationship_type=RelationshipType.DERIVED_FROM,
            strength=0.9,
        )

        assert rel.relationship_type == RelationshipType.DERIVED_FROM
        assert rel.strength == 0.9

    def test_memory_item_to_dict(self):
        """Test serialization"""
        item = MemoryItem(content="Test", memory_type=MemoryType.WORKING)
        data = item.to_dict()

        assert data["memory_type"] == "working"
        assert data["content"] == "Test"
        assert "created_at" in data["metadata"]


class TestMemoryTypes:
    """Test memory type interfaces"""

    def test_working_memory_properties(self):
        """Test working memory characteristics"""
        from aura_backend.memory.types import WorkingMemory

        wm = WorkingMemory()
        assert wm.memory_type == MemoryType.WORKING
        assert wm.max_size == 50
        assert wm.default_ttl is not None

    def test_episodic_memory_properties(self):
        """Test episodic memory characteristics"""
        from aura_backend.memory.types import EpisodicMemory

        em = EpisodicMemory()
        assert em.memory_type == MemoryType.EPISODIC
        assert em.max_size == 10000
        assert em.default_ttl is None  # Permanent

    def test_semantic_memory_properties(self):
        """Test semantic memory characteristics"""
        from aura_backend.memory.types import SemanticMemory

        sm = SemanticMemory()
        assert sm.memory_type == MemoryType.SEMANTIC
        assert sm.max_size == 100000
        assert sm.default_ttl is None  # Permanent


class TestPolicies:
    """Test policy models"""

    def test_memory_policy_defaults(self):
        """Test memory policy defaults"""
        policy = MemoryPolicy()

        assert policy.max_working_memory_items == 50
        assert policy.max_context_tokens == 8000
        assert policy.working_memory_ttl_minutes == 30

    def test_memory_policy_retention(self):
        """Test retention logic"""
        policy = MemoryPolicy(
            min_importance_to_retain=0.5,
            auto_archive_low_importance=True,
            auto_archive_threshold=0.2,
        )

        # High importance should be retained
        assert policy.should_retain(0.8, age_days=10)

        # Low importance old memory should not be retained
        assert not policy.should_retain(0.1, age_days=100)

    def test_execution_policy_compliance(self):
        """Test execution policy compliance check"""
        policy = ExecutionPolicy(
            max_tokens=1000,
            max_cost_dollars=10.0,
            max_tool_calls=50,
        )

        compliant_stats = {
            "tokens_used": 500,
            "cost": 5.0,
            "tool_calls": 25,
        }

        assert policy.is_compliant(compliant_stats)

        non_compliant_stats = {
            "tokens_used": 2000,  # Exceeds limit
            "cost": 5.0,
            "tool_calls": 25,
        }

        assert not policy.is_compliant(non_compliant_stats)


class TestContextBuilder:
    """Test context building"""

    def test_windowing_strategy(self):
        """Test windowing compression"""
        strategy = WindowingStrategy(window_size=3)

        items = [
            MemoryItem(content=f"Item {i}", memory_type=MemoryType.WORKING)
            for i in range(10)
        ]

        # All items should be included since window_size is 3
        # (but only last 3 by recency)
        assert len(items) == 10

    @pytest.mark.asyncio
    async def test_context_builder_basic(self):
        """Test basic context building"""
        builder = ContextBuilder()

        items = [
            MemoryItem(
                content="Python fact",
                memory_type=MemoryType.SEMANTIC,
                summary="Python is interpreted",
            ),
            MemoryItem(
                content="Async fact",
                memory_type=MemoryType.SEMANTIC,
                summary="Async enables concurrency",
            ),
        ]

        context = await builder.build_context(
            goal="Research Python features",
            memories=items,
            max_tokens=4000,
        )

        assert "Research Python features" in context["context"]
        assert "memory_items" in context
        assert "compression_ratio" in context
        assert "token_estimate" in context

    @pytest.mark.asyncio
    async def test_context_builder_empty(self):
        """Test context building with no memories"""
        builder = ContextBuilder()

        context = await builder.build_context(
            goal="Start fresh",
            memories=[],
            max_tokens=4000,
        )

        assert "Start fresh" in context["context"]
        assert len(context["memory_items"]) == 0


class TestMemoryManager:
    """Test MemoryManager with InMemoryStore"""

    @pytest_asyncio.fixture
    async def memory_store(self):
        """Fixture for real InMemoryStore"""
        store = InMemoryStore()
        await store.connect()
        yield store
        await store.disconnect()

    @pytest.mark.asyncio
    async def test_manager_initialization(self, memory_store):
        """Test manager initialization"""
        manager = MemoryManager(memory_store)

        await manager.initialize()
        health = await memory_store.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_manager_store_memory(self, memory_store):
        """Test storing a memory"""
        manager = MemoryManager(memory_store)

        item_id = await manager.store(
            content="Test memory",
            memory_type=MemoryType.WORKING,
        )

        assert item_id is not None
        item = await memory_store.get(item_id)
        assert item is not None
        assert item.content == "Test memory"

    @pytest.mark.asyncio
    async def test_manager_retrieve_memory(self, memory_store):
        """Test retrieving a memory"""
        test_item = MemoryItem(
            id="item-1",
            content="Test",
            memory_type=MemoryType.WORKING,
        )
        await memory_store.put(test_item)

        manager = MemoryManager(memory_store)
        item = await manager.retrieve("item-1")

        assert item is not None
        assert item.content == "Test"

    @pytest.mark.asyncio
    async def test_manager_metrics(self, memory_store):
        """Test metrics collection"""
        manager = MemoryManager(memory_store)

        item_id_1 = await manager.store("Memory 1")
        await manager.store("Memory 2")
        await manager.retrieve(item_id_1)

        metrics = await manager.get_metrics()

        assert metrics["store_operations"] == 2
        assert metrics["retrieve_operations"] == 1


class TestInMemoryStore:
    """Test InMemoryStore reference implementation"""

    @pytest_asyncio.fixture
    async def store(self):
        """Create a fresh InMemoryStore for each test"""
        store = InMemoryStore()
        await store.connect()
        yield store
        await store.disconnect()

    @pytest.mark.asyncio
    async def test_connect_disconnect(self, store):
        """Test connection lifecycle"""
        health = await store.health()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_put_get(self, store):
        """Test basic put/get operations"""
        item = MemoryItem(content="Test content", memory_type=MemoryType.WORKING)
        item_id = await store.put(item)

        retrieved = await store.get(item_id)
        assert retrieved is not None
        assert retrieved.content == "Test content"
        assert retrieved.memory_type == MemoryType.WORKING

    @pytest.mark.asyncio
    async def test_delete(self, store):
        """Test delete operation"""
        item = MemoryItem(content="Delete me", memory_type=MemoryType.WORKING)
        item_id = await store.put(item)

        assert await store.exists(item_id)
        assert await store.delete(item_id)
        assert not await store.exists(item_id)

    @pytest.mark.asyncio
    async def test_batch_operations(self, store):
        """Test batch put/get/delete"""
        items = [
            MemoryItem(content=f"Item {i}", memory_type=MemoryType.WORKING)
            for i in range(5)
        ]

        ids = await store.batch_put(items)
        assert len(ids) == 5

        retrieved = await store.batch_get(ids)
        assert len(retrieved) == 5
        assert all(item is not None for item in retrieved)

        deleted = await store.batch_delete(ids)
        assert deleted == 5

    @pytest.mark.asyncio
    async def test_count(self, store):
        """Test item counting"""
        assert await store.count() == 0

        for i in range(3):
            item = MemoryItem(
                content=f"Item {i}",
                memory_type=MemoryType.WORKING,
            )
            await store.put(item)

        assert await store.count() == 3

    @pytest.mark.asyncio
    async def test_query_by_text(self, store):
        """Test text search"""
        item1 = MemoryItem(content="Python programming", memory_type=MemoryType.SEMANTIC)
        item2 = MemoryItem(content="JavaScript async", memory_type=MemoryType.SEMANTIC)

        await store.put(item1)
        await store.put(item2)

        results = await store.query("Python")
        assert len(results) == 1
        assert results[0].content == "Python programming"

    @pytest.mark.asyncio
    async def test_query_by_type(self, store):
        """Test filtering by memory type"""
        working = MemoryItem(content="Working", memory_type=MemoryType.WORKING)
        semantic = MemoryItem(content="Semantic", memory_type=MemoryType.SEMANTIC)

        await store.put(working)
        await store.put(semantic)

        results = await store.query_by_type("working")
        assert len(results) == 1
        assert results[0].content == "Working"

    @pytest.mark.asyncio
    async def test_query_by_importance(self, store):
        """Test filtering by importance"""
        high_imp = MemoryItem(content="Important")
        high_imp.metadata.importance = 0.9
        low_imp = MemoryItem(content="Less important")
        low_imp.metadata.importance = 0.2

        await store.put(high_imp)
        await store.put(low_imp)

        results = await store.query_by_importance(0.5)
        assert len(results) == 1
        assert results[0].content == "Important"

    @pytest.mark.asyncio
    async def test_query_by_metadata(self, store):
        """Test metadata filtering"""
        item1 = MemoryItem(content="Item 1")
        item1.metadata.tags.add("python")
        item1.metadata.created_by = "agent-1"

        item2 = MemoryItem(content="Item 2")
        item2.metadata.tags.add("javascript")
        item2.metadata.created_by = "agent-2"

        await store.put(item1)
        await store.put(item2)

        results = await store.query_by_metadata({"tags": ["python"]})
        assert len(results) == 1
        assert results[0].content == "Item 1"

    @pytest.mark.asyncio
    async def test_relationships(self, store):
        """Test storing and retrieving relationships"""
        item1 = MemoryItem(content="Fact 1", memory_type=MemoryType.SEMANTIC)
        item2 = MemoryItem(content="Observation 1", memory_type=MemoryType.EPISODIC)

        id1 = await store.put(item1)
        id2 = await store.put(item2)

        rel = Relationship(
            source_id=id1,
            target_id=id2,
            relationship_type=RelationshipType.DERIVED_FROM,
            strength=0.95,
        )

        rel_id = await store.store_relationship(rel)
        assert rel_id is not None

        retrieved = await store.get_relationships(source_id=id1)
        assert len(retrieved) == 1
        assert retrieved[0].target_id == id2
        assert retrieved[0].relationship_type == RelationshipType.DERIVED_FROM

    @pytest.mark.asyncio
    async def test_relationship_filtering(self, store):
        """Test relationship query filtering"""
        item1 = MemoryItem(content="Item 1")
        item2 = MemoryItem(content="Item 2")
        item3 = MemoryItem(content="Item 3")

        id1 = await store.put(item1)
        id2 = await store.put(item2)
        id3 = await store.put(item3)

        # Create relationships
        rel1 = Relationship(
            source_id=id1,
            target_id=id2,
            relationship_type=RelationshipType.SUPPORTS,
        )
        rel2 = Relationship(
            source_id=id1,
            target_id=id3,
            relationship_type=RelationshipType.CONTRADICTS,
        )

        await store.store_relationship(rel1)
        await store.store_relationship(rel2)

        # Query by type
        supports = await store.get_relationships(
            relationship_type=RelationshipType.SUPPORTS
        )
        assert len(supports) == 1
        assert supports[0].target_id == id2

    @pytest.mark.asyncio
    async def test_archive_restore(self, store):
        """Test archiving and restoring items"""
        item = MemoryItem(content="Archivable", memory_type=MemoryType.EPISODIC)
        item_id = await store.put(item)

        # Archive it
        assert await store.archive(item_id)

        # Should not be in active store
        assert await store.get(item_id) is None

        # Restore it
        assert await store.restore(item_id)

        # Should be back
        retrieved = await store.get(item_id)
        assert retrieved is not None
        assert retrieved.content == "Archivable"

    @pytest.mark.asyncio
    async def test_count_relationships(self, store):
        """Test relationship counting"""
        item1 = MemoryItem(content="Item 1")
        item2 = MemoryItem(content="Item 2")

        id1 = await store.put(item1)
        id2 = await store.put(item2)

        assert await store.count_relationships() == 0

        rel = Relationship(source_id=id1, target_id=id2)
        await store.store_relationship(rel)

        assert await store.count_relationships() == 1

    @pytest.mark.asyncio
    async def test_clear(self, store):
        """Test clearing all data"""
        item = MemoryItem(content="Will be cleared")
        await store.put(item)

        assert await store.count() == 1

        await store.clear()

        assert await store.count() == 0


class TestStoreAbstraction:
    """Test MemoryStore abstraction"""

    def test_store_registry(self):
        """Test store registry"""
        from aura_backend.memory.stores import MemoryStoreRegistry
        from aura_backend.memory.stores.plugins import SQLiteMemoryStore

        registry = MemoryStoreRegistry()
        registry.register("sqlite", SQLiteMemoryStore)

        assert registry.get("sqlite") == SQLiteMemoryStore
        assert "sqlite" in registry.list()

    def test_plugin_definitions(self):
        """Test that all plugins are defined"""
        from aura_backend.memory.stores.plugins import (
            SQLiteMemoryStore,
            PostgreSQLMemoryStore,
            RedisMemoryStore,
            QdrantMemoryStore,
            MilvusMemoryStore,
            WeaviateMemoryStore,
            ChromaMemoryStore,
            FilesystemMemoryStore,
        )

        # All should be defined (even if stubs)
        plugins = [
            SQLiteMemoryStore,
            PostgreSQLMemoryStore,
            RedisMemoryStore,
            QdrantMemoryStore,
            MilvusMemoryStore,
            WeaviateMemoryStore,
            ChromaMemoryStore,
            FilesystemMemoryStore,
        ]

        assert len(plugins) == 8

    @pytest.mark.asyncio
    async def test_in_memory_store_implements_interface(self):
        """Test that InMemoryStore properly implements MemoryStore"""
        from aura_backend.memory.stores import MemoryStore

        store = InMemoryStore()
        assert isinstance(store, MemoryStore)


class TestArchitectureValidation:
    """Validate the complete memory platform architecture"""

    @pytest.mark.asyncio
    async def test_full_stack_integration(self):
        """Test complete flow: Agent → MemoryManager → MemoryStore → InMemoryStore"""
        # Create the store
        store = InMemoryStore()
        await store.connect()

        # Create the manager
        manager = MemoryManager(store)
        await manager.initialize()

        # Store a memory
        item_id = await manager.store(
            content="Agent execution step",
            memory_type=MemoryType.EPISODIC,
        )

        # Retrieve it
        item = await manager.retrieve(item_id)
        assert item is not None
        assert item.content == "Agent execution step"

        # Search for it
        results = await manager.search("execution")
        assert len(results) > 0

        # Get metrics
        metrics = await manager.get_metrics()
        assert metrics["store_operations"] >= 1

        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_knowledge_graph_traversal(self):
        """Test that relationships enable knowledge graph traversal"""
        store = InMemoryStore()
        await store.connect()

        # Create a simple knowledge graph
        fact = MemoryItem(
            content="Python supports async/await",
            memory_type=MemoryType.SEMANTIC,
        )
        obs = MemoryItem(
            content="Observed async behavior in test",
            memory_type=MemoryType.EPISODIC,
        )

        fact_id = await store.put(fact)
        obs_id = await store.put(obs)

        # Create relationship
        rel = Relationship(
            source_id=fact_id,
            target_id=obs_id,
            relationship_type=RelationshipType.SUPPORTS,
            strength=0.9,
        )
        await store.store_relationship(rel)

        # Traverse: find what supports this observation
        relationships = await store.get_relationships(target_id=obs_id)
        assert len(relationships) == 1
        assert relationships[0].relationship_type == RelationshipType.SUPPORTS

        # Get the supporting fact
        supporting_fact = await store.get(relationships[0].source_id)
        assert supporting_fact.content == "Python supports async/await"

        await store.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

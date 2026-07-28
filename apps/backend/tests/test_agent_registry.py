"""
Tests for agent registry and lifecycle.
"""

from typing import Any, Dict

import pytest

from aura_backend.core.agents import (
    BaseAgent,
    AgentRegistry,
    AgentMetadata,
    AgentCapability,
    AgentRegistrationError,
)


class TestAgent(BaseAgent):
    """Test agent implementation"""

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "healthy"}

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            id=self.id,
            name="Test Agent",
            agent_type="test",
            version="0.1.0",
            description="A test agent",
            author="Test Author",
        )

    def get_capabilities(self) -> list[AgentCapability]:
        return [
            AgentCapability(
                name="test-capability",
                description="A test capability",
            )
        ]


@pytest.fixture
def registry():
    """Create an agent registry"""
    return AgentRegistry()


@pytest.mark.asyncio
async def test_registry_creation(registry):
    """Agent registry creates successfully"""
    assert registry is not None


@pytest.mark.asyncio
async def test_registry_register_class(registry):
    """Registry registers agent classes"""
    registry.register_class(TestAgent)
    agent = registry.create_agent(TestAgent)
    assert agent is not None
    assert isinstance(agent, TestAgent)


@pytest.mark.asyncio
async def test_registry_register_instance(registry):
    """Registry registers agent instances"""
    agent = TestAgent()
    registry.register_instance(agent)
    retrieved = registry.get(agent.id)
    assert retrieved is agent


@pytest.mark.asyncio
async def test_registry_list_agents(registry):
    """Registry lists agents"""
    agent = TestAgent()
    registry.register_instance(agent)
    agents = registry.list()
    assert len(agents) == 1


@pytest.mark.asyncio
async def test_registry_find_by_type(registry):
    """Registry finds agents by type"""
    agent = TestAgent()
    registry.register_instance(agent)
    found = registry.find_by_type("test")
    assert len(found) == 1
    assert found[0] is agent


@pytest.mark.asyncio
async def test_registry_initialize_agents(registry):
    """Registry initializes all agents"""
    agent = TestAgent()
    registry.register_instance(agent)
    await registry.initialize_all()
    assert agent.status == "ready"


@pytest.mark.asyncio
async def test_registry_shutdown_agents(registry):
    """Registry shuts down all agents"""
    agent = TestAgent()
    registry.register_instance(agent)
    await registry.initialize_all()
    await registry.shutdown_all()
    assert agent.status == "shut_down"


@pytest.mark.asyncio
async def test_registry_health(registry):
    """Registry reports health"""
    agent = TestAgent()
    registry.register_instance(agent)
    await registry.initialize_all()
    health = registry.health()
    assert health["total_agents"] == 1

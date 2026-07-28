# AURA AI Framework Documentation

## Overview

The AURA AI Framework is a **provider-agnostic, architecture-first framework** for building sophisticated AI agents. It defines the contracts and interfaces for agent execution without prescribing implementation details.

**Key Principle**: The framework is architecture without implementation. Every interface is defined; no business logic exists. This keeps the framework clean, extensible, and ready for integration with any AI provider (OpenAI, Anthropic, Gemini, Ollama, or future providers).

## Architecture

### Core Components

```
AI Framework
├── Goals
├── Planning
├── Memory
├── Execution
├── Tools
├── Providers
├── Prompts
├── Sessions
├── State Machine
└── Base Agent
```

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│            BaseAgent (Lifecycle)               │
│  init → plan → execute → observe → reflect     │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
   ┌────▼───┐  ┌───▼──┐  ┌───▼────┐
   │Planning│  │Tools │  │Memory  │
   └────┬───┘  └───┬──┘  └───┬────┘
        │          │         │
   ┌────▼──────────▼─────────▼────┐
   │   Execution Engine           │
   └────┬──────────────────────────┘
        │
   ┌────▼──────────────────────────┐
   │   Runtime Integration         │
   │   (Event Bus, Services)       │
   └───────────────────────────────┘
```

## Components

### Goals

**Purpose**: Represent high-level intent for agent execution.

**Key Types**:
- `Goal`: Immutable goal representation
- `GoalPriority`: CRITICAL, HIGH, NORMAL, LOW
- `GoalStatus`: PENDING, ACTIVE, COMPLETED, FAILED, CANCELLED
- `GoalResult`: Result of goal execution
- `GoalMetadata`: Tags, deadline, constraints

**Immutability**: All goal objects are immutable. Changes create new instances:

```python
goal = Goal(title="Write article")
updated_goal = goal.with_status(GoalStatus.ACTIVE)
# Original goal unchanged
```

### Agent Context

**Purpose**: Flow execution state through agent lifecycle.

**Carries**:
- Session and correlation IDs
- Current goal and step tracking
- Working memory
- Execution history
- Configuration and metadata
- Runtime references
- Cancellation token

**Example**:

```python
context = AgentContext(goal="research topic")
context.update_memory("research_findings", [...])
context.add_step(ExecutionStep(description="researched X"))
```

### State Machine

**Purpose**: Enforce valid agent state transitions.

**States**:
- IDLE → PLANNING → WAITING/EXECUTING → REFLECTING → COMPLETED
- ERROR transitions to FAILED
- Any state can transition to CANCELLED

**Usage**:

```python
sm = StateMachine()
sm.transition_to(AgentState.PLANNING)
# Raises StateTransitionError if invalid
```

### Planning

**Purpose**: Convert goals into executable plans.

**Interface Only** - No AI implementation included.

**Types**:
- `Planner`: Abstract interface for planning
- `Plan`: Collection of ordered steps
- `PlanStep`: Single step in plan
- `PlanResult`: Plan + feasibility

**Example**:

```python
result = await planner.plan(goal=my_goal, context=ctx)
# Result contains Plan, feasibility, confidence
```

### Memory

**Purpose**: Store and retrieve information at different timescales.

**Types**:
- `WorkingMemory`: Immediate task state (short-lived)
- `LongTermMemory`: Persistent knowledge (long-lived)
- `SemanticMemory`: Conceptual knowledge and relationships
- `EpisodicMemory`: Execution sessions and events
- `ConversationMemory`: Dialogue history
- `MemoryStore`: Unified memory interface

**Important**: These are interfaces only. No persistence, vector databases, or implementation included.

### Tools

**Purpose**: Universal framework for agent capabilities.

**Design**: Every future capability becomes a Tool.

**Tool Interface**:
- `id`: Unique identifier
- `get_name()`: Tool name
- `get_description()`: What it does
- `get_capabilities()`: List of capabilities
- `get_parameters()`: Required parameters
- `validate()`: Validate inputs
- `execute()`: Run the tool
- `health()`: Health status
- `timeout_seconds`: Execution timeout

**Built-in Placeholder Tools** (Milestone 3 only):
- `FilesystemTool`: File operations
- `PythonTool`: Python execution
- `VisionTool`: Image analysis
- `VideoTool`: Video processing
- `AudioTool`: Audio processing
- `BrowserTool`: Web browsing
- `ImageGenerationTool`: Image generation

**Tool Registry**:

```python
registry = ToolRegistry()
registry.register(my_tool)
registry.register(another_tool)

tool = registry.get("tool-id")
all_tools = registry.list()
```

### Providers

**Purpose**: Interfaces for AI/ML services.

**Provider Types** (Interfaces Only):
- `LLMProvider`: Language model completions
- `VisionProvider`: Image analysis
- `EmbeddingProvider`: Vector embeddings
- `SpeechProvider`: Speech-to-text, text-to-speech
- `ImageGenerationProvider`: Image generation
- `PromptRenderer`: Render prompt templates

**Key Design**: Completely provider-agnostic. Contracts only - no calls to OpenAI, Anthropic, Gemini, or any service.

### Execution Engine

**Purpose**: Framework for executing plans and tracking progress.

**Types**:
- `ExecutionContext`: Tracks phase and progress
- `ExecutionPipeline`: Executes plans
- `ExecutionPolicy`: Execution behavior rules
- `RetryPolicy`: Retry strategy for failures
- `ExecutionPhase`: PREPARING, RUNNING, MONITORING, COMPLETED
- `Progress`: Step completion tracking
- `Checkpoint`: Recovery points
- `ExecutionResult`: Final outcome

### Prompt System

**Purpose**: Manage prompts and support future versioning.

**Types**:
- `PromptTemplate`: Template with variables
- `PromptVariables`: Template variable values
- `PromptVersion`: Versioned prompt
- `PromptLibrary`: Library of templates

**Example**:

```python
template = PromptTemplate(
    id="research",
    template="Research {topic} and summarize",
    description="Research template"
)

lib.register_template(template)

variables = PromptVariables()
variables.set("topic", "quantum computing")
```

### Sessions

**Purpose**: Track individual agent execution sessions.

**Session Lifecycle**:
- CREATED → RUNNING → COMPLETED/FAILED/CANCELLED

**SessionManager**:

```python
mgr = SessionManager()
session = mgr.create_session(agent_id="a1", goal_id="g1")
session.start()
session.complete()

mgr.list_sessions(agent_id="a1")
mgr.count_sessions(status=SessionStatus.RUNNING)
```

### Base Agent

**Purpose**: Lifecycle management for all agents.

**Lifecycle Methods**:

```python
class MyAgent(BaseAgent):
    async def initialize(self):
        """Setup and resources"""
    
    async def plan(self, goal, context):
        """Create execution plan"""
    
    async def execute(self, plan, context):
        """Execute the plan"""
    
    async def observe(self, result, context):
        """Analyze results"""
    
    async def reflect(self, observations, context):
        """Learn from execution"""
    
    async def shutdown(self):
        """Cleanup"""
```

**Each method**:
- Publishes events to runtime
- Handles errors gracefully
- Tracks execution metrics
- Logs lifecycle transitions

## AI Framework Events

The framework extends the runtime EventBus with AI-specific events:

**Goal Events**: GoalCreated, GoalUpdated, GoalCompleted, GoalFailed, GoalCancelled

**Planning Events**: PlanningStarted, PlanningCompleted, PlanningFailed

**Execution Events**: ExecutionStarted, ExecutionCompleted, ExecutionFailed, ExecutionCancelled

**Step Events**: StepStarted, StepCompleted, StepFailed

**Tool Events**: ToolExecuted, ToolFailed

**Observation Events**: ObservationRecorded

**Reflection Events**: ReflectionStarted, ReflectionCompleted

**Memory Events**: MemoryUpdated, MemoryRetrieved

**Agent Events**: AgentStateChanged, AgentFailed, AgentRecovered

**Health Events**: FrameworkHealthChanged

## Extension Guide

### Creating a Custom Agent

```python
from aura_backend.ai import BaseAgent, AgentContext

class ResearchAgent(BaseAgent):
    async def _initialize_impl(self):
        # Load research tools
        pass

    async def _plan_impl(self, goal, context):
        # Create research plan
        return {
            "steps": [
                {"action": "search", "query": goal},
                {"action": "analyze", "sources": "..."},
                {"action": "summarize"},
            ]
        }

    async def _execute_impl(self, plan, context):
        # Execute each step
        results = []
        for step in plan["steps"]:
            result = await self.execute_step(step)
            results.append(result)
        return {"results": results, "success": True}
```

### Implementing a Custom Tool

```python
from aura_backend.ai import Tool, ToolCapability, ToolParameter, ToolResult

class ResearchTool(Tool):
    def get_name(self) -> str:
        return "Research"

    def get_description(self) -> str:
        return "Research on topics"

    def get_capabilities(self) -> list[ToolCapability]:
        return [
            ToolCapability("search", "Search for information"),
            ToolCapability("analyze", "Analyze research results"),
        ]

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter("query", "string", "Search query", required=True),
        ]

    async def validate(self, **kwargs) -> dict:
        if "query" not in kwargs:
            return {"valid": False, "error": "Missing query"}
        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query")
        # Research logic would go here
        return ToolResult(success=False, output=None, error="Not implemented")
```

### Implementing an LLM Provider

```python
from aura_backend.ai import LLMProvider, CompletionRequest, CompletionResponse

class MyLLMProvider(LLMProvider):
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        # Call your LLM service
        # (e.g., OpenAI, Anthropic, Gemini, etc.)
        pass

    async def stream_complete(self, request: CompletionRequest):
        # Stream completions
        pass

    async def list_models(self) -> list[str]:
        # Return available models
        pass
```

## Runtime Integration

The AI Framework integrates seamlessly with the AURA Runtime:

**Event Publishing**:
```python
context.event_publisher.publish(GoalCreated(goal_id=goal.id, goal_title=goal.title))
```

**Service Container**:
```python
llm_provider = context.service_container.resolve(LLMProvider)
memory_store = context.service_container.resolve(MemoryStore)
```

**Health Monitoring**:
```python
health = await agent.health()
# Reports to runtime health endpoint
```

## Future Extension Points

### Milestone 4: LLM Integration
- Implement specific `LLMProvider` for OpenAI/Anthropic/Gemini
- Connect planning to actual LLM models
- Implement prompt rendering

### Milestone 5: Tool Implementations
- Implement actual `FilesystemTool` with file operations
- Implement `VideoTool` with FFmpeg integration
- Implement `VisionTool` with image processing

### Milestone 6: Memory Systems
- Implement `WorkingMemory` with in-memory storage
- Implement `LongTermMemory` with database persistence
- Implement `SemanticMemory` with vector embeddings

### Milestone 7+: Workflow, Scheduling, Video Processing
- Each built on top of this foundation
- No rework of agent lifecycle or planning

## Design Principles

### Provider Agnostic
No hardcoded dependencies on specific AI providers. All provider interactions go through interfaces.

### Interface First
Every component is an interface with optional default implementations. Extensions inherit from these contracts.

### No Magic
No hidden behavior. What you see is what you get. All integration points explicit.

### Type Safe
Full Python type hints throughout. Every function signature is a contract.

### Event Driven
Agent lifecycle communicated via runtime EventBus. No direct coupling between components.

### Immutable Values
Goals, contexts, and results are immutable. Changes create new instances.

### Testable
All interfaces can be mocked. Components have minimal dependencies on concrete implementations.

## Key Architectural Decisions

1. **Interfaces Only for Providers**: No LLM calls, embeddings, vision, or generation until Milestone 4+. Keeps framework clean.

2. **Placeholder Tools**: Tools exist as interfaces + placeholders. Framework works, tools do nothing in Milestone 3.

3. **Immutable Goals**: Goals cannot be modified in-place. Changes create new instances, enabling history tracking.

4. **Event-Driven Lifecycle**: Agent actions publish events. Logging, monitoring, and future workflows hook into events.

5. **Sessions vs Contexts**: Sessions track execution metadata; Contexts carry execution state. Different concerns.

6. **State Machine Enforcement**: Invalid transitions raise errors immediately. No silent failures.

7. **Tool as Universal Capability**: Every future capability becomes a Tool. Consistent interface.

## Testing

All components are fully testable without implementation:

```python
# Mock provider
class MockLLMProvider(LLMProvider):
    async def complete(self, request):
        return CompletionResponse(text="mock response", model="mock", stop_reason="end", tokens_used=0)

# Mock tool
class MockTool(Tool):
    async def execute(self, **kwargs):
        return ToolResult(success=True, output="mock result")

# Test agent
agent = MyAgent()
agent.set_event_publisher(mock_publisher)
await agent.initialize()  # Works with mocks
```

## Comparison: Architecture vs Implementation

| Aspect | Milestone 3 | Milestone 4+ |
|--------|------------|-------------|
| Goals | ✓ Complete | ✓ Reused |
| Planning interface | ✓ Complete | Implement algorithm |
| Memory interface | ✓ Complete | Implement storage |
| Tools framework | ✓ Complete | Implement each tool |
| Providers interface | ✓ Complete | Implement (OpenAI, etc.) |
| Execution engine | ✓ Complete | Implement logic |
| Events | ✓ Complete | ✓ Reused |
| Agent lifecycle | ✓ Complete | Override methods |

## Conclusion

The AURA AI Framework provides:

✅ **Complete Architecture**: All contracts, interfaces, and domain models defined  
✅ **No Implementation Details**: Providers, tools, and algorithms left for future milestones  
✅ **Full Testability**: Mock every component, test framework without business logic  
✅ **Clean Extension Points**: Clear places to add AI logic, tool implementations, and providers  
✅ **Provider Agnostic**: No lock-in to any specific AI service  
✅ **Event Integrated**: Fully integrated with AURA Runtime  

This foundation enables Milestones 4-10 to be built cleanly on top without reworking core architecture.

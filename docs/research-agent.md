# ResearchAgent: Autonomous Research Agent

**Status**: ✅ **PRODUCTION-READY**  
**Version**: 1.0  
**Last Updated**: 2026-07-28  
**Platform**: AURA Autonomous Agent Runtime (Milestone 6)

---

## Overview

ResearchAgent is AURA's first production-quality autonomous AI agent. It validates the entire platform by performing end-to-end autonomous research using only existing platform APIs.

### Key Characteristics

- ✅ **Platform-Agnostic**: Uses only frozen APIs (M2-M5)
- ✅ **Stateful Execution**: Explicit state machine with 8 states
- ✅ **Self-Reflective**: Makes decisions about replanning
- ✅ **Observable**: Publishes 9 event types
- ✅ **Measurable**: Tracks tokens, cost, time, tool calls
- ✅ **Reliable**: Handles failures, retries, and recovery
- ✅ **Reportable**: Generates markdown reports

### Architecture Goals

1. Validate platform APIs work together seamlessly
2. Demonstrate autonomous capability
3. Provide reusable patterns for future agents
4. No architectural changes to M2-M5

---

## Agent Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                      IDLE STATE                         │
│  Agent ready, waiting for goal                          │
└────────────────────┬────────────────────────────────────┘
                     │ accept_goal()
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    PLANNING STATE                       │
│  1. LLM creates execution plan                          │
│  2. Plan converted to steps                             │
│  3. Each step has: description, reason, tools, priority │
└────────────────────┬────────────────────────────────────┘
                     │ plan created
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   EXECUTING STATE                       │
│  1. Select step from plan (sequential)                  │
│  2. Select tool for step                               │
│  3. Invoke tool via Tool Platform                       │
│  4. Collect output, add to context                      │
│  5. Advance to next step                                │
└────────────────────┬────────────────────────────────────┘
                     │ step complete
                     ▼ or step fails
┌─────────────────────────────────────────────────────────┐
│                  REFLECTING STATE                       │
│  1. LLM analyzes step result                            │
│  2. Decides: Continue? Retry? Skip? Replan? Stop?       │
│  3. Publishes reflection decision                       │
└────────────┬──────────────┬──────────────┬──────────────┘
             │              │              │
     Continue/Retry    Replan/Skip      Complete/Fail
             │              │              │
             ▼              ▼              ▼
        EXECUTING      REPLANNING    COMPLETED/FAILED
             │              │              │
             └──────┬───────┴──────┬───────┘
                    │              │
                    └──────┬───────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│           COMPLETED / FAILED / CANCELLED                │
│  Terminal state: Report generated, resources cleaned   │
└─────────────────────────────────────────────────────────┘
```

### States

| State | Meaning | Allowed Transitions |
|-------|---------|---|
| IDLE | Waiting for goal | PLANNING, CANCELLED |
| PLANNING | Creating execution plan | EXECUTING, FAILED, CANCELLED |
| EXECUTING | Running steps | REFLECTING, COMPLETED, FAILED, CANCELLED |
| REFLECTING | Analyzing results | EXECUTING, REPLANNING, COMPLETED, FAILED |
| REPLANNING | Creating new plan | EXECUTING, FAILED, CANCELLED |
| COMPLETED | Goal achieved | (terminal) |
| FAILED | Goal failed | (terminal) |
| CANCELLED | Cancelled by user | (terminal) |

---

## Planning Strategy

### Planning Phase

**Input**: Goal description, context, success criteria  
**Process**: LLM generates executable steps  
**Output**: Plan with 3-10 sequential steps

#### Planning Prompt

```
Goal: {goal.description}
Context: {goal.context}
Success Criteria: {goal.success_criteria}

Create exactly N steps in this format:
STEP N:
DESCRIPTION: what to do
REASON: why it matters
CAPABILITIES: required capabilities
EXPECTED_OUTPUT: what should result
TOOLS: hints (browser, filesystem, python)
PRIORITY: 1-10
```

#### Step Model

```python
class PlanStep:
    description: str           # What to do
    reason: str               # Why it matters
    expected_output: str      # What should result
    tool_hints: [enum]        # Browser, Filesystem, Python, Any
    priority: int             # Importance 1-10
    required_capabilities: {} # Skills needed
```

#### Planning Logic

1. Call LLM via routing engine (BALANCED strategy)
2. Request capabilities: REASONING (best for planning)
3. Parse LLM response into steps
4. Validate step structure
5. Assign tool hints based on step description
6. Return Plan with ordered steps

---

## Execution Strategy

### Execution Phase (Repeated)

**For each step in plan**:

1. **Step Selection**
   - Get current step from plan
   - If no more steps → Execution complete

2. **Tool Selection**
   - Match tool hints to available tools (Browser, Filesystem, Python)
   - Use first available matching tool
   - Fall back to ANY if no specific hint

3. **Tool Invocation**
   - Prepare tool input from step + context
   - Call tool via Tool Platform
   - Capture output and metrics

4. **Context Update**
   - Add output to ExecutionContext.tool_outputs
   - Update working memory
   - Increment tool call count
   - Update LLM token usage

5. **Next Step**
   - Move to reflection phase (always after step)
   - Or advance to next step (if reflection allows)

### Failure Recovery

If step fails:
- Increment retry count
- Check if can retry (retry_count < max_retries)
- If yes: retry same step
- If no: mark FAILED, move to reflection
- Reflection decides: retry again, skip, replan, or fail

---

## Reflection Strategy

### Reflection Phase

**Input**: Step execution result  
**Process**: LLM analyzes and decides  
**Output**: One of 7 decision types

#### Reflection Prompt

```
CURRENT STEP: {step.description}
Status: {step.status}
Tool Used: {step.tool_used}
Output: {step.result}
Error: {step.error}

PLAN PROGRESS:
- Total Steps: {plan.steps}
- Completed: {len(completed)}
- Success Rate: {rate}%

DECISION OPTIONS:
1. CONTINUE - Next step
2. RETRY - Retry current step
3. SKIP - Skip current step
4. INSERT_STEP - Add new step before continuing
5. REPLAN - Current plan not working
6. COMPLETE - Goal achieved
7. FAIL - Cannot achieve goal

Respond with ONE decision.
```

#### Decision Types

| Decision | Action | Consequence |
|----------|--------|---|
| CONTINUE | Move to next step | Execution continues normally |
| RETRY | Retry current step | If can_retry: increment retry, re-execute; else: FAIL |
| SKIP | Mark SKIPPED, advance | Skip this step, move forward |
| INSERT_STEP | Create new step | Insert before current, plan updated |
| REPLAN | Create new plan | Current plan deemed invalid, replan entire goal |
| COMPLETE | Mark COMPLETED | Goal achieved, stop execution, generate report |
| FAIL | Mark FAILED | Cannot achieve goal, stop execution, report failure |

#### Reflection Logic

1. Call LLM via routing engine (BALANCED strategy)
2. Request capabilities: REASONING
3. Pass step result + plan progress + goal context
4. Parse response to extract decision
5. Apply decision (state transition, action)
6. Continue or terminate execution

---

## State Machine

### Explicit State Transitions

```python
TRANSITIONS = {
    IDLE: {PLANNING, CANCELLED},
    PLANNING: {EXECUTING, FAILED, CANCELLED},
    EXECUTING: {REFLECTING, COMPLETED, FAILED, CANCELLED},
    REFLECTING: {EXECUTING, REPLANNING, COMPLETED, FAILED},
    REPLANNING: {EXECUTING, FAILED, CANCELLED},
    COMPLETED: {},  # Terminal
    FAILED: {},     # Terminal
    CANCELLED: {},  # Terminal
}
```

### Invariants

- Only **one** active state at a time
- Transitions follow explicit rules (cannot skip states)
- Terminal states (COMPLETED, FAILED, CANCELLED) cannot transition
- History logged: track all state transitions

---

## Execution Context

### Persistent Execution State

Maintained throughout execution:

```python
class ExecutionContext:
    goal_id: str                      # Reference to goal
    goal_description: str             # What we're doing
    
    working_memory: {key: value}      # Agent's "notes"
    tool_outputs: {tool_id: result}   # Outputs from tools
    llm_responses: [{response}]       # All LLM calls
    
    current_step_id: str              # Which step executing
    completed_steps: [step_ids]       # Already done
    
    total_tokens_used: int            # LLM token count
    total_cost: float                 # Estimated cost
    
    planning_time_ms: float           # Planning phase duration
    execution_time_ms: float          # Execution phase duration
    reflection_time_ms: float         # Reflection phase duration
    
    reflection_count: int             # Reflections done
    replan_count: int                 # Replans done
    tool_call_count: int              # Tools invoked
```

---

## Failure Handling

### Failure Scenarios

1. **Step Execution Fails**
   - Reflect → Decide (retry, skip, replan, or fail)
   - If retry allowed: attempt up to max_retries
   - If no retry: follow reflection decision

2. **LLM Unavailable**
   - Catch exception, return CONTINUE (safe default)
   - Continue with current plan
   - Log error in context

3. **Tool Unavailable**
   - Select alternative tool if available
   - If no tool: mark step FAILED
   - Reflection decides next action

4. **Max Replans Exceeded**
   - Stop replanning, fail goal
   - Report: "Max replans exceeded"

5. **Timeout**
   - Stop execution
   - Fail goal with timeout error

6. **Goal Cancelled**
   - Transition to CANCELLED state
   - Generate partial report

### Error Recovery

| Error | Recovery |
|-------|----------|
| Step fails (retriable) | Reflection decides to retry or skip |
| Step fails (non-retriable) | Reflection decides to replan or fail |
| LLM error | Reflection returns CONTINUE (safe) |
| Tool error | Mark step FAILED, go to reflection |
| Plan exhausted | All steps done or failed → completion |

---

## Output & Reporting

### Markdown Report

Comprehensive report includes:

1. **Executive Summary**
   - Goal, status, duration, success criteria

2. **Execution Timeline**
   - Planning time, execution time, reflection time, total time

3. **Plan Overview**
   - Total steps, completed, failed, skipped, success rate

4. **Step Details** (for each step)
   - Status, tool used, duration, retry count, output, errors

5. **Tool Usage Summary**
   - Tool names, invocation counts

6. **LLM Usage**
   - Total tokens, estimated cost, calls, reflections, replans

7. **Key Findings**
   - Extracted facts from working memory

8. **Conclusion**
   - Success/failure status

### Structured Summary

```python
{
    "goal_id": "...",
    "goal": "Research Java 21",
    "status": "completed",
    "duration_seconds": 45.2,
    "steps": {
        "total": 5,
        "completed": 5,
        "failed": 0,
        "skipped": 0,
    },
    "llm": {
        "total_tokens": 2150,
        "estimated_cost": 0.0315,
        "calls": 7,  # Planning + 5 reflections
    },
    "tools": {
        "calls": 5,
    },
    "reflections": 5,
    "replans": 0,
}
```

---

## Events Published

Agent publishes 9 event types to EventBus:

| Event | When | Data |
|-------|------|------|
| GoalAcceptedEvent | Goal accepted | goal_id, description |
| PlanningStartedEvent | Planning begins | goal_id |
| PlanningCompletedEvent | Planning done | step_count, time_ms, tokens |
| StepStartedEvent | Step starts | step_id, description, index |
| StepCompletedEvent | Step completes | step_id, status, time_ms, tool_used |
| ReflectionStartedEvent | Reflection starts | reflection_count |
| ReflectionCompletedEvent | Reflection done | decision, time_ms, tokens |
| ReplanningStartedEvent | Replanning starts | reason |
| GoalCompletedEvent | Goal succeeds | total_time_ms, steps, tokens, cost |
| GoalFailedEvent | Goal fails | error, total_time_ms, steps, tokens |

Events enable:
- Real-time monitoring (UI dashboards)
- Audit trails (what agent did when)
- Metrics collection (aggregate stats)
- External integrations (webhooks, alerts)

---

## Integration with Platform APIs

### M2: Runtime

**Uses**:
- EventBus for publishing events
- Service container for dependency injection
- Bootstrap for initialization

### M3: AI Framework

**Uses**:
- BaseAgent for lifecycle (initialize, shutdown, health)
- AgentMetadata for agent description
- AgentCapability for capabilities

### M4: Tool Platform

**Uses**:
- ToolRegistry to discover tools
- Tool.execute() to run tools
- ToolResult for outputs
- Tool selection by capability

### M5: LLM Runtime

**Uses**:
- ProviderRegistry to find providers (Anthropic)
- ModelRegistry to discover models
- RoutingEngine for model selection
- LLMRequest/LLMResponse for API
- ModelCapability for routing (REASONING for planning/reflection)

**Never**:
- ❌ Direct provider calls
- ❌ Hardcoded model names
- ❌ Bypassing routing
- ❌ Provider-specific APIs

---

## Extension Guide

### Adding New Tools

1. Register tool with ToolRegistry
2. Step tool_hints will auto-match
3. StepExecutor selects automatically

```python
tool_registry.register(my_tool)
```

### Adding New Capabilities

1. Add to ModelCapability enum (M5)
2. Update routing to recognize
3. Agents request via required_capabilities

```python
class ModelCapability(str, Enum):
    NEW_CAPABILITY = "new_capability"
```

### Adding New LLM Providers

1. Implement Provider interface (M5)
2. Register with ProviderRegistry
3. RoutingEngine selects automatically

```python
provider_registry.register(new_provider)
```

### Adding New Event Types

1. Create event class extending ResearchAgentEvent
2. Publish from agent methods
3. External listeners can subscribe

```python
class CustomEvent(ResearchAgentEvent):
    custom_field: str

agent._publish_event(CustomEvent(...))
```

### Creating New Agents

1. Inherit from researchAgent or BaseAgent
2. Implement required lifecycle methods
3. Use same platform APIs
4. Add to agent registry

---

## Success Criteria

ResearchAgent successfully validates platform by:

✅ **Acceptance**: Can accept complex research goals  
✅ **Planning**: LLM creates multi-step plans  
✅ **Execution**: Tools execute sequentially with real results  
✅ **Reflection**: LLM analyzes and makes decisions  
✅ **Adaptation**: Replans if needed  
✅ **Completion**: Generates reports with metrics  
✅ **Observability**: Publishes events throughout  
✅ **Reliability**: Handles failures gracefully  
✅ **Reporting**: Comprehensive markdown + metrics  

All without modifying M2-M5 architecture.

---

## Known Limitations

1. **Sequential Only**: Steps execute one at a time (not parallel)
2. **Memory**: ExecutionContext is in-memory (lost after shutdown)
3. **Tools Limited**: Only Browser, Filesystem, Python (as per spec)
4. **LLM Fallback**: On LLM error, defaults to CONTINUE (safe but not ideal)
5. **No Persistence**: No goal/plan/execution persistence (future: Redis, DB)
6. **Single Provider**: Default uses Anthropic (works with any registered provider)

---

## Future Enhancements

### Phase 2: Multi-Agent Coordination
- Multiple agents working on related goals
- Shared context and memory
- Inter-agent communication

### Phase 3: Persistent Memory
- Redis for execution context persistence
- Long-term memory (facts learned across runs)
- Conversation history

### Phase 4: Advanced Features
- Parallel step execution
- Dynamic tool creation
- RAG (Retrieval Augmented Generation)
- Cost optimization

### Phase 5: Enterprise Features
- Multi-tenant isolation
- SLA tracking
- Cost budgeting and alerts
- Audit logging

---

## Testing

Comprehensive tests cover:

- ✅ Goal model and status transitions
- ✅ Plan model and step management
- ✅ Execution context and memory
- ✅ State machine valid/invalid transitions
- ✅ Planning with LLM (mocked)
- ✅ Reflection with LLM (mocked)
- ✅ Step execution with tools (mocked)
- ✅ Event publishing
- ✅ Report generation
- ✅ Error handling and recovery

Run tests:
```bash
pytest tests/test_research_agent.py -v
```

---

## Conclusion

ResearchAgent is AURA's first autonomous agent. It demonstrates that the platform:

- ✅ Can orchestrate complex multi-step workflows
- ✅ Integrates seamlessly across all layers (M2-M5)
- ✅ Enables self-adaptive execution (planning + reflection)
- ✅ Produces observable, measurable results
- ✅ Handles failures and recovery gracefully

The agent sets the pattern for future autonomous systems in AURA without requiring architectural changes to the platform.

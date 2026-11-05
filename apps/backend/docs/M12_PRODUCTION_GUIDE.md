# Milestone 12: Rendering Engine — Production Guide

## Overview

M12 is the complete rendering execution engine for the AURA AI Platform. It transforms EditPlans from M11 (Research) into ArtifactBundles through a unified provider-agnostic pipeline, integrated with M8 Task Orchestration for complete traceability and recovery.

## Architecture

### Core Components

**Phase 1: Domain Models & Provider Interface**

- `RenderJob`, `RenderTask`, `RenderSegment`: Pipeline units with immutable specs
- `RendererProvider`: Abstract interface (14 methods) enabling provider swappability
- `MockRendererProvider` (test), `FFmpegProvider` (real-world): Full interface implementation

**Phase 2: Stateless Rendering Engines**

- 10 specialized renderers: ClipRenderer → CompositeRenderer → ExportRenderer
- RenderContext + RenderCapability for capability negotiation
- Pure functions consuming EditPlan, producing partial artifacts

**Phase 3: M6/M8 Integration & Orchestration**

- RenderingPlanner: EditPlan → RenderStage DAG with proper dependencies
- 10 M6 agents wrapping engines, implementing ExecutableAgent
- RenderingAgentRegistry for M8 integration
- RenderFailure + lifecycle events for complete traceability

**Phase 4: Production Readiness**

- MetricsAggregator: Real-time performance tracking, retention
- DashboardProvider: Live job progress, provider status, charts
- PerformanceOptimizer: Provider selection, parallel execution scheduling
- Integration tests + benchmark suite
- Full documentation

### Data Flow

```
EditPlan (M11 output)
  ↓
RenderingPlanner.create_stage_dag()
  ↓
[RenderStage DAG with dependencies]
  ↓
planner.stages_to_m8_tasks()
  ↓
[M8 Task objects]
  ↓
M8 Orchestration (executes via M6 agents)
  ↓
Each agent calls engine.render_*()
  ↓
RendererProvider executes (mock/ffmpeg/custom)
  ↓
RenderingMetrics + RenderFailure events emitted
  ↓
ArtifactBundle assembled
```

## Production Deployment

### Prerequisites

```bash
# Java 17+
java -version

# Python 3.10+
python3 --version

# For FFmpeg provider: ffmpeg 4.0+
ffmpeg -version

# Optional: NVIDIA GPU for H.265, advanced codecs
nvidia-smi
```

### Configuration

Set these environment variables before startup:

```bash
# Provider selection (mock, ffmpeg, or custom)
LANDREGISTRY_RENDERER_DEFAULT_PROVIDER=ffmpeg

# GPU acceleration
LANDREGISTRY_RENDERER_GPU_ENABLED=true
LANDREGISTRY_RENDERER_GPU_MEMORY_LIMIT_MB=4096

# Quality profiles
LANDREGISTRY_RENDERER_QUALITY_PRESET=high
LANDREGISTRY_RENDERER_TARGET_BITRATE_KBPS=5000

# Timeout and retry policy
LANDREGISTRY_RENDERER_TIMEOUT_SECONDS=600
LANDREGISTRY_RENDERER_MAX_RETRIES=3

# Metrics retention
LANDREGISTRY_RENDERER_METRICS_RETENTION_HOURS=24
```

### Startup

```bash
# Build
cd app-backend && mvn clean package

# Run with rendering enabled
SPRING_PROFILES_ACTIVE=prod \
LANDREGISTRY_RENDERER_DEFAULT_PROVIDER=ffmpeg \
LANDREGISTRY_RENDERER_GPU_ENABLED=true \
JAVA_HOME=$(/usr/libexec/java_home -v 17) \
mvn spring-boot:run
```

## Provider Selection

### MockRendererProvider

**When to use:**

- Development and testing
- CI/CD pipelines
- Prototyping new features
- Validating EditPlan structure before committing to expensive FFmpeg runs

**Characteristics:**

- Always available (no external dependencies)
- Fast (< 1ms per operation)
- Deterministic (reproduces identical outputs)
- All capabilities enabled (no real rendering)

**Example:**

```python
from aura_backend.rendering import MockRendererProvider, RenderContext

provider = MockRendererProvider()
context = RenderContext(session_id="s1", job_id="j1")

# Render immediately, always succeeds
await provider.render_clip(clip_data, context)
```

### FFmpegProvider

**When to use:**

- Production rendering
- Real video quality assessment
- Codec compatibility validation
- Performance benchmarking

**Characteristics:**

- Real ffmpeg library (4.0+)
- Supports H.264, H.265, VP9, AV1
- GPU acceleration if CUDA available
- May timeout or fail if system resources exhausted

**Limitations:**

- Transitions, overlays, zoom require complex filtergraphs (documented as unsupported)
- Memory usage scales with video resolution and duration
- I/O bound on shared storage

**Example:**

```python
from aura_backend.rendering import FFmpegProvider

provider = FFmpegProvider()

# Check availability before use
if await provider.is_available():
    result = await provider.export_video(segments, format, context)
```

### Custom Providers

To add a new provider (e.g., OpenShot, DaVinci):

1. Extend `RendererProvider` abstract class
2. Implement all 14 methods
3. Declare capabilities via `RenderCapability`
4. Register in ProviderRegistry

```python
class CustomProvider(RendererProvider):
    async def render_clip(self, clip, context):
        # Custom implementation
        return RenderedAsset(...)

    # ... implement remaining 13 methods

    @property
    def capabilities(self) -> RenderCapability:
        return RenderCapability(...)
```

## Failure Handling

### Automatic Recovery

M12 implements 3-tier failure recovery:

**Tier 1: Retry with same provider**

- Transient failures (network, timeouts, race conditions)
- Max retries: 3 (configurable)
- Backoff: exponential (1s, 2s, 4s)
- Logged in `RenderFailure.retry_count`

**Tier 2: Fallback to alternative provider**

- After retries exhausted, try fallback provider
- Automatically selected if original provider unsuitable
- e.g., ffmpeg → mock (if mock supports stage type)
- Logged in `RenderFailure.fallback_provider`

**Tier 3: Manual intervention (rare)**

- Only unrecoverable errors without fallback
- Logged with full stack trace
- Surfaces in dashboard as StageFailed event

### Checking Recovery Status

```python
from aura_backend.rendering.stages import RenderFailure

# During/after rendering
if failure.is_recoverable:
    if failure.retry_count < failure.max_retries:
        # Will retry
        print(f"Retrying {failure.stage_id} (attempt {failure.retry_count + 1})")
    elif failure.can_use_fallback:
        # Falling back to alternative
        print(f"Falling back to {failure.fallback_provider}")
else:
    # Unrecoverable—requires manual intervention
    print(f"CRITICAL: {failure.error_message}")
    print(f"Recovery info: {failure.recovery_info}")
```

## Optimization Strategies

### Provider Selection

Use `PerformanceOptimizer.select_best_provider()` to choose provider based on:

- Capability match (provider must support stage requirements)
- Recent success rate (higher = higher score)
- Average duration (lower = higher score)

```python
from aura_backend.rendering.dashboard import PerformanceOptimizer

stage = stages[0]
capabilities = {...}  # {provider: RenderCapability}
metrics = {...}  # {provider: ProviderMetrics}

best = PerformanceOptimizer.select_best_provider(stage, capabilities, metrics)
# Returns: "ffmpeg" or "mock" based on scoring
```

### Parallel Execution

Identify stages that can execute in parallel:

```python
parallel_groups = PerformanceOptimizer.calculate_parallel_stages(stages)
# Returns: {"wave_1": ["s1"], "wave_2": ["s2"], "wave_3": ["s3", "s4"]}
```

Stages in the same wave can run concurrently. M8 Task Orchestration handles the actual parallel dispatch.

### Resource Scheduling

Estimate total time accounting for parallelism:

```python
estimated_seconds = PerformanceOptimizer.estimate_total_duration(stages)
# Accounts for dependency chains and parallel waves
```

Use this to:

- Warn users of long render times upfront
- Scale resource allocation dynamically
- Auto-scale job queue based on ETA

## Metrics and Monitoring

### Real-Time Dashboard

Access job progress, provider status, and performance charts:

```python
from aura_backend.rendering.dashboard import DashboardProvider
from aura_backend.rendering.metrics import MetricsAggregator

aggregator = MetricsAggregator()
dashboard = DashboardProvider(aggregator)

# Register running job
dashboard.register_job("job-123", stages)

# Query progress
progress = dashboard.get_job_progress("job-123")
# {
#   "job_id": "job-123",
#   "total_stages": 8,
#   "completed_stages": 3,
#   "progress_percent": 37.5,
#   "stages": [...]
# }

# Provider status
status = dashboard.get_provider_status()
# {
#   "ffmpeg": {"success_rate": 0.95, "avg_duration": 15.2, "peak_memory_mb": 1024, ...},
#   "mock": {"success_rate": 1.0, "avg_duration": 0.5, ...}
# }

# Performance summary
summary = dashboard.get_performance_summary()
# {
#   "period": "1 hour",
#   "jobs_completed": 42,
#   "throughput_per_hour": 42,
#   "failure_rate_percent": 2.4,
#   "avg_retries": 0.1,
#   "providers": {...}
# }
```

### Metrics Retention

MetricsAggregator automatically purges data older than 24 hours. Adjust via:

```python
aggregator = MetricsAggregator(retention_hours=72)  # 3 days
```

### Logging

All rendering events logged to standard logging system:

```bash
# View rendering events
tail -f logs/app.log | grep "RenderingEvent"

# View failures only
tail -f logs/app.log | grep "StageFailed"

# View metrics summaries
tail -f logs/app.log | grep "PerformanceSummary"
```

## Testing in Production

### Dry-Run Mode

Test rendering without modifying production data:

```python
context = RenderContext(
    session_id="prod-test-1",
    job_id="dry-run-123",
    dry_run=True  # Stages execute but artifacts not persisted
)
```

### Canary Rendering

Route small percentage of jobs through new provider:

```python
# In environment config
LANDREGISTRY_RENDERER_CANARY_PROVIDER=new_provider
LANDREGISTRY_RENDERER_CANARY_TRAFFIC_PERCENT=5
```

Monitor dashboards and metrics before ramping to 100%.

## Troubleshooting

### Common Issues

**Rendering timeout**

- Increase `LANDREGISTRY_RENDERER_TIMEOUT_SECONDS`
- Check disk space and memory
- Reduce video resolution if possible

**High failure rate**

- Check provider availability: `ffmpeg -version`
- Verify system resources not exhausted
- Inspect StageFailed events for specific error messages

**Slow rendering**

- Enable GPU: `LANDREGISTRY_RENDERER_GPU_ENABLED=true`
- Check provider selection (mock too slow? → use ffmpeg)
- Review parallel execution—are stages serialized unnecessarily?

**Memory exhaustion**

- Reduce clip count per job
- Limit parallel execution (M8 config)
- Scale horizontally (multiple render workers)

### Debug Logging

Enable verbose rendering logs:

```bash
LANDREGISTRY_RENDERER_LOG_LEVEL=DEBUG \
SPRING_PROFILES_ACTIVE=prod \
mvn spring-boot:run
```

## Appendix: Common EditPlans

### Simple 2-clip transition

```python
from aura_backend.editing import EditPlan, Clip, Transition, TransitionType

plan = EditPlan(
    clips=[
        Clip(session_id="s1", video_id="v1", start_timestamp=0.0, end_timestamp=5.0),
        Clip(session_id="s1", video_id="v1", start_timestamp=5.0, end_timestamp=10.0),
    ],
    transitions=[
        Transition(
            from_clip_id=...,
            to_clip_id=...,
            transition_type=TransitionType.FADE,
            duration_seconds=0.5,
        ),
    ],
)
# Stages: CLIP_RENDER → COMPOSITE → EXPORT → VALIDATE
```

### Full featured: clips + subtitles + overlays + music

```python
plan = EditPlan(
    clips=[...],
    subtitles=[SubtitleSegment(...)],
    overlays=[Overlay(...)],
    music_suggestions=[MusicCue(...)],
)
# Stages: CLIP_RENDER → COMPOSITE → SUBTITLE → OVERLAY → AUDIO → EXPORT → VALIDATE
```

See [M11_RESEARCH_GUIDE.md](./M11_RESEARCH_GUIDE.md) for full EditPlan schema.

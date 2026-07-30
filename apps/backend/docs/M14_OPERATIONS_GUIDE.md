# M14 Operations Guide – Monitoring & Troubleshooting

## Operational Dashboard

### Real-Time Dashboard Access

```python
from aura_backend.learning.dashboard import LearningDashboard

dashboard = LearningDashboard()
snapshot = dashboard.get_dashboard_snapshot()

# Display dashboard
print(f"Queue size: {snapshot['queue']['size']}")
print(f"Provider health: {snapshot['provider_health']['healthy']}/{snapshot['provider_health']['total']}")
print(f"Active jobs: {snapshot['analytics_progress']['active_jobs']}")
print(f"Avg progress: {snapshot['analytics_progress']['avg_progress_percent']:.0f}%")
```

### Dashboard Components

#### 1. Queue Monitoring

```python
# Get current queue
queue = dashboard.get_queue(limit=50)
for item in queue:
    wait_time = (datetime.utcnow() - item.queued_at).total_seconds()
    print(f"Job {item.job_id}: {item.platform}, priority {item.priority}, wait {wait_time:.0f}s")

# Check queue size and priority distribution
snapshot = dashboard.get_dashboard_snapshot()
print(f"Queue size: {snapshot['queue']['size']}")
print(f"Avg priority: {snapshot['queue']['avg_priority']:.1f}")
```

#### 2. Provider Health

```python
# Get provider health
provider_health = dashboard.get_provider_health()
for name, health in provider_health.items():
    print(f"{name}:")
    print(f"  Status: {health.status}")
    print(f"  Success rate: {health.success_rate:.1%}")
    print(f"  Avg latency: {health.avg_latency_ms:.0f}ms")
    print(f"  Failed requests: {health.failed_requests}/{health.total_requests}")
```

#### 3. Analytics Progress

```python
# Track active analytics collections
progress_list = dashboard.get_all_progress()
for progress in progress_list:
    print(f"Job {progress.job_id}:")
    print(f"  Platform: {progress.platform}")
    print(f"  Stage: {progress.stage_type}")
    print(f"  Progress: {progress.progress_percent}%")
    print(f"  Step: {progress.current_step}")
```

#### 4. Recommendations

```python
# View generated recommendations
summary = dashboard.get_recommendations("job-1")
if summary:
    print(f"Total: {summary.total_count}")
    print(f"High priority: {summary.high_priority}")
    print(f"Avg confidence: {summary.avg_confidence:.2f}")
    print(f"By category: {summary.categories}")
```

#### 5. Creator Profile Evolution

```python
# Track creator learning progression
history = dashboard.get_creator_history("creator-1")
for evolution in history:
    print(f"Version {evolution.profile_version} ({evolution.timestamp}):")
    print(f"  Fields updated: {evolution.fields_updated}")
    print(f"  Video length change: {evolution.avg_video_length_change:+.1f} min")
    print(f"  Topic diversity change: {evolution.topic_diversity_change:+.2f}")
```

#### 6. Memory Statistics

```python
# Check learning memory usage
stats = dashboard.get_memory_statistics("creator-1")
if stats:
    print(f"Total experiments: {stats.total_experiments}")
    print(f"Recommendations seen: {stats.total_recommendations_seen}")
    print(f"Acceptance rate: {stats.acceptance_rate:.1%}")
    print(f"Memory size: {stats.memory_size_kb:.1f} KB")
```

## Metrics Analysis

### Accessing Operational Metrics

```python
from aura_backend.learning.operational_metrics import OperationalMetricsAggregator

metrics = OperationalMetricsAggregator()

# Get comprehensive report
report = metrics.get_comprehensive_report()
```

### Stage Execution Analysis

```python
# Analyze stage performance
stats = metrics.get_stage_duration_stats("retrieve_metrics")
print(f"Stage: retrieve_metrics")
print(f"  Executions: {stats['count']}")
print(f"  Avg duration: {stats['avg_ms']:.0f}ms")
print(f"  Range: {stats['min_ms']:.0f}ms - {stats['max_ms']:.0f}ms")
print(f"  Success rate: {stats['success_rate']:.1%}")
print(f"  By platform:")
for platform, data in stats['by_platform'].items():
    print(f"    {platform}: {data['avg_ms']:.0f}ms ({data['count']} runs)")
```

### Provider Performance

```python
# Analyze provider latencies
stats = metrics.get_provider_latency_stats("youtube")
print(f"Provider: youtube")
print(f"  Calls: {stats['count']}")
print(f"  Avg latency: {stats['avg_ms']:.0f}ms")
print(f"  Success rate: {stats['success_rate']:.1%}")
print(f"  By method:")
for method, data in stats['by_method'].items():
    print(f"    {method}: {data['avg_ms']:.0f}ms ({data['count']} calls)")
```

### Recommendation Quality

```python
# Analyze recommendation generation
stats = metrics.get_recommendation_stats()
print(f"Total generated: {stats['total_generated']}")
print(f"Avg confidence: {stats['avg_confidence']:.2f}")
print(f"Avg generation time: {stats['avg_generation_time_ms']:.0f}ms")
print(f"By category:")
for category, count in stats['by_category'].items():
    print(f"  {category}: {count}")

# Analyze confidence distribution
dist = metrics.get_confidence_distribution()
print(f"Confidence distribution:")
print(f"  High (≥0.8): {dist['high']} ({dist['high_percent']:.0f}%)")
print(f"  Medium (0.5-0.8): {dist['medium']} ({dist['medium_percent']:.0f}%)")
print(f"  Low (<0.5): {dist['low']} ({dist['low_percent']:.0f}%)")
print(f"  Avg: {dist['avg_confidence']:.2f}")
```

### Throughput Analysis

```python
# Analyze system throughput
stats = metrics.get_throughput_stats()
print(f"Throughput:")
print(f"  Completed: {stats['total_completed']}")
print(f"  Failed: {stats['total_failed']}")
print(f"  In progress: {stats['total_in_progress']}")
print(f"  Avg success rate: {stats['avg_success_rate']:.1%}")
print(f"  Avg duration: {stats['avg_duration_seconds']:.0f}s")
```

## Performance Optimization

### Queue Optimization

```python
from aura_backend.learning.optimizer import QueueOptimizer

optimizer = QueueOptimizer(max_parallel_jobs=10)

# Check if can process job immediately
can_process = optimizer.should_process_immediately("job-1", priority=8)

# Get optimization recommendations
decisions = optimizer.optimize_queue([
    ("job-1", 5),
    ("job-2", 3),
    ("job-3", 8),
])

for decision in decisions:
    if decision.reorder:
        print(f"Deprioritize {decision.job_id}: {decision.reason}")
    else:
        print(f"Process {decision.job_id}: {decision.reason}")
```

### Cache Management

```python
from aura_backend.learning.optimizer import RecommendationCacheManager

cache = RecommendationCacheManager(ttl_minutes=60)

# Monitor cache efficiency
stats = cache.get_stats()
print(f"Cache stats:")
print(f"  Total entries: {stats['total_entries']}")
print(f"  Valid entries: {stats['valid_entries']}")
print(f"  Expired entries: {stats['expired_entries']}")
print(f"  Capacity used: {stats['capacity_used_percent']:.0f}%")

# Invalidate stale cache for creator
invalidated = cache.invalidate("creator-1")
print(f"Invalidated {invalidated} entries for creator-1")
```

### Retry Optimization

```python
from aura_backend.learning.optimizer import RetryOptimizer

retry_opt = RetryOptimizer(max_retries=3)

# Determine retry strategy for transient error
should_retry, backoff = retry_opt.should_retry(
    "stage-1",
    "timeout",
    retry_count=1
)
print(f"Should retry: {should_retry}, backoff: {backoff}s")

# Get retry strategy for unreliable provider
strategy = retry_opt.get_retry_strategy("youtube", success_rate=0.92)
print(f"Retry strategy for youtube:")
print(f"  Max retries: {strategy['max_retries']}")
print(f"  Backoff base: {strategy['backoff_base']}")
```

### Parallel Collection

```python
from aura_backend.learning.optimizer import ParallelAnalyticsCollector

collector = ParallelAnalyticsCollector(max_parallel=5)

# Start collection for multiple platforms
platforms_to_collect = collector.start_collection("job-1", ["youtube", "tiktok", "instagram"])
print(f"Started collection for: {platforms_to_collect}")

# Check collection status
summary = collector.get_collection_summary("job-1")
print(f"Active platforms: {summary['active_platforms']}")
print(f"Capacity used: {summary['parallel_capacity_used']}/{summary['max_parallel']}")

# Complete collection for platform
collector.finish_collection("job-1", "youtube")
```

## Common Operations

### Check System Health

```python
def check_system_health(dashboard, metrics):
    """Quick health check of learning system."""

    # 1. Check queue
    queue = dashboard.get_queue()
    if len(queue) > 1000:
        print("WARNING: Queue backlog detected")

    # 2. Check provider health
    provider_health = dashboard.get_provider_health()
    for name, health in provider_health.items():
        if health.status != "healthy":
            print(f"WARNING: {name} is {health.status}")
        if health.success_rate < 0.95:
            print(f"WARNING: {name} success rate low ({health.success_rate:.1%})")

    # 3. Check stage durations
    stats = metrics.get_stage_duration_stats()
    if stats['avg_ms'] > 500:
        print("WARNING: Stage execution slow")

    # 4. Check recommendations
    rec_stats = metrics.get_recommendation_stats()
    if rec_stats['total_generated'] == 0:
        print("WARNING: No recommendations generated")

    print("Health check complete")

check_system_health(dashboard, metrics)
```

### Scale Queue Processing

```python
def scale_queue_processing(optimizer, new_max_jobs):
    """Adjust parallelism."""

    current_active = optimizer.get_active_count()
    print(f"Current active jobs: {current_active}")

    # Create new optimizer with higher capacity
    optimizer = QueueOptimizer(max_parallel_jobs=new_max_jobs)
    print(f"Scaled to {new_max_jobs} parallel jobs")

    # Check if queue will drain faster
    if current_active < new_max_jobs:
        print("Can now process more jobs in parallel")

    return optimizer
```

### Analyze Failure Patterns

```python
def analyze_failures(metrics):
    """Identify failure patterns."""

    # Get stage failures
    stats = metrics.get_stage_duration_stats()
    success_rate = stats.get('success_rate', 1.0)

    if success_rate < 0.95:
        print(f"Stage success rate: {success_rate:.1%}")

        # Check provider latency for correlation
        provider_stats = metrics.get_provider_latency_stats()
        if provider_stats['avg_ms'] > 500:
            print("  -> Possible cause: Provider latency high")

    # Check by platform
    print("Failure by platform:")
    for platform, data in stats.get('by_platform', {}).items():
        print(f"  {platform}: {data['avg_ms']:.0f}ms")
```

## Incident Response

### Common Incidents

#### Provider Outage

1. **Detect**: Monitor provider health status
2. **Alert**: Check `ProviderHealthStatus.UNAVAILABLE`
3. **Respond**:
   ```python
   # Use fallback provider
   selection = selector.select_provider(context, caps, providers)
   if selection.fallback_provider:
       use_provider(selection.fallback_provider)
   ```
4. **Track**: Record in metrics
5. **Resolve**: Restore provider or promote fallback

#### Queue Backlog

1. **Detect**: Queue size > threshold (default 1000)
2. **Alert**: Check `dashboard.get_queue_size()`
3. **Respond**:
   ```python
   # Increase parallelism
   optimizer = QueueOptimizer(max_parallel_jobs=20)
   ```
4. **Track**: Monitor queue drain time
5. **Resolve**: Revert when backlog cleared

#### Slow Stage Execution

1. **Detect**: Avg stage duration > threshold (default 500ms)
2. **Alert**: Check `metrics.get_stage_duration_stats()`
3. **Respond**:
   ```python
   # Enable parallel collection
   collector = ParallelAnalyticsCollector(max_parallel=10)
   ```
4. **Track**: Monitor latency trend
5. **Resolve**: Identify bottleneck (provider vs agent)

## Maintenance Tasks

### Daily

- Review dashboard snapshot
- Check provider health
- Verify no critical alerts
- Check queue backlog trend

### Weekly

- Review metrics report
- Analyze failure patterns
- Check cache efficiency
- Review provider performance

### Monthly

- Full performance audit
- Scaling analysis
- Cache tuning review
- Disaster recovery drill
- Credentials rotation

### Quarterly

- Provider comparison analysis
- Capacity planning review
- Cost analysis
- Security audit

## Performance Targets

| Metric                         | Target  | Warning  | Critical |
| ------------------------------ | ------- | -------- | -------- |
| Queue size                     | < 100   | > 500    | > 1000   |
| Avg stage duration             | < 200ms | > 500ms  | > 1000ms |
| Provider success rate          | > 99%   | < 95%    | < 90%    |
| Provider latency               | < 200ms | > 500ms  | > 1000ms |
| Recommendation generation time | < 300ms | > 500ms  | > 1000ms |
| Cache hit rate                 | > 50%   | > 30%    | < 20%    |
| Queue backlog age              | < 5 min | > 10 min | > 30 min |

## Log Analysis

### Key Log Patterns

```bash
# Provider failures
grep "provider.*error" logs/learning.log | tail -20

# Stage timeouts
grep "stage.*timeout" logs/learning.log | tail -20

# Queue events
grep "queue.*add\|queue.*remove" logs/learning.log | tail -20

# Cache events
grep "cache.*hit\|cache.*miss" logs/learning.log | tail -20

# Recommendation generation
grep "recommendation.*generated" logs/learning.log | tail -20
```

### Performance Profiling

```python
import cProfile
import pstats

# Profile stage execution
pr = cProfile.Profile()
pr.enable()

stages = planner.create_stage_dag(job, context, None)

pr.disable()
ps = pstats.Stats(pr)
ps.sort_stats('cumulative')
ps.print_stats(10)  # Top 10 functions
```

## Reference

- [M14 Overview](M14_OVERVIEW.md) – Architecture and design
- [M14 Production Guide](M14_PRODUCTION_GUIDE.md) – Deployment and scaling
- [M14 Benchmarks](M14_BENCHMARKS.md) – Performance characteristics

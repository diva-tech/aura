# M14 Production Guide – Deployment & Configuration

## Deployment

### Prerequisites

- Python 3.11+
- M8 task orchestration runtime
- Redis (optional, for caching)
- Provider API credentials (YouTube, TikTok, Instagram, LinkedIn, Podcast)

### Installation

```bash
cd app-backend
pip install -r requirements.txt
```

### Configuration

Environment variables:

```bash
# Learning Configuration
LEARNING_ENABLED=true
LEARNING_MAX_PARALLEL_JOBS=10
LEARNING_CACHE_TTL_MINUTES=60

# Provider Configuration
YOUTUBE_API_KEY=your-key
TIKTOK_API_KEY=your-key
INSTAGRAM_API_TOKEN=your-token
LINKEDIN_API_KEY=your-key
PODCAST_API_KEY=your-key

# Dashboard Configuration
DASHBOARD_SNAPSHOT_INTERVAL_SECONDS=60
DASHBOARD_MAX_QUEUE_SIZE=5000

# Metrics Configuration
METRICS_MAX_HISTORY=10000
METRICS_AGGREGATION_INTERVAL_SECONDS=300
```

## Production Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (80% code coverage minimum)
- [ ] Benchmarks run and performance acceptable
- [ ] Provider credentials validated
- [ ] M8 orchestration runtime available
- [ ] Monitoring infrastructure ready
- [ ] Alert thresholds configured

### Deployment

- [ ] Deploy M14 code
- [ ] Configure environment variables
- [ ] Verify provider registry initialization
- [ ] Initialize learning dashboard
- [ ] Start metrics aggregator
- [ ] Verify M8 integration
- [ ] Enable learning orchestration

### Post-Deployment

- [ ] Monitor dashboard for queue health
- [ ] Check provider health metrics
- [ ] Verify agent registry
- [ ] Monitor stage execution times
- [ ] Check failure rates
- [ ] Validate cache hit rates

## Scaling Considerations

### Horizontal Scaling

**Dashboard & Metrics:**

- Dashboard is stateless and can run in multiple instances
- Metrics aggregator should be centralized or use Redis backend
- Queues should be backed by distributed cache

**Providers:**

- Each provider instance should be independent
- Rate limits should be managed per instance or centrally
- Cache should be shared across instances

**Agents:**

- M6 agents are stateless and can run in parallel
- Agent registry should be shared or cached
- Task graph should be coordinated by M8

### Configuration for Scale

```python
# For production with multiple instances
LEARNING_MAX_PARALLEL_JOBS=50  # Higher parallelism
METRICS_MAX_HISTORY=50000      # Larger metrics window
DASHBOARD_MAX_QUEUE_SIZE=10000 # Larger queue
CACHE_TYPE=redis               # Use Redis for shared cache
```

## Monitoring

### Key Metrics to Monitor

1. **Queue Health**
   - Queue size (should stay < max_queue_size)
   - Average priority (indicates job prioritization)
   - Wait times (should trend down)

2. **Provider Health**
   - Success rate per provider (target > 95%)
   - Average latency per provider (target < 500ms)
   - Failed request count (should be low)
   - Rate limit usage (should stay < 80%)

3. **Stage Execution**
   - Average stage duration by type
   - Success rate by stage (target > 98%)
   - Retry count distribution
   - Failure by error type

4. **Recommendations**
   - Total count generated
   - Confidence distribution
   - Category breakdown
   - Generation time

5. **System Health**
   - Active job count
   - Memory usage by component
   - Cache hit rates
   - Queue processing rate

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Queue metrics
queue_size = Gauge('learning_queue_size', 'Current queue size')
queue_priority_avg = Gauge('learning_queue_priority_avg', 'Average queue priority')

# Stage metrics
stage_duration = Histogram('learning_stage_duration_ms', 'Stage execution duration')
stage_failures = Counter('learning_stage_failures_total', 'Total stage failures', ['stage_type'])

# Provider metrics
provider_latency = Histogram('learning_provider_latency_ms', 'Provider call latency', ['provider'])
provider_success_rate = Gauge('learning_provider_success_rate', 'Provider success rate', ['provider'])

# Recommendation metrics
recommendations_generated = Counter('learning_recommendations_total', 'Total recommendations')
confidence_avg = Gauge('learning_confidence_avg', 'Average recommendation confidence')
```

## Alerting

### Alert Rules

```yaml
groups:
  - name: learning_engine
    rules:
      # Queue alerts
      - alert: LearningQueueBacklog
        expr: learning_queue_size > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Learning queue backlog detected"

      # Provider health alerts
      - alert: ProviderSuccessRateLow
        expr: learning_provider_success_rate < 0.85
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Provider {{ $labels.provider }} success rate low"

      # Stage failure alerts
      - alert: StageFailureRateHigh
        expr: rate(learning_stage_failures_total[5m]) > 0.05
        labels:
          severity: critical
        annotations:
          summary: "Stage failure rate high for {{ $labels.stage_type }}"

      # Cache performance alerts
      - alert: CacheHitRateLow
        expr: learning_cache_hit_rate < 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Learning cache hit rate below threshold"
```

## Troubleshooting

### Common Issues

#### High Queue Backlog

- Check provider health
- Verify agent availability
- Increase `MAX_PARALLEL_JOBS`
- Check for stuck jobs

**Solution:**

```python
# Monitor queue
dashboard = LearningDashboard()
queue = dashboard.get_queue()
avg_wait = sum(item.queued_at for item in queue) / len(queue)
if avg_wait > 300:  # > 5 minutes
    # Investigate provider health
    provider_health = dashboard.get_provider_health()
    for name, health in provider_health.items():
        if health.status != ProviderHealthStatus.HEALTHY:
            # Increase retry or switch to fallback
```

#### Low Provider Success Rate

- Check API credentials
- Verify rate limits not exceeded
- Check provider status page
- Review error logs for specific errors

**Solution:**

```python
# Get provider latency
metrics = OperationalMetricsAggregator()
stats = metrics.get_provider_latency_stats("youtube")
if stats["success_rate"] < 0.85:
    # Switch to fallback provider
    selection = CapabilityBasedProviderSelector()
    alt_provider = selection.select_provider(context, caps, providers)
```

#### Cache Misses

- Check TTL configuration
- Verify cache size adequate
- Monitor cache evictions
- Check cache invalidation logic

**Solution:**

```python
# Monitor cache
cache = RecommendationCacheManager()
stats = cache.get_stats()
print(f"Hit rate: {stats['valid_entries'] / stats['total_entries']}")
if hit_rate < 0.3:
    # Increase TTL or cache size
    cache = RecommendationCacheManager(ttl_minutes=120, max_entries=2000)
```

#### Slow Stage Execution

- Check provider latency
- Profile agent execution
- Verify parallelization working
- Check M8 queue health

**Solution:**

```python
# Analyze stage durations
stats = metrics.get_stage_duration_stats("retrieve_metrics")
print(f"Avg: {stats['avg_ms']:.0f}ms")
print(f"Max: {stats['max_ms']:.0f}ms")
if stats["avg_ms"] > 1000:
    # Enable parallel collection
    collector = ParallelAnalyticsCollector(max_parallel=10)
```

## Performance Tuning

### Queue Optimization

```python
# Adjust based on job characteristics
optimizer = QueueOptimizer(max_parallel_jobs=20)

# Monitor active jobs
active = optimizer.get_active_count()
if active < max_parallel_jobs:
    # Process more jobs
    can_process = optimizer.should_process_immediately(job_id, priority)
```

### Cache Tuning

```python
# Adjust TTL based on recommendation staleness tolerance
cache = RecommendationCacheManager(
    ttl_minutes=120,      # Recommendations valid for 2 hours
    max_entries=5000      # Cache up to 5000 results
)

# Monitor cache efficiency
stats = cache.get_stats()
print(f"Capacity used: {stats['capacity_used_percent']:.1f}%")
```

### Provider Selection

```python
# Tune capability negotiation
selector = CapabilityBasedProviderSelector()
selection = selector.select_provider(
    context,
    ("video_metrics", "retention_curve"),  # Required capabilities
    providers
)
# Use fallback if primary fails
if not primary_success:
    use_provider(selection.fallback_provider)
```

## Backup & Recovery

### State Backup

1. **Creator Profiles**: Backup `LearningMemory` periodically
2. **Metrics History**: Archive `OperationalMetricsAggregator` snapshots
3. **Learning Queue**: Persist queue to durable store

### Recovery Procedures

**Provider Failure:**

1. Automatic fallback to fallback_provider
2. If fallback unavailable, queue job for retry
3. Alert on-call team

**Queue Corruption:**

1. Restart queue from persistent store
2. Mark in-progress jobs as failed
3. Retry failed jobs

**Metrics Loss:**

1. Restart metrics aggregation
2. Query providers for historical data
3. Rebuild metrics windows

## Compliance & Security

### Data Privacy

- Ensure provider credentials not logged
- Use environment variables for secrets
- Implement audit logging for data access
- Respect creator privacy settings

### Rate Limiting

- Monitor provider rate limits
- Implement backoff strategies
- Use queue to smooth traffic
- Set per-creator rate limits

### Access Control

- Restrict dashboard access to operations team
- Audit all dashboard access
- Implement API key rotation
- Validate provider credentials

## Disaster Recovery

### RTO/RPO Targets

- **RTO** (Recovery Time): < 15 minutes
- **RPO** (Recovery Point): < 5 minutes

### Recovery Steps

1. Verify M8 task graph available
2. Restart learning orchestration
3. Rebuild queue from persistent store
4. Reinitialize provider registry
5. Restore dashboard state
6. Resume job execution

### Testing

- Monthly disaster recovery drills
- Automated backup verification
- Failover testing to secondary region
- Metrics recovery validation

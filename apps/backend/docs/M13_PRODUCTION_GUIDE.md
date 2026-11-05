# M13: Publishing & Distribution Platform — Production Guide

## Deployment Checklist

### Before Going Live

**Environment Variables**

```bash
# Required for all providers
export VITE_API_BASE_URL="https://api.aura.io/api"
export JWT_SECRET="<32+ char key>"

# YouTube provider
export YOUTUBE_CLIENT_ID="<your-client-id>"
export YOUTUBE_CLIENT_SECRET="<your-client-secret>"
export YOUTUBE_REFRESH_TOKEN="<refresh-token>"

# TikTok provider
export TIKTOK_CLIENT_ID="<client-id>"
export TIKTOK_CLIENT_SECRET="<client-secret>"

# Instagram / Meta provider
export META_ACCESS_TOKEN="<access-token>"

# LinkedIn provider
export LINKEDIN_ACCESS_TOKEN="<access-token>"

# Retry policy
export PUBLISH_MAX_RETRIES="3"
export PUBLISH_RETRY_STRATEGY="exponential"  # fixed, linear, exponential
export PUBLISH_BASE_RETRY_DELAY_SECONDS="1"

# Metrics
export METRICS_RETENTION_HOURS="24"
export METRICS_CLEANUP_INTERVAL_HOURS="1"

# Dashboard
export DASHBOARD_QUEUE_UPDATE_INTERVAL_SECONDS="5"
export DASHBOARD_PROVIDER_HEALTH_CHECK_INTERVAL_SECONDS="30"
```

### Provider Setup

**YouTube:**

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Add redirect URI: `https://api.aura.io/callbacks/youtube`
3. Set `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`

**TikTok:**

1. Register app in TikTok Developer Console
2. Request Business API access
3. Set `TIKTOK_CLIENT_ID`, `TIKTOK_CLIENT_SECRET`

**Instagram / Meta:**

1. Create Facebook App
2. Get long-lived access token
3. Set `META_ACCESS_TOKEN`

**LinkedIn:**

1. Create LinkedIn App
2. Get access token with `w_member_social` scope
3. Set `LINKEDIN_ACCESS_TOKEN`

### Health Checks

```python
# Check provider availability
GET /api/publishing/health/providers

# Response:
{
  "providers": {
    "youtube": {"available": true, "latency_ms": 45},
    "tiktok": {"available": true, "latency_ms": 120},
    "instagram": {"available": false, "latency_ms": 5000},
    "linkedin": {"available": true, "latency_ms": 80}
  }
}
```

---

## Provider Selection Strategy

**Automatic Selection (Score-based)**

Each provider has a score: `success_rate * 100 - avg_duration_seconds`

Example:

- YouTube: 98% success, 15s avg = 9800 - 15 = **9785**
- TikTok: 95% success, 20s avg = 9500 - 20 = **9480** ← pick YouTube
- Mock: 100% success, 1s avg = 10000 - 1 = **9999** ← fallback only

```python
from aura_backend.publishing import PerformanceOptimizer

provider_metrics = {
    "youtube": {"success_rate": 98.0, "avg_duration": 15.0},
    "tiktok": {"success_rate": 95.0, "avg_duration": 20.0},
}

best = PerformanceOptimizer.select_best_provider(
    platforms=["youtube", "tiktok"],
    provider_metrics=provider_metrics,
)
# Returns: "youtube"
```

---

## Failure Handling

### Retry Policy

**Default Retry Configuration**

```
Max retries: 3
Strategy: Exponential backoff
Base delay: 1 second
Backoff: 1s → 2s → 4s → (give up)
```

**Retryable Errors**

- Network timeout
- Rate limit (429)
- Temporary server error (5xx)
- Authentication refresh needed

**Non-Retryable Errors**

- Invalid video format
- Unsupported codec
- Metadata validation failed
- Account suspended

### Fallback Strategy

When a provider fails:

1. **Check if retryable** (retry_count < max_retries)
   - Yes → retry with backoff
   - No → fallback

2. **Try fallback provider**
   - If configured → use fallback
   - If none available → mark job as failed

3. **Example Fallback Chain**
   ```
   Primary: YouTube
   Fallback 1: TikTok
   Fallback 2: Mock (always succeeds)
   ```

### Recovery via Dashboard

```python
from aura_backend.publishing import PublishingDashboard, MetricsAggregator

aggregator = MetricsAggregator()
dashboard = PublishingDashboard(aggregator)

# Get failed jobs
failed_jobs = dashboard.get_retry_queue()

# Retry specific job
dashboard.retry_job(job_id="job-123")

# Batch retry with different provider
dashboard.retry_batch(provider_override="mock")
```

---

## Configuration & Tuning

### Parallel Execution

```python
from aura_backend.publishing import PerformanceOptimizer

# Queue has 100 jobs, system supports 4 concurrent
parallel_jobs = PerformanceOptimizer.calculate_parallel_jobs(
    queue_depth=100,
    max_concurrent=4,
)
# Returns: 4
```

### Queue Optimization

```python
# Estimate time to clear queue
time_needed = PerformanceOptimizer.estimate_queue_clearance(
    queue_depth=100,
    avg_duration_seconds=15.0,
    concurrent_jobs=4,
)
# Returns: 375.0 seconds (100 jobs / 4 parallel * 15s per job)
```

### Metrics Retention

```bash
# Adjust retention based on storage/performance needs
METRICS_RETENTION_HOURS=24      # Default: 1 day
METRICS_RETENTION_HOURS=168     # Extended: 1 week
METRICS_RETENTION_HOURS=720     # Long-term: 30 days
```

Old metrics are automatically purged.

---

## Scaling Considerations

### Horizontal Scaling

M13 is stateless and scales linearly:

```
1 instance: ~10 jobs/hour
2 instances: ~20 jobs/hour
4 instances: ~40 jobs/hour
```

**Load balancing**: Round-robin across instances (no sticky sessions needed)

### Rate Limits by Provider

| Provider  | Limit            | Strategy                                 |
| --------- | ---------------- | ---------------------------------------- |
| YouTube   | 10,000 quota/day | Distribute across day; use batch uploads |
| TikTok    | 1,000 req/min    | Queue rate limiting; batch when possible |
| Instagram | 500 req/min      | Space out parallel jobs                  |
| LinkedIn  | 100 req/min      | Serialize LinkedIn jobs                  |

### Queue Depth Targets

| Throughput Goal | Queue Target | Max Parallel |
| --------------- | ------------ | ------------ |
| 10 jobs/hour    | 20           | 2            |
| 50 jobs/hour    | 100          | 4            |
| 100 jobs/hour   | 200          | 8            |
| 500 jobs/hour   | 1000         | 16           |

---

## Monitoring

### Key Metrics to Watch

```python
from aura_backend.publishing import MetricsAggregator

aggregator = MetricsAggregator()

# Throughput
throughput = aggregator.get_throughput_metrics()
print(f"Jobs/hour: {throughput.jobs_per_hour}")

# Success rate
failure_rate = aggregator.get_failure_rate()
if failure_rate > 5.0:
    alert("Failure rate exceeding 5%")

# Provider health
youtube_metrics = aggregator.get_provider_metrics("youtube")
if youtube_metrics.success_rate < 90.0:
    alert("YouTube success rate below 90%")

# Retry efficiency
retry_stats = aggregator.get_retry_statistics()
if retry_stats["avg"] > 1.5:
    alert("High retry rate: avg retries > 1.5")
```

### Alerting Thresholds

| Metric               | Alert Level | Action                                  |
| -------------------- | ----------- | --------------------------------------- |
| Failure rate > 10%   | Critical    | Pause publishing; investigate provider  |
| Provider unavailable | Warning     | Switch to fallback; notify DevOps       |
| Queue depth > 1000   | Info        | Monitor; scale if trend continues       |
| Retry rate > 30%     | Warning     | Review transient errors; adjust backoff |
| API latency > 1s     | Info        | Monitor; may indicate provider issues   |

---

## Disaster Recovery

### Provider Outage

```
Scenario: YouTube goes down (429 Rate Limit Errors)

1. MetricsAggregator detects 429 errors
2. PerformanceOptimizer scores YouTube = negative
3. Dashboard alerts about provider unavailability
4. New jobs automatically route to TikTok/Instagram/Mock
5. YouTube jobs auto-retry with fallback enabled
6. When YouTube recovers, jobs resume normal flow
```

### Failed Jobs Queue

```python
# Retrieve failed jobs
failed = dashboard.get_failed_jobs_queue()

# Retry all with mock provider
dashboard.retry_batch(
    job_ids=[j.id for j in failed],
    provider_override="mock",
)
```

### Metrics Data Loss

```
Retention: 24 hours (default)
Recovery: Historical metrics in dashboard available until cleanup
Action: Export metrics before retention expires (if needed)
```

---

## Performance Tuning

### Optimize for Throughput (High-Volume)

```python
# Configuration
PUBLISH_MAX_RETRIES = 2           # Fail fast
PUBLISH_RETRY_STRATEGY = "linear" # Faster recovery
METRICS_RETENTION_HOURS = 6       # Less storage

# Scaling
max_concurrent = 16               # Max parallelization
batch_size = 50                   # Batch uploads
```

### Optimize for Reliability (Mission-Critical)

```python
# Configuration
PUBLISH_MAX_RETRIES = 5           # More attempts
PUBLISH_RETRY_STRATEGY = "exponential"  # Careful backoff
METRICS_RETENTION_HOURS = 168     # 1 week for analysis

# Scaling
max_concurrent = 4                # Careful parallelization
batch_size = 1                    # Individual uploads
```

---

## Maintenance

### Daily

- Monitor dashboard for queue depth
- Check provider health status
- Review failure logs

### Weekly

- Analyze throughput trends
- Review retry statistics
- Update provider credentials if needed

### Monthly

- Audit provider costs
- Review and optimize rate limit usage
- Analyze provider performance comparisons

---

## Emergency Procedures

### Kill Switch

```python
# Pause all publishing
PUBLISH_ENABLED = False

# Resume
PUBLISH_ENABLED = True
```

### Manual Provider Override

```bash
# Force all jobs to use Mock provider
PUBLISH_FORCE_PROVIDER="mock"
```

### Queue Drain

```python
# Process entire queue as fast as safely possible
max_concurrent = 32
batch_size = 100
METRICS_RETENTION_HOURS = 1  # Reduce storage usage
```

---

## Cost Optimization

### Provider Selection

- **YouTube**: Highest quality (16:9, 12h), higher latency
- **TikTok**: Fast uploads (9:16, 10m), rate limits apply
- **Mock**: Zero cost (testing), always available

**Strategy**: Use Mock for development/testing; YouTube/TikTok for production

### Batch Publishing

```python
# Instead of individual uploads
for job in jobs:
    publish_job(job)  # Slow, many API calls

# Batch uploads
publish_batch(jobs)  # Faster, fewer API calls
```

### Retry Optimization

```
High retry rate → more API calls → higher costs
Optimize by:
  1. Increase backoff delay (fewer retries)
  2. Improve network reliability
  3. Validate content before publishing
```

---

## Support

**Issues / Questions:**

1. Check [M13_OPERATIONS_GUIDE.md](./M13_OPERATIONS_GUIDE.md) for troubleshooting
2. Review [M13_BENCHMARKS.md](./M13_BENCHMARKS.md) for performance baseline
3. Check provider API documentation
4. Check application logs for detailed error messages

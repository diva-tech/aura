# M13: Publishing & Distribution Platform — Operations Guide

## Monitoring Dashboard

### Real-Time Queue Visualization

```python
from aura_backend.publishing import PublishingDashboard, MetricsAggregator

aggregator = MetricsAggregator()
dashboard = PublishingDashboard(aggregator)

# Get full dashboard summary
summary = dashboard.get_dashboard_summary()

print(summary)
# {
#   "summary": {
#     "period": "1 hour",
#     "jobs_completed": 45,
#     "throughput_per_hour": 45,
#     "failure_rate_percent": 2.2,
#     "avg_retries": 0.5,
#     "total_retries": 23
#   },
#   "queue": {
#     "queued_jobs": 12,
#     "active_jobs": 4,
#     "avg_wait_seconds": 120
#   },
#   "providers": {
#     "youtube": {
#       "status": "available",
#       "success_rate": 98.5,
#       "avg_duration": 15.2,
#       "queue_depth": 2
#     },
#     "tiktok": {
#       "status": "available",
#       "success_rate": 96.0,
#       "avg_duration": 12.0,
#       "queue_depth": 1
#     }
#   },
#   "active_jobs": 4
# }
```

### Job Progress Tracking

```python
# Register job for tracking
dashboard.register_job(job_id="job-123", platforms=["youtube", "tiktok"])

# Get job progress
progress = dashboard.get_job_progress("job-123")

print(progress)
# JobProgress(
#   job_id="job-123",
#   total_stages=14,        # 2 platforms × 7 stages each
#   completed_stages=5,
#   failed_stages=0,
#   progress_percent=35.7,
#   estimated_remaining_seconds=180
# )
```

---

## Health Checks

### Provider Health Status

```bash
# Check provider availability
curl http://localhost:8080/api/publishing/health/providers

# Response:
{
  "providers": {
    "youtube": {
      "available": true,
      "latency_ms": 45,
      "last_check": "2024-01-15T10:30:00Z",
      "success_rate": 98.5
    },
    "tiktok": {
      "available": true,
      "latency_ms": 120,
      "last_check": "2024-01-15T10:30:00Z",
      "success_rate": 96.0
    },
    "instagram": {
      "available": false,
      "latency_ms": 5000,
      "last_check": "2024-01-15T10:30:00Z",
      "error": "Connection timeout"
    }
  }
}
```

### Application Health

```bash
# Full health check
curl http://localhost:8080/health

# Response:
{
  "status": "UP",
  "services": {
    "publishing": "UP",
    "metrics": "UP",
    "database": "UP",
    "cache": "UP"
  }
}
```

---

## Troubleshooting Playbook

### Issue: High Failure Rate (> 10%)

**Diagnosis**

```python
from aura_backend.publishing import MetricsAggregator

aggregator = MetricsAggregator()
failure_rate = aggregator.get_failure_rate()

if failure_rate > 10.0:
    # Get provider breakdown
    for provider in ["youtube", "tiktok", "instagram"]:
        metrics = aggregator.get_provider_metrics(provider)
        print(f"{provider}: {metrics.success_rate}% success")
```

**Common Causes & Fixes**

| Cause                   | Symptom           | Fix                                           |
| ----------------------- | ----------------- | --------------------------------------------- |
| Provider API rate limit | 429 errors        | Reduce parallelization; space out jobs        |
| Invalid credentials     | 401 errors        | Refresh tokens (YouTube); check access tokens |
| Network connectivity    | Timeout errors    | Check network; verify VPN if needed           |
| Invalid video format    | Validation errors | Check artifact format matches profile specs   |
| Provider account issues | Quota exceeded    | Review provider account limits                |

### Issue: Provider Unavailable

**Diagnosis**

```python
provider_metrics = aggregator.get_provider_metrics("youtube")

if provider_metrics.success_rate < 50.0:
    print("YouTube is unreliable or unavailable")

    # Check latest failures
    recent_failures = aggregator.get_recent_failures(limit=10)
    for failure in recent_failures:
        print(f"  Error: {failure['error_message']}")
        print(f"  Recoverable: {failure['is_recoverable']}")
```

**Action**

```python
# Option 1: Automatically use fallback
dashboard.register_job("job-123", ["youtube"], fallback_provider="tiktok")

# Option 2: Pause publishing to this provider
DISABLED_PROVIDERS = ["youtube"]

# Option 3: Retry with exponential backoff
dashboard.retry_job("job-123", strategy="exponential")
```

### Issue: Queue Backup (> 1000 jobs)

**Diagnosis**

```python
queue_status = dashboard.get_queue_status()

if queue_status["queued_jobs"] > 1000:
    # Estimate clear time
    throughput = aggregator.get_throughput_metrics()
    jobs_per_second = throughput.jobs_per_hour / 3600
    clear_time_seconds = queue_status["queued_jobs"] / jobs_per_second
    print(f"Queue will clear in {clear_time_seconds / 3600:.1f} hours")
```

**Action**

```python
from aura_backend.publishing import PerformanceOptimizer

# Increase parallelization
parallel = PerformanceOptimizer.calculate_parallel_jobs(
    queue_depth=1000,
    max_concurrent=16,  # Increase from 4
)

# Scale horizontally (add instances)
# Each instance adds ~10 jobs/hour throughput
```

### Issue: Slow Job Completion (> 60 seconds)

**Diagnosis**

```python
# Check stage-by-stage duration
job_progress = dashboard.get_job_progress("job-123")

if job_progress.estimated_remaining_seconds > 600:
    # Get provider latency
    provider_metrics = aggregator.get_provider_metrics("youtube")
    print(f"YouTube avg duration: {provider_metrics.avg_upload_seconds}s")

    # Check queue wait time
    queue_status = dashboard.get_queue_status()
    print(f"Queue wait time: {queue_status['avg_wait_seconds']}s")
```

**Action**

| Symptom                   | Cause               | Fix                                   |
| ------------------------- | ------------------- | ------------------------------------- |
| Provider latency > 20s    | Provider slowness   | Switch to faster provider             |
| Queue wait > 60s          | Queue backup        | Scale up parallel execution           |
| Per-stage time increasing | Resource contention | Add instances; reduce concurrent jobs |

### Issue: High Retry Rate (> 30%)

**Diagnosis**

```python
retry_stats = aggregator.get_retry_statistics()

if retry_stats["avg"] > 0.3:
    print(f"High retry rate: {retry_stats['avg']} retries per job")

    # Analyze retry causes
    for failure in aggregator.get_recent_failures():
        if failure["retry_count"] > 0:
            print(f"  Error: {failure['error_message']}")
```

**Action**

| Cause                    | Fix                                    |
| ------------------------ | -------------------------------------- |
| Transient network errors | No action (auto-retry working)         |
| Rate limits (429)        | Increase backoff delay                 |
| Timeout errors           | Increase timeout; reduce parallel jobs |
| Invalid content          | Improve validation before publishing   |

---

## Capacity Planning

### Resource Allocation

```python
from aura_backend.publishing import PerformanceOptimizer

# Estimate resource needs for target throughput
target_jobs_per_hour = 100
jobs_per_instance = 10

instances_needed = target_jobs_per_hour / jobs_per_instance
# Returns: 10 instances

# Database connections
# Rule of thumb: max_concurrent_jobs * 2
max_concurrent = 8
db_connections = max_concurrent * 2  # 16 connections
```

### Storage for Metrics

```
Default retention: 24 hours

Per job metrics:
- ~500 bytes per job record
- ~200 bytes per failure record

Estimated storage:
- 100 jobs/hour * 24 hours * 500 bytes = 1.2 MB/day
- Failure records: ~5% * 100 * 24 * 200 = 0.24 MB/day

Total: ~1.5 MB/day (trivial)
```

### Network Bandwidth

```
Per job estimate:
- Upload artifact: ~10-100 MB (provider-dependent)
- Metadata API calls: ~100 KB
- Webhook callbacks: ~10 KB

Estimated bandwidth:
- 100 jobs/hour * 50 MB average = 5 GB/hour
```

---

## Disaster Recovery

### Backup & Restore

**What to Backup**

- Publishing job history (in database)
- Provider credentials (encrypted in secrets manager)
- Metrics aggregates (if retention > 1 day)
- Dashboard state (ephemeral, not critical)

**Restore Procedure**

```python
# 1. Restore database
restore_db_from_backup()

# 2. Restore credentials
restore_secrets_from_vault()

# 3. Verify provider connectivity
check_provider_health()

# 4. Replay failed jobs from history
failed_jobs = query_db("SELECT * FROM publishing_jobs WHERE status = 'FAILED'")
for job in failed_jobs:
    dashboard.retry_job(job.id, strategy="exponential")
```

### Incident Recovery

**Scenario: Database corruption**

1. Stop publishing (set `PUBLISH_ENABLED=false`)
2. Restore database to last clean backup
3. Query job history to identify lost jobs
4. Resubmit lost jobs to queue
5. Resume publishing (set `PUBLISH_ENABLED=true`)

**Scenario: All providers down**

1. Redirect jobs to Mock provider (for testing/staging)
2. Queue jobs locally; retry when providers recover
3. Escalate to provider support teams
4. Monitor provider status pages

**Scenario: Credentials compromised**

1. Revoke all API tokens immediately
2. Generate new credentials from each provider
3. Update secrets manager
4. Restart application
5. Audit recently published content

---

## Log Analysis

### Key Log Patterns

**Success Pattern**

```
[INFO] Publishing job started: job-123
[INFO] Stage VALIDATE completed in 0.5s
[INFO] Stage UPLOAD completed in 15.2s
[INFO] Stage PUBLISH completed in 2.1s
[INFO] Publishing job completed: job-123 (success)
```

**Failure Pattern**

```
[ERROR] Stage UPLOAD failed: Connection timeout
[WARN] Retrying with exponential backoff (retry 1/3)
[ERROR] Stage UPLOAD failed again: Rate limit exceeded
[WARN] Retrying with exponential backoff (retry 2/3)
[ERROR] Stage UPLOAD failed (max retries exceeded)
[ERROR] Publishing job failed: job-123 (recovery: fallback to tiktok)
```

**Performance Pattern**

```
[WARN] Job queue depth: 150 (increasing)
[WARN] YouTube success rate: 85% (below threshold)
[INFO] Redirecting new jobs to TikTok
[INFO] Queue depth stabilizing: 120 (decreasing)
```

### Extracting Metrics from Logs

```bash
# Count failures by provider
grep "Stage.*FAILED" logs.txt | grep -o "provider: [a-z]*" | sort | uniq -c

# Find slow stages
grep "completed in" logs.txt | awk '{print $NF}' | sort -rn | head -20

# Count retries
grep "Retrying" logs.txt | wc -l

# Identify error types
grep "ERROR" logs.txt | grep -o "\\[[A-Z_]*\\]" | sort | uniq -c
```

---

## Performance Tuning Checklist

- [ ] **Database**: Connection pool size matches concurrent jobs × 2
- [ ] **Network**: CDN configured for artifact delivery
- [ ] **Caching**: Provider capabilities cached (TTL: 1 hour)
- [ ] **Rate Limits**: Backoff strategy matches provider limits
- [ ] **Parallelization**: Concurrent jobs tuned to provider limits
- [ ] **Metrics**: Retention hours matches operational needs
- [ ] **Monitoring**: Alerts configured for key metrics
- [ ] **Credentials**: Tokens rotated on schedule

---

## Scheduled Maintenance

### Daily (Automated)

- Metrics cleanup (keep 24 hours)
- Failed job analysis
- Provider health check

### Weekly

- Review performance trends
- Audit provider rate limits
- Check for hung jobs

### Monthly

- Refresh provider credentials
- Update provider API versions
- Optimize retry strategies

### Quarterly

- Capacity planning review
- Cost analysis by provider
- Security audit

---

## Emergency Contacts

**Provider Support**

- YouTube: support.google.com/youtube
- TikTok: tiktok.com/creators/help/request
- Meta (Instagram): help.instagram.com
- LinkedIn: linkedin.com/help

**Internal**

- Publishing Team: #m13-publishing Slack
- DevOps: #devops Slack
- On-call Runbook: https://runbooks.internal/m13

---

## Quick Reference

### Common Commands

```python
# Get dashboard summary
dashboard.get_dashboard_summary()

# Retry failed job
dashboard.retry_job("job-id")

# Check provider health
aggregator.get_provider_metrics("youtube")

# Get queue status
dashboard.get_queue_status()

# Clear metrics
aggregator._metrics_history.clear()

# Pause publishing
PUBLISH_ENABLED = False
```

### Key Files

- Source: `src/aura_backend/publishing/`
- Tests: `tests/publishing/`
- Docs: `docs/M13_*.md`
- Config: `application.yml` (Spring profiles)

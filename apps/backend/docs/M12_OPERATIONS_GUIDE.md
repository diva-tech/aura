# Milestone 12: Rendering Engine — Operations Guide

## Daily Operations

### Health Checks

**Every 1 hour:**

```bash
# Check rendering throughput
curl -s http://localhost:8080/api/metrics/rendering/throughput | jq .

# Check provider status
curl -s http://localhost:8080/api/metrics/rendering/providers | jq .

# Check failure rate
curl -s http://localhost:8080/api/metrics/rendering/failures | jq '.failure_rate_percent'
```

**If failure rate > 5%:**

1. Check disk space: `df -h /var/lib/rendering`
2. Check memory: `free -h`
3. Check provider availability: `ffmpeg -version`
4. Review recent StageFailed events in logs

**If throughput drops:**

1. Check M8 Task Orchestration queue depth: `curl -s http://localhost:8080/api/tasks/queue`
2. Check system load: `uptime`
3. Check network connectivity to storage
4. Review performance metrics by stage type

### Monitoring Dashboard

Access real-time dashboard at `http://localhost:8080/rendering/dashboard`

**Key metrics to watch:**

- **Completion Rate:** Should stay near 95%+
- **Avg Duration:** Track trends (increasing = degrading performance)
- **Memory Usage:** Should not exceed 80% of system RAM
- **Retry Rate:** Should stay below 10%

### Alerts to Set Up

```
threshold.rendering.failure_rate > 5%
→ CRITICAL: Page oncall
→ Action: Check "High Failure Rate" below

threshold.rendering.throughput_jobs_per_hour < 10
→ WARNING: Notify team
→ Action: Check "Low Throughput" below

threshold.rendering.avg_duration_seconds > 300
→ WARNING: Notify team
→ Action: Check "Slow Rendering" below

threshold.rendering.memory_percent > 85%
→ WARNING: Page oncall
→ Action: Check "Memory Exhaustion" below
```

## Troubleshooting Playbooks

### High Failure Rate (> 5%)

**Investigation:**

1. **Check error patterns:**

   ```bash
   tail -1000 logs/app.log | grep "StageFailed" | jq '.error_message' | sort | uniq -c | sort -rn
   ```

2. **Identify failing stage type:**

   ```bash
   tail -1000 logs/app.log | grep "StageFailed" | jq '.stage_type' | sort | uniq -c
   ```

3. **Check provider involved:**
   ```bash
   tail -1000 logs/app.log | grep "StageFailed" | jq '.provider_name' | sort | uniq -c
   ```

**Resolution by error type:**

| Error                        | Cause                     | Fix                                         |
| ---------------------------- | ------------------------- | ------------------------------------------- |
| "Out of memory"              | System RAM exhausted      | Scale horizontally or reduce clip count     |
| "Disk full"                  | `/var/lib/rendering` full | `df -h`, clear temp artifacts               |
| "ffmpeg not found"           | Provider unavailable      | `apt-get install ffmpeg`                    |
| "Codec not supported"        | FFmpeg build lacks codec  | Rebuild FFmpeg with additional codecs       |
| "Timeout waiting for output" | Video too long/complex    | Increase timeout or split into smaller jobs |

**If failures localized to one provider:**

```python
# Temporarily disable failing provider
LANDREGISTRY_RENDERER_DISABLED_PROVIDERS=ffmpeg
# Rendering will automatically fallback to mock
```

### Low Throughput (< 10 jobs/hour)

**Investigation:**

1. **Check queue depth:**

   ```bash
   curl -s http://localhost:8080/api/tasks/queue | jq '.pending_count'
   ```

2. **Check M8 orchestration status:**

   ```bash
   curl -s http://localhost:8080/api/orchestration/status | jq '.agents_available'
   ```

3. **Check system resources:**
   ```bash
   top -n 1 | head -20  # CPU and memory
   iostat -x 1 5       # Disk I/O
   ```

**Resolution:**

| Cause           | Fix                                                         |
| --------------- | ----------------------------------------------------------- |
| Queue backed up | Scale M8 workers (increase ORCHESTRATION_WORKER_COUNT)      |
| High CPU usage  | Reduce parallel stages (lower RENDERER_MAX_PARALLEL_STAGES) |
| High disk I/O   | Enable artifact caching (RENDERER_CACHE_ARTIFACTS=true)     |
| Provider busy   | Switch to faster provider (mock for testing, GPU for prod)  |

### Slow Rendering (avg duration > 300s)

**Investigation:**

1. **Check breakdown by stage:**

   ```bash
   curl -s http://localhost:8080/api/metrics/rendering/by-stage | jq '.stages | sort_by(.avg_duration)'
   ```

2. **Identify bottleneck stage:**

   ```
   Output shows which stage is slowest (e.g., "composite" = 150s avg)
   ```

3. **Check provider efficiency:**
   ```bash
   curl -s http://localhost:8080/api/metrics/rendering/providers | jq '.[] | {name, avg_duration}'
   ```

**Resolution:**

| Bottleneck       | Fix                                                     |
| ---------------- | ------------------------------------------------------- |
| CLIP_RENDER slow | Use FFmpeg provider with GPU enabled                    |
| COMPOSITE slow   | Check resolution/bitrate; try lower quality preset      |
| SUBTITLE slow    | May not support subtitles—use mock for testing          |
| EXPORT slow      | Reduce bitrate or use H.264 instead of H.265            |
| OVERALL slow     | Enable parallelism (multiple stages run simultaneously) |

### Memory Exhaustion (> 85%)

**Investigation:**

1. **Check memory by provider:**

   ```bash
   curl -s http://localhost:8080/api/metrics/rendering/memory | jq '.by_provider'
   ```

2. **Check current running jobs:**

   ```bash
   curl -s http://localhost:8080/api/rendering/jobs/running | jq '.[] | {job_id, clip_count, duration}'
   ```

3. **Check OS memory:**
   ```bash
   free -h
   ps aux | grep java | grep rendering
   ```

**Resolution:**

| Action                                             | Impact                                     |
| -------------------------------------------------- | ------------------------------------------ |
| Reduce `LANDREGISTRY_RENDERER_GPU_MEMORY_LIMIT_MB` | Lower peak usage but slower GPU rendering  |
| Reduce `ORCHESTRATION_MAX_PARALLEL_JOBS`           | Fewer concurrent jobs but lower throughput |
| Clear artifact cache                               | Recover disk space immediately             |
| Upgrade server RAM                                 | Permanent fix (if budget available)        |

**Immediate actions:**

```bash
# 1. Clear temp artifacts
rm -f /var/lib/rendering/tmp/*

# 2. Stop accepting new jobs (graceful degradation)
curl -X POST http://localhost:8080/api/rendering/pause

# 3. Wait for current jobs to complete (monitor progress)
watch -n 5 'curl -s http://localhost:8080/api/rendering/jobs/running | jq ".[] | .progress_percent"'

# 4. Resume when memory drops below 70%
curl -X POST http://localhost:8080/api/rendering/resume
```

## Capacity Planning

### Scaling Rendering

**Vertical scaling (more powerful machine):**

- Larger RAM (ffmpeg uses ~200MB per 1GB video)
- More cores (parallel stages scale with CPU count)
- GPU (H.265, AI effects)

**Horizontal scaling (multiple render workers):**

- Deploy M12 rendering pool on separate servers
- Use M8 Task Orchestration to distribute jobs
- Share artifact storage (NFS or S3)

**Configuration for 1000 jobs/hour:**

```bash
# 4-core machine, 16GB RAM
ORCHESTRATION_WORKER_COUNT=4
LANDREGISTRY_RENDERER_MAX_PARALLEL_JOBS=8
LANDREGISTRY_RENDERER_GPU_ENABLED=true
LANDREGISTRY_RENDERER_QUALITY_PRESET=medium

# Estimated: 4 workers × 15 jobs/hour = 60 jobs/hour per machine
# Need ~17 machines for 1000/hour (or scale vertically)
```

### Storage Planning

**Per job storage estimate:**

- Input clips: varies (1-100MB)
- Working storage: ~1.5x clip size during rendering
- Output artifact: ~2-10MB (depends on quality)
- Temporary files: cleaned up after completion

**Example: 1000 jobs/day, 5min avg duration:**

```
1000 jobs × 50MB avg = 50GB working storage
Peak (if all jobs overlap): 50GB × 4 concurrent = 200GB
→ Recommend 500GB fast storage (/var/lib/rendering)
→ 1TB for safety margin
```

## Disaster Recovery

### Backup Strategy

**Critical data:**

- RenderingMetrics (analytics)
- Provider configuration
- Custom provider implementations

**Non-critical (regenerable):**

- Temp artifacts (will be recreated)
- Cache files (will be re-cached)
- Job logs (archived separately)

**Backup script:**

```bash
#!/bin/bash
# Run daily via cron
BACKUP_DIR=/backups/rendering-$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Export metrics
curl -s http://localhost:8080/api/metrics/rendering/export > $BACKUP_DIR/metrics.json

# Backup config
cp -r app-backend/src/main/resources $BACKUP_DIR/config

# Backup custom providers (if any)
cp -r app-backend/src/main/java/in/gov/landrevenue/rendering/*.java $BACKUP_DIR/providers

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

### Recovery Procedures

**If rendering service crashes:**

1. Check logs: `tail -100 logs/app.log | grep "ERROR"`
2. Restart: `mvn spring-boot:run` (or systemd service)
3. Resume interrupted jobs: Dashboard will show them as pending
4. Verify recovery: Check failure rate drops back to baseline

**If artifact storage corrupted:**

1. Stop rendering: `curl -X POST http://localhost:8080/api/rendering/pause`
2. Check storage: `df -i /var/lib/rendering` (inode/block availability)
3. Restore from backup: `tar -xzf backups/rendering-YYYYMMDD.tar.gz`
4. Rerun failed jobs: Dashboard shows which jobs to retry

**If metrics database corrupted:**

1. Metrics are ephemeral (24-hour retention by default)
2. No action needed—metrics will rebuild within 24 hours
3. To preserve: Export before data loss via API

## Performance Tuning

### Optimization Checklist

- [ ] GPU enabled if available: `nvidia-smi`
- [ ] FFmpeg built with x265 support: `ffmpeg -codecs | grep hevc`
- [ ] CPU scaling disabled: `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
- [ ] Disk I/O optimized: `iostat` showing < 10% busy
- [ ] Network bandwidth sufficient: test `scp` speed
- [ ] Artifact cache enabled: `RENDERER_CACHE_ARTIFACTS=true`
- [ ] Parallel stages maximized: `RENDERER_MAX_PARALLEL_STAGES=4` or higher

### Provider-Specific Tuning

**FFmpeg (production):**

```bash
# Enable H.265 with 10-bit for better quality/smaller file
LANDREGISTRY_RENDERER_FFMPEG_PRESET=medium  # quality vs speed tradeoff
LANDREGISTRY_RENDERER_FFMPEG_CRF=23         # 0-51, lower = better (20-28 typical)
LANDREGISTRY_RENDERER_FFMPEG_SCALE_FILTER="-1:1080"  # max 1080p
```

**Mock (testing):**

```bash
# No tuning needed (instant)
# Use for: dry runs, EditPlan validation, CI/CD
```

## Capacity Trends

### Weekly Reporting

Every Monday, run:

```bash
#!/bin/bash
# Collect last 7 days of metrics
curl -s http://localhost:8080/api/metrics/rendering/weekly-summary | jq '
{
  jobs_completed: .jobs_completed,
  avg_duration_seconds: .avg_duration_seconds,
  failure_rate_percent: .failure_rate_percent,
  peak_concurrent_jobs: .peak_concurrent_jobs,
  total_cpu_hours: .total_cpu_hours,
  total_gpu_hours: (.gpu_usage_percent / 100),
  recommended_action: (
    if .failure_rate_percent > 5 then "Scale up or fix failures"
    elif .peak_concurrent_jobs > 8 then "Consider horizontal scaling"
    else "Stable"
    end
  )
}' > reports/rendering-$(date +%Y-W%V).json
```

Use trends to forecast capacity needs for next quarter.

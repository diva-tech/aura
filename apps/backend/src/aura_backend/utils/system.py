from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import psutil

from aura_backend.api.v1.schemas.health import HealthState, ResourceMetric


def get_gpu_metric() -> ResourceMetric:
    if shutil.which("nvidia-smi") is None:
        return ResourceMetric(
            status="unavailable",
            details={"reason": "nvidia-smi not available"},
        )

    try:
        command = [
            "nvidia-smi",
            "--query-gpu=memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
        raw_output = subprocess.check_output(
            command,
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
        total_memory, used_memory, utilization = [
            int(item.strip()) for item in raw_output.split(",")
        ]
        free_memory = total_memory - used_memory
        percent_used = round((used_memory / total_memory) * 100, 2) if total_memory else 0.0
        return ResourceMetric(
            status="healthy",
            total=total_memory,
            used=used_memory,
            free=free_memory,
            percent=percent_used,
            details={"utilization_percent": utilization},
        )
    except Exception as exc:
        return ResourceMetric(status="unhealthy", details={"reason": str(exc)})


def get_disk_metric(path: str) -> ResourceMetric:
    resolved_path = Path(path)
    usage = psutil.disk_usage(str(resolved_path))
    status: HealthState = "healthy" if usage.percent < 90 else "degraded"
    return ResourceMetric(
        status=status,
        total=usage.total,
        used=usage.used,
        free=usage.free,
        percent=usage.percent,
    )


def get_memory_metric() -> ResourceMetric:
    memory = psutil.virtual_memory()
    status: HealthState = "healthy" if memory.percent < 90 else "degraded"
    return ResourceMetric(
        status=status,
        total=memory.total,
        used=memory.used,
        free=memory.available,
        percent=memory.percent,
    )

"""
LLM Runtime Metrics.

Track requests, tokens, costs, latency, provider health.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import threading


@dataclass
class RequestMetrics:
    """Metrics for single request"""

    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    time_to_first_token_ms: Optional[int] = None
    estimated_cost: float = 0.0
    finish_reason: str = ""
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict"""
        return {
            "model": self.model,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "time_to_first_token_ms": self.time_to_first_token_ms,
            "estimated_cost": self.estimated_cost,
            "finish_reason": self.finish_reason,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsCollector:
    """Collect and aggregate LLM metrics"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics: list[RequestMetrics] = []
        self._lock = threading.Lock()
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._provider_stats: Dict[str, Dict[str, Any]] = {}

    def record(self, metrics: RequestMetrics) -> None:
        """Record request metrics"""
        with self._lock:
            self._metrics.append(metrics)
            if len(self._metrics) > self.max_history:
                self._metrics.pop(0)

            self._request_count += 1
            self._total_tokens += metrics.input_tokens + metrics.output_tokens
            self._total_cost += metrics.estimated_cost

            # Update provider stats
            if metrics.provider not in self._provider_stats:
                self._provider_stats[metrics.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0.0,
                    "avg_latency": 0,
                    "success_rate": 0.0,
                }

            stats = self._provider_stats[metrics.provider]
            stats["requests"] += 1
            stats["tokens"] += metrics.input_tokens + metrics.output_tokens
            stats["cost"] += metrics.estimated_cost
            stats["avg_latency"] = (stats["avg_latency"] * (stats["requests"] - 1) + metrics.latency_ms) / stats["requests"]

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        with self._lock:
            return {
                "total_requests": self._request_count,
                "total_tokens": self._total_tokens,
                "total_cost": self._total_cost,
                "provider_stats": self._provider_stats.copy(),
                "recent_requests": len(self._metrics),
            }

    def get_provider_stats(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get stats for specific provider"""
        with self._lock:
            return self._provider_stats.get(provider)

    def clear(self) -> None:
        """Clear all metrics"""
        with self._lock:
            self._metrics.clear()
            self._provider_stats.clear()
            self._request_count = 0
            self._total_tokens = 0
            self._total_cost = 0.0

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, generate_latest

request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

request_size = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    buckets=(100, 1000, 10000, 100000, 1000000),
)

response_size = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status"],
    buckets=(100, 1000, 10000, 100000, 1000000),
)

active_requests = Gauge(
    "http_requests_active",
    "Currently active HTTP requests",
)

exceptions_raised = Counter(
    "exceptions_raised_total",
    "Total exceptions raised",
    ["exception_type"],
)


class MetricsService:
    @staticmethod
    def get_metrics() -> bytes:
        return generate_latest()

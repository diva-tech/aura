"""M13 Phase 1: Publishing Foundation — Retry Policy.

Immutable retry policy for publishing failures.
"""

from dataclasses import dataclass
from enum import StrEnum


class RetryStrategy(StrEnum):
    """Retry strategy"""

    NONE = "none"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


class RetryableError(StrEnum):
    """Retryable error types"""

    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_SERVER_ERROR = "temporary_server_error"
    TRANSIENT_AUTH_ERROR = "transient_auth_error"
    RESOURCE_EXHAUSTED = "resource_exhausted"


@dataclass(frozen=True)
class RetryPolicy:
    """Immutable retry policy"""

    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    initial_delay_seconds: int = 1
    max_delay_seconds: int = 300
    backoff_multiplier: float = 2.0
    retryable_errors: tuple[RetryableError, ...] = (
        RetryableError.NETWORK_ERROR,
        RetryableError.TIMEOUT,
        RetryableError.RATE_LIMIT,
        RetryableError.TEMPORARY_SERVER_ERROR,
    )
    jitter_enabled: bool = True

    def should_retry(self, retry_count: int) -> bool:
        """Check if should retry"""
        if self.retry_strategy == RetryStrategy.NONE:
            return False
        return retry_count < self.max_retries

    def get_next_delay_seconds(self, retry_count: int) -> int:
        """Calculate delay for next retry"""
        if self.retry_strategy == RetryStrategy.NONE:
            return 0

        if self.retry_strategy == RetryStrategy.FIXED_DELAY:
            return self.initial_delay_seconds

        if self.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.initial_delay_seconds * (retry_count + 1)
            return min(delay, self.max_delay_seconds)

        if self.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = int(self.initial_delay_seconds * (self.backoff_multiplier**retry_count))
            return min(delay, self.max_delay_seconds)

        return self.initial_delay_seconds

    def is_retryable(self, error_type: str) -> bool:
        """Check if error is retryable"""
        try:
            error = RetryableError(error_type)
            return error in self.retryable_errors
        except ValueError:
            return False

    def to_dict(self) -> dict:
        return {
            "max_retries": self.max_retries,
            "retry_strategy": self.retry_strategy.value,
            "initial_delay_seconds": self.initial_delay_seconds,
            "max_delay_seconds": self.max_delay_seconds,
            "backoff_multiplier": self.backoff_multiplier,
            "jitter_enabled": self.jitter_enabled,
        }


# Built-in retry policies

DEFAULT_RETRY_POLICY = RetryPolicy(
    max_retries=3,
    retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    initial_delay_seconds=1,
    max_delay_seconds=300,
    backoff_multiplier=2.0,
    jitter_enabled=True,
)

AGGRESSIVE_RETRY_POLICY = RetryPolicy(
    max_retries=5,
    retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    initial_delay_seconds=1,
    max_delay_seconds=600,
    backoff_multiplier=1.5,
    jitter_enabled=True,
)

CONSERVATIVE_RETRY_POLICY = RetryPolicy(
    max_retries=2,
    retry_strategy=RetryStrategy.LINEAR_BACKOFF,
    initial_delay_seconds=5,
    max_delay_seconds=60,
    backoff_multiplier=1.0,
    jitter_enabled=False,
)

NO_RETRY_POLICY = RetryPolicy(
    max_retries=0,
    retry_strategy=RetryStrategy.NONE,
)

RATE_LIMIT_RETRY_POLICY = RetryPolicy(
    max_retries=10,
    retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    initial_delay_seconds=5,
    max_delay_seconds=1800,  # 30 minutes max
    backoff_multiplier=2.0,
    retryable_errors=(RetryableError.RATE_LIMIT,),
    jitter_enabled=True,
)

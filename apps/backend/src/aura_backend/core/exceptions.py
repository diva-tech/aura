from __future__ import annotations


class AuraError(Exception):
    def __init__(
        self,
        message: str,
        *,
        error_code: str,
        status_code: int,
        details: dict[str, str | int | float | bool | None] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class RateLimitExceededError(AuraError):
    def __init__(
        self,
        *,
        retry_after_seconds: int,
        scope: str,
    ) -> None:
        super().__init__(
            "Rate limit exceeded.",
            error_code="rate_limit_exceeded",
            status_code=429,
            details={
                "retry_after_seconds": retry_after_seconds,
                "scope": scope,
            },
        )

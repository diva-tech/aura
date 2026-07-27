from __future__ import annotations

import time
from collections.abc import MutableMapping
from math import ceil

from redis.asyncio import Redis

from aura_backend.config.logging import get_logger
from aura_backend.core.exceptions import RateLimitExceededError


class RateLimitService:
    def __init__(
        self,
        redis_client: Redis,
        *,
        requests: int,
        window_seconds: int,
    ) -> None:
        self._redis_client = redis_client
        self._requests = requests
        self._window_seconds = window_seconds
        self._logger = get_logger(__name__)
        self._fallback_store: MutableMapping[str, tuple[int, float]] = {}

    async def enforce(self, *, key: str, scope: str) -> None:
        try:
            allowed, retry_after_seconds = await self._check_redis(key)
        except Exception:
            self._logger.warning("rate_limit_redis_unavailable", extra={"scope": scope})
            allowed, retry_after_seconds = self._check_fallback(key)

        if not allowed:
            raise RateLimitExceededError(
                retry_after_seconds=retry_after_seconds,
                scope=scope,
            )

    async def _check_redis(self, key: str) -> tuple[bool, int]:
        namespaced_key = f"aura:rate-limit:{key}"
        current = await self._redis_client.incr(namespaced_key)
        if current == 1:
            await self._redis_client.expire(namespaced_key, self._window_seconds)

        ttl = await self._redis_client.ttl(namespaced_key)
        retry_after_seconds = max(ttl, 1)
        return current <= self._requests, retry_after_seconds

    def _check_fallback(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        count, window_started_at = self._fallback_store.get(key, (0, now))
        if now - window_started_at >= self._window_seconds:
            count = 0
            window_started_at = now

        count += 1
        self._fallback_store[key] = (count, window_started_at)
        retry_after_seconds = max(ceil(self._window_seconds - (now - window_started_at)), 1)
        return count <= self._requests, retry_after_seconds

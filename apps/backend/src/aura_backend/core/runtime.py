from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class RuntimeState:
    started_at: datetime
    version: str

    @classmethod
    def create(cls, version: str) -> RuntimeState:
        return cls(started_at=datetime.now(UTC), version=version)

    def uptime_seconds(self) -> float:
        return (datetime.now(UTC) - self.started_at).total_seconds()

from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from aura_backend.config.settings import Settings
from aura_backend.database.session import create_database_engine, create_session_factory


@dataclass(frozen=True)
class InfrastructureClients:
    database_engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis_client: Redis


async def create_infrastructure_clients(settings: Settings) -> InfrastructureClients:
    database_engine = create_database_engine(settings.database_url)
    session_factory = create_session_factory(database_engine)
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return InfrastructureClients(
        database_engine=database_engine,
        session_factory=session_factory,
        redis_client=redis_client,
    )


async def close_infrastructure_clients(clients: InfrastructureClients) -> None:
    await clients.redis_client.aclose()
    await clients.database_engine.dispose()

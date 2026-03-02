"""Shared dependency injection functions."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.adapters.persistence.session import get_db_session


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


# Database session dependency
async def _get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.

    Yields:
        AsyncSession: Database session.
    """
    async for session in get_db_session():
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(_get_db_session)]


# TODO: Add Redis client dependency when cache is implemented
# async def get_redis() -> AsyncGenerator[Redis, None]:
#     """Get Redis client.
#
#     Yields:
#         Redis: Redis client.
#     """
#     redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
#     try:
#         yield redis
#     finally:
#         await redis.close()
#
#
# RedisDep = Annotated[Redis, Depends(get_redis)]

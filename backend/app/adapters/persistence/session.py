"""Database session management.

Provides async SQLAlchemy session factory and dependency injection.
"""

from collections.abc import AsyncGenerator
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DEBUG,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection.

    Yields:
        AsyncSession: Database session.

    Example:
        As a FastAPI dependency:
        ```python
        @app.get("/")
        async def endpoint(session: DBSessionDep):
            result = await session.execute(select(Model))
            return result.scalars().all()
        ```
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_session_context() -> AsyncContextManager[AsyncSession]:
    """Get database session as a context manager.

    Returns:
        AsyncContextManager: Database session context manager.

    Example:
        ```python
        async with get_db_session_context() as session:
            result = await session.execute(select(Model))
        ```
    """
    return async_session_maker()


__all__ = [
    "engine",
    "async_session_maker",
    "get_db_session",
    "get_db_session_context",
]

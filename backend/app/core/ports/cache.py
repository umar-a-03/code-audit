"""Cache protocol (abstract interface).

Defines the contract for cache implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Cache(ABC, Generic[T]):
    """Cache protocol.

    All cache implementations (Redis, Memcached, in-memory) must implement this interface.
    """

    @abstractmethod
    async def get(self, key: str) -> T | None:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None.
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds.

        Returns:
            True if successful.
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            True if key was deleted.
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Cache key.

        Returns:
            True if key exists.
        """
        pass

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter.

        Args:
            key: Counter key.
            amount: Amount to increment.

        Returns:
            New counter value.
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if successful.
        """
        pass

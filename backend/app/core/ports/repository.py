"""Repository protocol (abstract interface).

Defines the contract that all repository implementations must follow.
This is part of the Hexagonal Architecture pattern.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

# Generic type for model entities
T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Base repository protocol.

    All repositories should implement this interface.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity.

        Args:
            entity: Entity to create.

        Returns:
            Created entity with ID.
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> T | None:
        """Get entity by ID.

        Args:
            id: Entity ID.

        Returns:
            Entity or None if not found.
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an entity.

        Args:
            entity: Entity to update.

        Returns:
            Updated entity.
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        """List entities with pagination and filters.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.
            filters: Filter criteria.

        Returns:
            List of entities.
        """
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count entities matching filters.

        Args:
            filters: Filter criteria.

        Returns:
            Number of matching entities.
        """
        pass

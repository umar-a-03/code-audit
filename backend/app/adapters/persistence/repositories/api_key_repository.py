"""API Key repository for database operations."""

from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.models.api_key import ApiKey


class ApiKeyRepository:
    """Repository for ApiKey model operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Database session.
        """
        self._session = session

    async def get_by_id(self, key_id: UUID) -> Optional[ApiKey]:
        """Get API key by ID.

        Args:
            key_id: API key ID.

        Returns:
            ApiKey if found, None otherwise.
        """
        stmt = select(ApiKey).where(ApiKey.id == key_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_client(
        self, key_id: UUID, client_id: UUID
    ) -> Optional[ApiKey]:
        """Get API key by ID and client (ownership check).

        Args:
            key_id: API key ID.
            client_id: Client ID.

        Returns:
            ApiKey if found and belongs to client, None otherwise.
        """
        stmt = select(ApiKey).where(
            ApiKey.id == key_id, ApiKey.client_id == client_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        """Get API key by hash.

        Args:
            key_hash: SHA-256 hash of the key.

        Returns:
            ApiKey if found, None otherwise.
        """
        stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_client(
        self, client_id: UUID
    ) -> list[ApiKey]:
        """List API keys for a client.

        Args:
            client_id: Client ID.

        Returns:
            List of API keys.
        """
        stmt = select(ApiKey).where(ApiKey.client_id == client_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        client_id: UUID,
        provider: str,
        encrypted_key: str,
        key_hash: str,
        key_name: Optional[str] = None,
    ) -> ApiKey:
        """Create a new API key.

        Args:
            client_id: Client ID.
            provider: Provider name (openai, anthropic, etc).
            encrypted_key: Fernet-encrypted key.
            key_hash: SHA-256 hash for duplicate detection.
            key_name: Optional display name.

        Returns:
            ApiKey: Created API key.
        """
        api_key = ApiKey(
            client_id=client_id,
            provider=provider,
            encrypted_key=encrypted_key,
            key_hash=key_hash,
            key_name=key_name,
            is_active=True,
        )
        self._session.add(api_key)
        await self._session.flush()
        return api_key

    async def delete(self, key_id: UUID) -> bool:
        """Delete an API key.

        Args:
            key_id: API key ID.

        Returns:
            True if deleted, False if not found.
        """
        api_key = await self.get_by_id(key_id)
        if not api_key:
            return False

        await self._session.delete(api_key)
        await self._session.flush()
        return True

    async def update_last_used(self, key_id: UUID) -> Optional[ApiKey]:
        """Update the last_used_at timestamp.

        Args:
            key_id: API key ID.

        Returns:
            Updated ApiKey if found, None otherwise.
        """
        from datetime import datetime

        api_key = await self.get_by_id(key_id)
        if not api_key:
            return None

        api_key.last_used_at = datetime.now()
        await self._session.flush()
        return api_key

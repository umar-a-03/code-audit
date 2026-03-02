"""API Key Service - Business logic for API key operations."""

import hashlib
from uuid import UUID
from typing import Optional

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.repositories import ApiKeyRepository
from app.adapters.persistence.session import get_db_session_context
from app.adapters.persistence.models.api_key import ApiKey
from app.config import get_settings


class ApiKeyService:
    """Service for API key operations."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize service with optional database session.

        Args:
            session: Optional database session.
        """
        self._session = session
        settings = get_settings()
        self._fernet = Fernet(settings.ENCRYPTION_KEY.get_secret_value())

    async def _get_session(self) -> AsyncSession:
        """Get or create database session."""
        if self._session:
            return self._session
        async with get_db_session_context() as session:
            return session

    async def _get_repo(self) -> ApiKeyRepository:
        """Get repository instance."""
        session = await self._get_session()
        return ApiKeyRepository(session)

    def _encrypt_key(self, key: str) -> str:
        """Encrypt API key.

        Args:
            key: Plain API key.

        Returns:
            Encrypted key as string.
        """
        return self._fernet.encrypt(key.encode()).decode()

    def _hash_key(self, client_id: UUID, provider: str, key: str) -> str:
        """Generate hash for API key (for duplicate detection).

        Args:
            client_id: Client ID.
            provider: Provider name.
            key: Plain API key.

        Returns:
            SHA-256 hash.
        """
        key_string = f"{client_id}:{provider}:{key}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _get_key_preview(self, key: str) -> str:
        """Get masked preview of API key.

        Args:
            key: Plain API key.

        Returns:
            Masked preview (e.g., "sk-***" or "an***").
        """
        if key.startswith("sk-"):
            return f"sk-{key[3:4]}***"
        elif key.startswith("ants"):
            return f"ants{key[4:5]}***"
        else:
            return f"{key[:2]}***"

    async def create_key(
        self,
        client_id: UUID,
        provider: str,
        key: str,
        key_name: Optional[str] = None,
    ) -> ApiKey:
        """Store a new API key (encrypted at rest).

        Args:
            client_id: Client ID.
            provider: Provider name (openai, anthropic, etc).
            key: Plain API key (will be encrypted).
            key_name: Optional display name.

        Returns:
            ApiKey: Created API key.

        Raises:
            ValueError: If key already exists.
        """
        repo = await self._get_repo()

        # Check for duplicate
        key_hash = self._hash_key(client_id, provider, key)
        existing = await repo.get_by_hash(key_hash)
        if existing:
            raise ValueError(f"API key for {provider} already exists")

        # Encrypt and store
        encrypted_key = self._encrypt_key(key)
        api_key = await repo.create(
            client_id=client_id,
            provider=provider,
            encrypted_key=encrypted_key,
            key_hash=key_hash,
            key_name=key_name,
        )
        return api_key

    async def list_keys(self, client_id: UUID) -> list[dict]:
        """List all API keys for a client.

        Args:
            client_id: Client ID.

        Returns:
            List of API key dicts with masked previews.
        """
        repo = await self._get_repo()
        keys = await repo.list_by_client(client_id)

        return [
            {
                "id": key.id,
                "provider": key.provider,
                "key_name": key.key_name,
                "is_active": key.is_active,
                "created_at": key.created_at,
                "last_used_at": key.last_used_at,
                "key_preview": f"{key.provider[:2].upper()}***",  # Generic preview
            }
            for key in keys
        ]

    async def delete_key(self, key_id: UUID, client_id: UUID) -> bool:
        """Delete an API key.

        Args:
            key_id: API key ID.
            client_id: Client ID (for ownership check).

        Returns:
            True if deleted, False if not found.

        Raises:
            ValueError: If key doesn't belong to client.
        """
        repo = await self._get_repo()

        # Verify ownership
        key = await repo.get_by_id_and_client(key_id, client_id)
        if not key:
            raise ValueError("API key not found")

        return await repo.delete(key_id)

    async def get_encrypted_key(self, key_id: UUID, client_id: UUID) -> Optional[str]:
        """Get encrypted API key for use in AI provider calls.

        Args:
            key_id: API key ID.
            client_id: Client ID.

        Returns:
            Encrypted API key if found and authorized, None otherwise.

        Note:
            The returned key is encrypted. Use decrypt_key() to decrypt.
        """
        repo = await self._get_repo()
        key = await repo.get_by_id_and_client(key_id, client_id)
        return key.encrypted_key if key else None

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an encrypted API key.

        Args:
            encrypted_key: Fernet-encrypted key.

        Returns:
            Decrypted plain key.
        """
        return self._fernet.decrypt(encrypted_key.encode()).decode()

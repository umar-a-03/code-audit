"""Client repository for database operations."""

from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.persistence.models.client import Client


class ClientRepository:
    """Repository for Client model operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Database session.
        """
        self._session = session

    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get client by ID.

        Args:
            client_id: Client ID.

        Returns:
            Client if found, None otherwise.
        """
        stmt = select(Client).where(Client.id == client_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email.

        Args:
            email: Client email.

        Returns:
            Client if found, None otherwise.
        """
        stmt = select(Client).where(Client.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_oauth_id(self, oauth_id: str) -> Optional[Client]:
        """Get client by OAuth provider ID.

        Args:
            oauth_id: OAuth provider user ID.

        Returns:
            Client if found, None otherwise.
        """
        stmt = select(Client).where(Client.oauth_id == oauth_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, client_id: UUID
    ) -> Optional[Client]:
        """Get client by ID with loaded relations.

        Args:
            client_id: Client ID.

        Returns:
            Client with relations loaded if found, None otherwise.
        """
        stmt = (
            select(Client)
            .where(Client.id == client_id)
            .options(
                selectinload(Client.projects),
                selectinload(Client.api_keys),
                selectinload(Client.analysis_jobs),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_by_oauth(
        self,
        oauth_id: str,
        email: str,
        name: Optional[str] = None,
        oauth_provider: str = "google",
    ) -> Client:
        """Get existing client or create new one from OAuth data.

        Args:
            oauth_id: OAuth provider user ID.
            email: User email.
            name: Optional user name.
            oauth_provider: OAuth provider name (default: google).

        Returns:
            Client: Existing or newly created client.
        """
        # Try to find by OAuth ID first
        client = await self.get_by_oauth_id(oauth_id)
        if client:
            return client

        # Try to find by email
        client = await self.get_by_email(email)
        if client:
            # Update OAuth info
            client.oauth_id = oauth_id
            client.oauth_provider = oauth_provider
        else:
            # Create new client
            client = Client(
                email=email,
                name=name or email.split("@")[0],
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                is_active=True,
            )
            self._session.add(client)

        await self._session.flush()
        return client

    async def create(
        self,
        email: str,
        name: Optional[str] = None,
        oauth_provider: Optional[str] = None,
        oauth_id: Optional[str] = None,
    ) -> Client:
        """Create a new client.

        Args:
            email: Client email.
            name: Optional client name.
            oauth_provider: Optional OAuth provider.
            oauth_id: Optional OAuth provider ID.

        Returns:
            Client: Created client.
        """
        client = Client(
            email=email,
            name=name,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_active=True,
        )
        self._session.add(client)
        await self._session.flush()
        return client

    async def update(self, client: Client) -> Client:
        """Update client.

        Args:
            client: Client to update.

        Returns:
            Client: Updated client.
        """
        self._session.add(client)
        await self._session.flush()
        return client

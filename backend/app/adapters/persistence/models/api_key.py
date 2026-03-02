"""API Key database model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.persistence.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.adapters.persistence.models.client import Client


class ApiKey(Base, TimestampMixin):
    """Encrypted API Key storage model.

    Implements the Bring Your Own API Key (BYOAK) pattern.
    Clients store their own API keys for AI providers, GitHub, etc.
    Keys are encrypted at rest using Fernet encryption.
    """

    __tablename__ = "api_keys"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key to client
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider identification
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # openai, anthropic, github
    key_name: Mapped[str | None] = mapped_column(String(100))  # Display name for the key

    # Encrypted key data
    encrypted_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Usage tracking
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationship
    client: Mapped["Client"] = relationship("Client", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, provider={self.provider}, key_name={self.key_name})>"

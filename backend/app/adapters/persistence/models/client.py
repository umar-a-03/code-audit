"""Client and User database models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.persistence.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.adapters.persistence.models.project import Project
    from app.adapters.persistence.models.api_key import ApiKey
    from app.adapters.persistence.models.audit import AnalysisJob, BatchJob


class Client(Base, TimestampMixin):
    """Client (tenant) model.

    Represents a tenant organization or individual user account.
    Each client has their own API keys, projects, and audit history.
    """

    __tablename__ = "clients"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Client information
    name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))  # For traditional auth
    oauth_provider: Mapped[str | None] = mapped_column(String(50))  # github, google (deprecated)
    oauth_id: Mapped[str | None] = mapped_column(String(255))  # Provider's user ID (deprecated)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Client settings (JSONB)
    # Stores: max_concurrent_jobs, retention_days, etc.
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    batch_jobs: Mapped[list["BatchJob"]] = relationship(
        "BatchJob",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, email={self.email})>"


class User(Base, TimestampMixin):
    """User model for multi-user accounts.

    Represents individual users within a client organization.
    Optional for v1 - included for future team collaboration features.
    """

    __tablename__ = "users"

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

    # User information
    email: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))

    # Role within client organization
    role: Mapped[str] = mapped_column(String(50), default="member")  # admin, member, viewer

    # Relationship
    client: Mapped["Client"] = relationship("Client", back_populates="users")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

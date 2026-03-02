"""Project database model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.persistence.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.adapters.persistence.models.client import Client
    from app.adapters.persistence.models.audit import AnalysisJob


class Project(Base, TimestampMixin):
    """Project model.

    Represents a code repository project to be analyzed.
    Each project can have multiple analysis jobs run against it.
    """

    __tablename__ = "projects"

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

    # Project information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Repository information
    repo_url: Mapped[str | None] = mapped_column(String(500))
    repo_branch: Mapped[str] = mapped_column(String(100), default="main")

    # Project settings (JSONB)
    # Stores: custom_rules, languages, ignore_patterns, etc.
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="projects")
    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        "AnalysisJob",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, repo_url={self.repo_url})>"

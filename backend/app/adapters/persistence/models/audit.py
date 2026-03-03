"""Audit and Analysis database models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, String, Text, ForeignKey, DateTime, Integer, UUID
from sqlalchemy.dialects.postgresql import ARRAY as SQLArray
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.persistence.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.adapters.persistence.models.client import Client
    from app.adapters.persistence.models.project import Project
    from app.adapters.persistence.models.result import AnalysisResult


class AnalysisJob(Base, TimestampMixin):
    """Analysis Job model.

    Represents a single code audit job.
    Jobs are queued in Redis and processed by RQ workers.
    """

    __tablename__ = "analysis_jobs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Repository information
    repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(100), default="main", nullable=True)

    # Job status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )
    # pending, queued, running, completed, failed, cancelled

    # RQ Queue reference
    rq_job_id: Mapped[str | None] = mapped_column(String(100), index=True)
    worker_name: Mapped[str | None] = mapped_column(String(100))

    # Analysis configuration
    analysis_type: Mapped[str] = mapped_column(
        String(50),
        default="full",
        nullable=False,
    )
    # full, quick, custom_rules, security_only

    options: Mapped[dict] = mapped_column(JSON, default=dict)
    # Additional options for the analysis

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Priority for queue (1=highest, 10=lowest)
    priority: Mapped[int] = mapped_column(Integer, default=5)

    # Relationships
    client: Mapped["Client"] = relationship("Client", back_populates="analysis_jobs")
    project: Mapped["Project"] = relationship("Project", back_populates="analysis_jobs")
    results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    @property
    def result(self) -> "AnalysisResult | None":
        """Get the first result if available.

        Returns:
            First AnalysisResult or None.
        """
        return self.results[0] if self.results else None

    def __repr__(self) -> str:
        return f"<AnalysisJob(id={self.id}, status={self.status}, analysis_type={self.analysis_type})>"


class AnalysisResult(Base, TimestampMixin):
    """Analysis Result model.

    Stores the results of a completed analysis job.
    Uses JSONB for flexible storage of various metrics and reports.
    """

    __tablename__ = "analysis_results"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Summary metrics (JSONB)
    # {
    #   "total_files": 150,
    #   "total_lines": 25000,
    #   "languages": {"python": 60, "javascript": 30},
    #   "quality_score": 72,
    #   "security_issues": 5,
    #   "violations": {"critical": 2, "high": 8, "medium": 15, "low": 30}
    # }
    summary: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Detailed results (JSONB)
    code_quality: Mapped[dict] = mapped_column(JSON, default=dict)
    # Cyclomatic complexity, code duplication, etc.

    rule_violations: Mapped[dict] = mapped_column(JSON, default=dict)
    # Custom rule violations with locations

    security_issues: Mapped[dict] = mapped_column(JSON, default=dict)
    # Security vulnerabilities found

    ai_report: Mapped[dict] = mapped_column(JSON, default=dict)
    # AI-generated insights and recommendations

    file_results: Mapped[dict] = mapped_column(JSON, default=dict)
    # File-by-file breakdown (for detailed views)

    # Relationships
    job: Mapped["AnalysisJob"] = relationship("AnalysisJob", back_populates="results")

    @property
    def quality_score(self) -> int | None:
        """Get quality score from summary.

        Returns:
            Quality score or None.
        """
        return self.summary.get("quality_score") if self.summary else None

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id}, job_id={self.job_id})>"


class BatchJob(Base, TimestampMixin):
    """Batch Job model.

    Represents a batch analysis of multiple repositories.
    Useful for bulk analysis operations.
    """

    __tablename__ = "batch_jobs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Batch information
    name: Mapped[str | None] = mapped_column(String(255))

    # Job tracking
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, default=0)

    # Array of analysis job IDs
    job_ids: Mapped[list[uuid.UUID]] = mapped_column(
        SQLArray(UUID),
        default=list,
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )
    # pending, running, completed, failed, cancelled

    # Relationship
    client: Mapped["Client"] = relationship("Client", back_populates="batch_jobs")

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage.

        Returns:
            float: Progress percentage (0-100).
        """
        if self.total_jobs == 0:
            return 0.0
        return (self.completed_jobs / self.total_jobs) * 100

    def __repr__(self) -> str:
        return f"<BatchJob(id={self.id}, status={self.status}, progress={self.progress_percentage:.1f}%)>"

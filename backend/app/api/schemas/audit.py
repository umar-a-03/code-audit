"""Audit schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field, EmailStr, field_validator


class AuditBase(BaseModel):
    """Base audit schema."""

    repo_url: str = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Git branch to analyze")
    project_id: Optional[UUID] = Field(None, description="Optional project ID")


class CreateAuditRequest(AuditBase):
    """Request schema for creating a new audit."""

    analysis_type: Literal["full", "quick", "security", "custom"] = Field(
        default="full",
        description="Type of analysis to perform",
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional analysis options",
    )


class AuditStatusResponse(BaseModel):
    """Response schema for audit status."""

    id: UUID
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Optional[int] = None
    current_file: Optional[str] = None


class AuditListResponse(BaseModel):
    """Response schema for audit list."""

    id: UUID
    project_id: Optional[UUID]
    status: str
    analysis_type: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    # Project info (if available)
    project_name: Optional[str] = None
    repo_url: Optional[str] = None

    # Result summary (if completed)
    quality_score: Optional[int] = None
    total_issues: Optional[int] = None


class BatchAuditRequest(BaseModel):
    """Request schema for batch audit."""

    repo_urls: list[str] = Field(
        ..., min_items=1, max_items=100,
        description="List of repository URLs to analyze"
    )
    name: Optional[str] = Field(None, description="Batch job name")
    options: dict[str, Any] = Field(default_factory=dict)


class BatchAuditStatus(BaseModel):
    """Response schema for batch audit status."""

    id: UUID
    name: Optional[str]
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    status: str
    created_at: datetime
    progress_percentage: float

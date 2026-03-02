"""Project schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    repo_url: Optional[str] = Field(None, description="GitHub repository URL")
    repo_branch: str = Field(default="main")


class CreateProjectRequest(ProjectBase):
    """Request schema for creating a project."""

    settings: dict = Field(default_factory=dict)


class UpdateProjectRequest(BaseModel):
    """Request schema for updating a project."""

    name: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[str] = None
    repo_branch: Optional[str] = None
    settings: Optional[dict] = None


class ProjectResponse(ProjectBase):
    """Response schema for a project."""

    id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime

    # Computed fields
    total_audits: int = 0
    last_audit_at: Optional[datetime] = None
    last_quality_score: Optional[int] = None


class ProjectListResponse(BaseModel):
    """Response schema for project list."""

    id: UUID
    name: str
    description: Optional[str]
    repo_url: Optional[str]
    created_at: datetime

    # Stats
    total_audits: int = 0
    last_audit_status: Optional[str] = None

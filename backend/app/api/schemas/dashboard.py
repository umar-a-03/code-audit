"""Dashboard schemas for request/response validation."""

from typing import Optional
from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    """Response schema for dashboard statistics."""

    # Counts
    total_projects: int = 0
    total_audits: int = 0
    pending_audits: int = 0
    processing_audits: int = 0
    completed_audits: int = 0
    failed_audits: int = 0

    # Metrics
    avg_quality_score: Optional[float] = None

    # Recent activity
    recent_audits: list = []


class RecentAuditItem(BaseModel):
    """Item in recent audits list."""

    id: str
    project_name: Optional[str] = None
    repo_url: Optional[str] = None
    status: str
    analysis_type: str
    quality_score: Optional[int] = None
    created_at: str

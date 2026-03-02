"""Report schemas for request/response validation."""

from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field


class ReportResponse(BaseModel):
    """Response schema for audit report."""

    job_id: UUID
    audit_id: UUID
    client_id: UUID

    # Summary metrics
    summary: dict[str, Any]

    # Detailed results
    code_quality: dict[str, Any]
    rule_violations: dict[str, Any]
    security_issues: dict[str, Any]
    ai_report: dict[str, Any]

    # File-by-file breakdown
    file_results: dict[str, Any]

    created_at: str


class ReportListResponse(BaseModel):
    """Response schema for report list (summary only)."""

    job_id: UUID
    created_at: str

    # Quick summary
    total_files: int
    total_lines: int
    quality_score: int
    total_issues: int

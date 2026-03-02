"""Dashboard API endpoints.

Provides statistics and overview data for the user dashboard.
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.api.schemas.dashboard import DashboardStatsResponse, RecentAuditItem
from app.api.deps.auth import CurrentUserDep
from app.core.services.audit import AuditService, ProjectService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: CurrentUserDep,
) -> DashboardStatsResponse:
    """Get dashboard statistics for the current user.

    Returns:
        DashboardStatsResponse: Dashboard statistics including counts and metrics.
    """
    audit_service = AuditService()
    project_service = ProjectService()

    # Get counts
    total_projects = await project_service.count_by_client(current_user.id)
    total_audits = await audit_service.count_by_client(current_user.id)
    pending_audits = await audit_service.count_by_status(current_user.id, "pending")
    processing_audits = await audit_service.count_by_status(current_user.id, "running")
    completed_audits = await audit_service.count_by_status(current_user.id, "completed")
    failed_audits = await audit_service.count_by_status(current_user.id, "failed")

    # Get average quality score
    avg_quality_score = await audit_service.get_avg_quality_score(current_user.id)

    # Get recent audits
    recent_audits_data = await audit_service.list_audits(
        client_id=current_user.id,
        limit=10,
        sort_by="created_at",
        sort_order="DESC",
    )

    return DashboardStatsResponse(
        total_projects=total_projects,
        total_audits=total_audits,
        pending_audits=pending_audits,
        processing_audits=processing_audits,
        completed_audits=completed_audits,
        failed_audits=failed_audits,
        avg_quality_score=avg_quality_score,
        recent_audits=[
            RecentAuditItem(
                id=str(audit.id),
                project_name=audit.project.name if audit.project else None,
                repo_url=audit.project.repo_url if audit.project else None,
                status=audit.status,
                analysis_type=audit.analysis_type,
                quality_score=audit.result.quality_score if audit.result else None,
                created_at=audit.created_at.isoformat(),
            )
            for audit in recent_audits_data
        ],
    )

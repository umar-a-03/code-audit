"""Audits API endpoints.

Manages code audit jobs and their results.
"""

import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Query, status as status
from pydantic import ValidationError

from app.api.deps.auth import CurrentUserDep
from app.api.schemas.audit import (
    CreateAuditRequest,
    AuditStatusResponse,
    AuditListResponse,
    BatchAuditRequest,
    BatchAuditStatus,
)
from app.core.services.audit import AuditService, BatchService
from app.api.exceptions import NotFoundException, BadRequestException
from app.adapters.queue.rq import get_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("", response_model=AuditStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    request: CreateAuditRequest,
    current_user: CurrentUserDep,
) -> AuditStatusResponse:
    """Create a new code audit job.

    Args:
        request: Audit creation data.

    Returns:
        AuditStatusResponse: Created audit job.

    Raises:
        HTTPException: 400 if validation fails, 409 if concurrent limit exceeded.
    """
    audit_service = AuditService()
    queue = get_queue()

    # Check concurrent job limit
    # TODO: Implement proper concurrent limit checking with Redis
    # active_jobs = await audit_service.count_active_jobs(current_user.id)
    # if active_jobs >= 5:
    #     raise HTTPException(status_code=409, detail="Concurrent job limit exceeded")

    # Create analysis job
    job = await audit_service.create_job(
        client_id=current_user.id,
        project_id=request.project_id,
        repo_url=request.repo_url,
        branch=request.branch,
        analysis_type=request.analysis_type,
        options=request.options,
    )

    # Enqueue the background job
    from app.workers.tasks import run_audit_job

    queued_job = queue.enqueue(
        run_audit_job,
        job_id=str(job.id),
        repo_url=request.repo_url,
        branch=request.branch,
        client_id=str(current_user.id),
        options=request.options,
    )

    # Update job with RQ job ID
    await audit_service.update_rq_job_id(job.id, queued_job.id)

    return AuditStatusResponse(
        id=job.id,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        progress=0,
    )


@router.get("", response_model=list[AuditListResponse])
async def list_audits(
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
) -> list[AuditListResponse]:
    """List all audits for the current user.

    Args:
        skip: Number of audits to skip.
        limit: Maximum number of audits to return.
        status: Filter by status.

    Returns:
        list[AuditListResponse]: List of audits.
    """
    audit_service = AuditService()

    audits = await audit_service.list_by_client(
        client_id=current_user.id,
        skip=skip,
        limit=limit,
        status_filter=status,
        sort_by="created_at",
        sort_order="DESC",
    )

    return [
        AuditListResponse(
            id=audit.id,
            project_id=audit.project_id,
            status=audit.status,
            analysis_type=audit.analysis_type,
            created_at=audit.created_at,
            completed_at=audit.completed_at,
            project_name=audit.project.name if audit.project else None,
            repo_url=audit.project.repo_url if audit.project else None,
            quality_score=None,  # TODO: Get from result
            total_issues=None,     # TODO: Get from result
        )
        for audit in audits
    ]


@router.get("/{audit_id}", response_model=AuditStatusResponse)
async def get_audit(
    audit_id: UUID,
    current_user: CurrentUserDep,
) -> AuditStatusResponse:
    """Get audit status and details by ID.

    Args:
        audit_id: Audit ID.

    Returns:
        AuditStatusResponse: Audit details.

    Raises:
        HTTPException: 404 if audit not found.
    """
    audit_service = AuditService()

    audit = await audit_service.get_by_id_and_client(
        audit_id=audit_id,
        client_id=current_user.id,
    )

    if not audit:
        raise NotFoundException("Audit not found")

    # Get progress from Redis cache if available
    # TODO: Implement Redis status cache

    return AuditStatusResponse(
        id=audit.id,
        status=audit.status,
        created_at=audit.created_at,
        started_at=audit.started_at,
        completed_at=audit.completed_at,
        error_message=audit.error_message,
        progress=None,  # TODO: Get from cache
        current_file=None,
    )


@router.delete("/{audit_id}", status_code=status.HTTP_202_ACCEPTED)
async def cancel_audit(
    audit_id: UUID,
    current_user: CurrentUserDep,
):
    """Cancel an audit job.

    Args:
        audit_id: Audit ID.

    Raises:
        HTTPException: 404 if audit not found.
    """
    audit_service = AuditService()
    queue = get_queue()

    # Verify ownership
    audit = await audit_service.get_by_id_and_client(
        audit_id=audit_id,
        client_id=current_user.id,
    )

    if not audit:
        raise NotFoundException("Audit not found")

    # Cancel in RQ if running
    if audit.rq_job_id:
        queue.cancel_job(audit.rq_job_id)

    # Update status
    await audit_service.update_status(audit_id, "cancelled")

    return None


@router.post("/batch", response_model=BatchAuditStatus)
async def create_batch_audit(
    request: BatchAuditRequest,
    current_user: CurrentUserDep,
) -> BatchAuditStatus:
    """Create a batch of audit jobs.

    Args:
        request: Batch audit request.

    Returns:
        BatchAuditStatus: Created batch job info.
    """
    batch_service = BatchService()
    audit_service = AuditService()

    # Create batch job
    batch_job = await batch_service.create(
        client_id=current_user.id,
        name=request.name,
        repo_urls=request.repo_urls,
        options=request.options,
    )

    # Create individual audit jobs
    job_ids = []

    for repo_url in request.repo_urls:
        job = await audit_service.create_job(
            client_id=current_user.id,
            repo_url=repo_url,
            branch="main",
            analysis_type="full",
            options=request.options,
        )
        job_ids.append(job.id)

    # Update batch with job IDs
    await batch_service.update_job_ids(batch_job.id, job_ids)

    return BatchAuditStatus(
        id=batch_job.id,
        name=batch_job.name,
        total_jobs=len(job_ids),
        completed_jobs=0,
        failed_jobs=0,
        status=batch_job.status,
        created_at=batch_job.created_at,
        progress_percentage=0.0,
    )


@router.get("/batch/{batch_id}", response_model=BatchAuditStatus)
async def get_batch_status(
    batch_id: UUID,
    current_user: CurrentUserDep,
) -> BatchAuditStatus:
    """Get batch audit status.

    Args:
        batch_id: Batch job ID.

    Returns:
        BatchAuditStatus: Batch status details.

    Raises:
        HTTPException: 404 if batch not found.
    """
    batch_service = BatchService()

    batch = await batch_service.get_by_id_and_client(
        batch_id=batch_id,
        client_id=current_user.id,
    )

    if not batch:
        raise NotFoundException("Batch job not found")

    # Calculate progress
    progress_percentage = batch.progress_percentage if hasattr(batch, 'progress_percentage') else 0.0

    return BatchAuditStatus(
        id=batch.id,
        name=batch.name,
        total_jobs=batch.total_jobs,
        completed_jobs=batch.completed_jobs,
        failed_jobs=batch.failed_jobs,
        status=batch.status,
        created_at=batch.created_at,
        progress_percentage=progress_percentage,
    )

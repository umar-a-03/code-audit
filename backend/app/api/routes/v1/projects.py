"""Projects API endpoints.

Manages code repository projects that can be audited.
"""

from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Query, status as status
from pydantic import ValidationError

from app.api.deps.auth import CurrentUserDep
from app.api.schemas.project import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
    ProjectListResponse,
)
from app.core.services.audit import ProjectService
from app.api.exceptions import NotFoundException, BadRequestException


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectListResponse])
async def list_projects(
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
) -> List[ProjectListResponse]:
    """List all projects for the current user.

    Args:
        skip: Number of projects to skip.
        limit: Maximum number of projects to return.
        sort_by: Field to sort by.
        sort_order: Sort order (asc/desc).

    Returns:
        List[ProjectListResponse]: List of projects.
    """
    project_service = ProjectService()

    projects = await project_service.list_by_client(
        client_id=current_user.id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Convert to response models
    return [
        ProjectListResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            repo_url=p.repo_url,
            created_at=p.created_at,
            total_audits=0,  # TODO: Add audit counting
            last_audit_status=None,
        )
        for p in projects
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    current_user: CurrentUserDep,
) -> ProjectResponse:
    """Create a new project.

    Args:
        request: Project creation data.

    Returns:
        ProjectResponse: Created project.
    """
    project_service = ProjectService()

    project = await project_service.create(
        client_id=current_user.id,
        name=request.name,
        description=request.description,
        repo_url=request.repo_url,
        repo_branch=request.repo_branch,
        settings=request.settings,
    )

    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        name=project.name,
        description=project.description,
        repo_url=project.repo_url,
        repo_branch=project.repo_branch,
        created_at=project.created_at,
        updated_at=project.updated_at,
        total_audits=0,
        last_audit_at=None,
        last_quality_score=None,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: CurrentUserDep,
) -> ProjectResponse:
    """Get a specific project by ID.

    Args:
        project_id: Project ID.

    Returns:
        ProjectResponse: Project details.

    Raises:
        HTTPException: 404 if project not found.
    """
    project_service = ProjectService()

    project = await project_service.get_by_id_and_client(
        project_id=project_id,
        client_id=current_user.id,
    )

    if not project:
        raise NotFoundException("Project not found")

    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        name=project.name,
        description=project.description,
        repo_url=project.repo_url,
        repo_branch=project.repo_branch,
        created_at=project.created_at,
        updated_at=project.updated_at,
        total_audits=0,
        last_audit_at=None,
        last_quality_score=None,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    request: UpdateProjectRequest,
    current_user: CurrentUserDep,
) -> ProjectResponse:
    """Update a project.

    Args:
        project_id: Project ID.
        request: Update data.

    Returns:
        ProjectResponse: Updated project.

    Raises:
        HTTPException: 404 if project not found.
    """
    project_service = ProjectService()

    # Verify ownership
    existing = await project_service.get_by_id_and_client(
        project_id=project_id,
        client_id=current_user.id,
    )

    if not existing:
        raise NotFoundException("Project not found")

    # Update only provided fields
    update_data = request.model_dump(exclude_unset=True)

    project = await project_service.update(
        project_id=project_id,
        **update_data,
    )

    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        name=project.name,
        description=project.description,
        repo_url=project.repo_url,
        repo_branch=project.repo_branch,
        created_at=project.created_at,
        updated_at=project.updated_at,
        total_audits=0,
        last_audit_at=None,
        last_quality_score=None,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: CurrentUserDep,
):
    """Delete a project.

    Args:
        project_id: Project ID.

    Raises:
        HTTPException: 404 if project not found.
    """
    project_service = ProjectService()

    # Verify ownership
    existing = await project_service.get_by_id_and_client(
        project_id=project_id,
        client_id=current_user.id,
    )

    if not existing:
        raise NotFoundException("Project not found")

    await project_service.delete(project_id)

    return None

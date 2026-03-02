"""Project repository for database operations."""

from uuid import UUID
from typing import Optional

from sqlalchemy import desc, select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.persistence.models.project import Project
from app.adapters.persistence.models.audit import AnalysisJob


class ProjectRepository:
    """Repository for Project model operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Database session.
        """
        self._session = session

    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID.

        Args:
            project_id: Project ID.

        Returns:
            Project if found, None otherwise.
        """
        stmt = select(Project).where(Project.id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_client(
        self, project_id: UUID, client_id: UUID
    ) -> Optional[Project]:
        """Get project by ID and client (ownership check).

        Args:
            project_id: Project ID.
            client_id: Client ID.

        Returns:
            Project if found and belongs to client, None otherwise.
        """
        stmt = select(Project).where(
            Project.id == project_id, Project.client_id == client_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, project_id: UUID, client_id: UUID
    ) -> Optional[Project]:
        """Get project by ID with relations.

        Args:
            project_id: Project ID.
            client_id: Client ID.

        Returns:
            Project with relations if found, None otherwise.
        """
        stmt = (
            select(Project)
            .where(Project.id == project_id, Project.client_id == client_id)
            .options(selectinload(Project.analysis_jobs))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[Project]:
        """List projects for a client.

        Args:
            client_id: Client ID.
            skip: Number of projects to skip.
            limit: Maximum number of projects to return.
            sort_by: Field to sort by.
            sort_order: Sort order (asc/desc).

        Returns:
            List of projects.
        """
        stmt = select(Project).where(Project.client_id == client_id)

        # Apply sorting
        sort_column = getattr(Project, sort_by, Project.created_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(sort_column))
        else:
            stmt = stmt.order_by(sort_column)

        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        client_id: UUID,
        name: str,
        description: Optional[str] = None,
        repo_url: Optional[str] = None,
        repo_branch: str = "main",
        settings: dict | None = None,
    ) -> Project:
        """Create a new project.

        Args:
            client_id: Client ID.
            name: Project name.
            description: Optional description.
            repo_url: Optional repository URL.
            repo_branch: Git branch (default: main).
            settings: Project settings dict.

        Returns:
            Project: Created project.
        """
        project = Project(
            client_id=client_id,
            name=name,
            description=description,
            repo_url=repo_url,
            repo_branch=repo_branch,
            settings=settings or {},
        )
        self._session.add(project)
        await self._session.flush()
        return project

    async def update(
        self,
        project_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        repo_url: Optional[str] = None,
        repo_branch: Optional[str] = None,
        settings: Optional[dict] = None,
    ) -> Optional[Project]:
        """Update a project.

        Args:
            project_id: Project ID.
            name: Optional new name.
            description: Optional new description.
            repo_url: Optional new repository URL.
            repo_branch: Optional new branch.
            settings: Optional new settings.

        Returns:
            Updated project if found, None otherwise.
        """
        project = await self.get_by_id(project_id)
        if not project:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if repo_url is not None:
            project.repo_url = repo_url
        if repo_branch is not None:
            project.repo_branch = repo_branch
        if settings is not None:
            project.settings = settings

        await self._session.flush()
        return project

    async def delete(self, project_id: UUID) -> bool:
        """Delete a project.

        Args:
            project_id: Project ID.

        Returns:
            True if deleted, False if not found.
        """
        project = await self.get_by_id(project_id)
        if not project:
            return False

        await self._session.delete(project)
        await self._session.flush()
        return True

    async def count_by_client(self, client_id: UUID) -> int:
        """Count projects for a client.

        Args:
            client_id: Client ID.

        Returns:
            Number of projects.
        """
        stmt = select(func.count()).where(Project.client_id == client_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def get_last_audit_status(self, project_id: UUID) -> Optional[str]:
        """Get the status of the most recent audit for a project.

        Args:
            project_id: Project ID.

        Returns:
            Status string or None if no audits.
        """
        stmt = (
            select(AnalysisJob.status)
            .where(AnalysisJob.project_id == project_id)
            .order_by(desc(AnalysisJob.created_at))
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

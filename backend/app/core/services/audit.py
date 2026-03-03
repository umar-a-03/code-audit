"""Audit Service - Business logic for audit operations."""

from uuid import UUID
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence.repositories import (
    AnalysisJobRepository,
    BatchJobRepository,
    ProjectRepository,
)
from app.adapters.persistence.session import get_db_session_context
from app.adapters.persistence.models.audit import AnalysisJob, BatchJob
from app.adapters.persistence.models.project import Project


class AuditService:
    """Service for audit-related business logic."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize service with optional database session.

        Args:
            session: Optional database session. If not provided, creates a new one.
        """
        self._session = session
        self._repo: AnalysisJobRepository | None = None

    async def _get_session(self) -> AsyncSession:
        """Get or create database session."""
        if self._session:
            return self._session
        # For backward compatibility with routes that don't pass session
        async with get_db_session_context() as session:
            return session

    async def _get_repo(self) -> AnalysisJobRepository:
        """Get repository instance."""
        if self._repo is None:
            session = await self._get_session()
            return AnalysisJobRepository(session)
        return self._repo

    async def create_job(
        self,
        client_id: UUID,
        project_id: Optional[UUID],
        repo_url: str,
        branch: str,
        analysis_type: str,
        options: dict,
    ) -> AnalysisJob:
        """Create a new analysis job.

        Args:
            client_id: Client ID.
            project_id: Optional project ID.
            repo_url: Repository URL.
            branch: Git branch.
            analysis_type: Type of analysis.
            options: Additional options.

        Returns:
            AnalysisJob: Created job.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)

        # If project_id is provided, use it. Otherwise, we might want to
        # find or create a project based on repo_url.
        # For now, just create the job with the provided project_id.
        job = await repo.create(
            client_id=client_id,
            project_id=project_id,
            repo_url=repo_url,
            branch=branch,
            analysis_type=analysis_type,
            options=options,
        )
        return job

    async def get_by_id_and_client(
        self,
        job_id: UUID,
        client_id: UUID,
    ) -> Optional[AnalysisJob]:
        """Get audit job by ID and client (for ownership check).

        Args:
            job_id: Job ID.
            client_id: Client ID.

        Returns:
            AnalysisJob if found, None otherwise.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        return await repo.get_by_id_and_client(job_id, client_id)

    async def list_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[AnalysisJob]:
        """List audits for a client.

        Args:
            client_id: Client ID.
            skip: Number to skip.
            limit: Max results.
            status_filter: Filter by status.
            sort_by: Field to sort by.
            sort_order: Sort order.

        Returns:
            List of AnalysisJob.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        return await repo.list_by_client(
            client_id=client_id,
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    # Alias for compatibility with dashboard route
    async def list_audits(
        self,
        client_id: UUID,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        **kwargs,
    ) -> List[AnalysisJob]:
        """Alias for list_by_client for compatibility.

        Args:
            client_id: Client ID.
            limit: Max results.
            sort_by: Field to sort by.
            sort_order: Sort order.
            **kwargs: Additional arguments.

        Returns:
            List of AnalysisJob.
        """
        return await self.list_by_client(
            client_id=client_id,
            skip=0,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def count_by_client(self, client_id: UUID) -> int:
        """Count all audits for a client.

        Args:
            client_id: Client ID.

        Returns:
            int: Count of audits.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        return await repo.count_by_client(client_id)

    async def count_by_status(
        self,
        client_id: UUID,
        status: str,
    ) -> int:
        """Count audits by status.

        Args:
            client_id: Client ID.
            status: Status to count.

        Returns:
            int: Count of audits with given status.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        return await repo.count_by_status(client_id, status)

    async def get_avg_quality_score(self, client_id: UUID) -> Optional[float]:
        """Get average quality score for a client.

        Args:
            client_id: Client ID.

        Returns:
            Average quality score or None.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        return await repo.get_avg_quality_score(client_id)

    async def update_status(
        self,
        job_id: UUID,
        status: str,
    ) -> None:
        """Update audit job status.

        Args:
            job_id: Job ID.
            status: New status.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        await repo.update_status(job_id, status)

    async def update_rq_job_id(
        self,
        job_id: UUID,
        rq_job_id: str,
    ) -> None:
        """Update audit job with RQ job ID.

        Args:
            job_id: Job ID.
            rq_job_id: RQ job ID.
        """
        session = await self._get_session()
        repo = AnalysisJobRepository(session)
        await repo.update_rq_job_id(job_id, rq_job_id)


class BatchService:
    """Service for batch audit operations."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize service with optional database session.

        Args:
            session: Optional database session.
        """
        self._session = session

    async def _get_session(self) -> AsyncSession:
        """Get or create database session."""
        if self._session:
            return self._session
        async with get_db_session_context() as session:
            return session

    async def create(
        self,
        client_id: UUID,
        name: Optional[str],
        repo_urls: List[str],
        options: dict,
    ) -> BatchJob:
        """Create a new batch audit job.

        Args:
            client_id: Client ID.
            name: Optional batch name.
            repo_urls: List of repository URLs.
            options: Additional options.

        Returns:
            BatchJob: Created batch job.
        """
        session = await self._get_session()
        repo = BatchJobRepository(session)
        return await repo.create(client_id, name, repo_urls, options)

    async def get_by_id_and_client(
        self,
        batch_id: UUID,
        client_id: UUID,
    ) -> Optional[BatchJob]:
        """Get batch job by ID and client.

        Args:
            batch_id: Batch job ID.
            client_id: Client ID.

        Returns:
            BatchJob if found, None otherwise.
        """
        session = await self._get_session()
        repo = BatchJobRepository(session)
        return await repo.get_by_id_and_client(batch_id, client_id)

    async def update_job_ids(
        self,
        batch_id: UUID,
        job_ids: List[UUID],
    ) -> None:
        """Update batch job with job IDs.

        Args:
            batch_id: Batch job ID.
            job_ids: List of job IDs.
        """
        session = await self._get_session()
        repo = BatchJobRepository(session)
        await repo.update_job_ids(batch_id, job_ids)

    async def update_progress(
        self,
        batch_id: UUID,
        completed: int,
        failed: int,
    ) -> None:
        """Update batch job progress.

        Args:
            batch_id: Batch job ID.
            completed: Number of completed jobs.
            failed: Number of failed jobs.
        """
        session = await self._get_session()
        repo = BatchJobRepository(session)
        await repo.update_progress(batch_id, completed, failed)

    async def delete(self, batch_id: UUID) -> bool:
        """Delete a batch job.

        Args:
            batch_id: Batch job ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        session = await self._get_session()
        repo = BatchJobRepository(session)
        return await repo.delete(batch_id)


class ProjectService:
    """Service for project operations."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        """Initialize service with optional database session.

        Args:
            session: Optional database session.
        """
        self._session = session

    async def _get_session(self) -> AsyncSession:
        """Get or create database session."""
        if self._session:
            return self._session
        async with get_db_session_context() as session:
            return session

    async def create(
        self,
        client_id: UUID,
        name: str,
        description: Optional[str],
        repo_url: Optional[str],
        repo_branch: str,
        settings: dict,
    ) -> Project:
        """Create a new project.

        Args:
            client_id: Client ID.
            name: Project name.
            description: Project description.
            repo_url: Repository URL.
            repo_branch: Git branch.
            settings: Project settings.

        Returns:
            Project: Created project.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        return await repo.create(
            client_id=client_id,
            name=name,
            description=description,
            repo_url=repo_url,
            repo_branch=repo_branch,
            settings=settings,
        )

    async def get_by_id_and_client(
        self,
        project_id: UUID,
        client_id: UUID,
    ) -> Optional[Project]:
        """Get project by ID and client (for ownership check).

        Args:
            project_id: Project ID.
            client_id: Client ID.

        Returns:
            Project if found, None otherwise.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        return await repo.get_by_id_and_client(project_id, client_id)

    async def list_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Project]:
        """List projects for a client.

        Args:
            client_id: Client ID.
            skip: Number to skip.
            limit: Max results.
            sort_by: Field to sort by.
            sort_order: Sort order.

        Returns:
            List of Project.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        return await repo.list_by_client(
            client_id=client_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def count_by_client(self, client_id: UUID) -> int:
        """Count projects for a client.

        Args:
            client_id: Client ID.

        Returns:
            int: Count of projects.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        return await repo.count_by_client(client_id)

    async def update(
        self,
        project_id: UUID,
        **kwargs,
    ) -> Project:
        """Update a project.

        Args:
            project_id: Project ID.
            **kwargs: Fields to update.

        Returns:
            Project: Updated project.

        Raises:
            ValueError: If project not found.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        result = await repo.update(project_id, **kwargs)
        if result is None:
            raise ValueError(f"Project {project_id} not found")
        return result

    async def delete(self, project_id: UUID) -> None:
        """Delete a project.

        Args:
            project_id: Project ID.

        Raises:
            ValueError: If project not found.
        """
        session = await self._get_session()
        repo = ProjectRepository(session)
        success = await repo.delete(project_id)
        if not success:
            raise ValueError(f"Project {project_id} not found")

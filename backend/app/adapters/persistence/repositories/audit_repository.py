"""Analysis Job repository for database operations."""

from uuid import UUID
from typing import Optional

from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.persistence.models.audit import AnalysisJob, BatchJob


class AnalysisJobRepository:
    """Repository for AnalysisJob model operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Database session.
        """
        self._session = session

    async def get_by_id(self, job_id: UUID) -> Optional[AnalysisJob]:
        """Get analysis job by ID.

        Args:
            job_id: Job ID.

        Returns:
            AnalysisJob if found, None otherwise.
        """
        stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_client(
        self, job_id: UUID, client_id: UUID
    ) -> Optional[AnalysisJob]:
        """Get analysis job by ID and client (ownership check).

        Args:
            job_id: Job ID.
            client_id: Client ID.

        Returns:
            AnalysisJob if found and belongs to client, None otherwise.
        """
        stmt = select(AnalysisJob).where(
            AnalysisJob.id == job_id, AnalysisJob.client_id == client_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, job_id: UUID, client_id: UUID
    ) -> Optional[AnalysisJob]:
        """Get analysis job with relations.

        Args:
            job_id: Job ID.
            client_id: Client ID.

        Returns:
            AnalysisJob with relations if found, None otherwise.
        """
        stmt = (
            select(AnalysisJob)
            .where(AnalysisJob.id == job_id, AnalysisJob.client_id == client_id)
            .options(
                selectinload(AnalysisJob.project),
                selectinload(AnalysisJob.results),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_client(
        self,
        client_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[AnalysisJob]:
        """List analysis jobs for a client.

        Args:
            client_id: Client ID.
            skip: Number of jobs to skip.
            limit: Maximum number of jobs to return.
            status_filter: Optional status filter.
            sort_by: Field to sort by.
            sort_order: Sort order (asc/desc).

        Returns:
            List of analysis jobs.
        """
        stmt = select(AnalysisJob).where(AnalysisJob.client_id == client_id)

        if status_filter:
            stmt = stmt.where(AnalysisJob.status == status_filter)

        # Apply sorting
        sort_column = getattr(AnalysisJob, sort_by, AnalysisJob.created_at)
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
        project_id: Optional[UUID],
        repo_url: str,
        branch: str,
        analysis_type: str,
        options: dict,
        status: str = "pending",
    ) -> AnalysisJob:
        """Create a new analysis job.

        Args:
            client_id: Client ID.
            project_id: Optional project ID.
            repo_url: Repository URL.
            branch: Git branch.
            analysis_type: Type of analysis.
            options: Additional options.
            status: Initial status (default: pending).

        Returns:
            AnalysisJob: Created job.
        """
        job = AnalysisJob(
            client_id=client_id,
            project_id=project_id,
            status=status,
            analysis_type=analysis_type,
            options=options,
            priority=5,
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_status(self, job_id: UUID, status: str) -> Optional[AnalysisJob]:
        """Update job status.

        Args:
            job_id: Job ID.
            status: New status.

        Returns:
            Updated job if found, None otherwise.
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.status = status
        await self._session.flush()
        return job

    async def update_rq_job_id(
        self, job_id: UUID, rq_job_id: str
    ) -> Optional[AnalysisJob]:
        """Update job with RQ job ID.

        Args:
            job_id: Job ID.
            rq_job_id: RQ job ID.

        Returns:
            Updated job if found, None otherwise.
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None

        job.rq_job_id = rq_job_id
        await self._session.flush()
        return job

    async def count_by_client(self, client_id: UUID) -> int:
        """Count jobs for a client.

        Args:
            client_id: Client ID.

        Returns:
            Number of jobs.
        """
        stmt = select(func.count()).where(AnalysisJob.client_id == client_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def count_by_status(
        self, client_id: UUID, status: str
    ) -> int:
        """Count jobs by status for a client.

        Args:
            client_id: Client ID.
            status: Status to count.

        Returns:
            Number of jobs with given status.
        """
        stmt = select(func.count()).where(
            AnalysisJob.client_id == client_id,
            AnalysisJob.status == status,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def get_avg_quality_score(self, client_id: UUID) -> Optional[float]:
        """Get average quality score for completed jobs.

        Args:
            client_id: Client ID.

        Returns:
            Average quality score or None if no completed jobs.
        """
        # This would join with analysis_results table
        # For now, return None as the results table isn't fully implemented
        return None


class BatchJobRepository:
    """Repository for BatchJob model operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Database session.
        """
        self._session = session

    async def get_by_id(self, batch_id: UUID) -> Optional[BatchJob]:
        """Get batch job by ID.

        Args:
            batch_id: Batch job ID.

        Returns:
            BatchJob if found, None otherwise.
        """
        stmt = select(BatchJob).where(BatchJob.id == batch_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_and_client(
        self, batch_id: UUID, client_id: UUID
    ) -> Optional[BatchJob]:
        """Get batch job by ID and client (ownership check).

        Args:
            batch_id: Batch job ID.
            client_id: Client ID.

        Returns:
            BatchJob if found and belongs to client, None otherwise.
        """
        stmt = select(BatchJob).where(
            BatchJob.id == batch_id, BatchJob.client_id == client_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        client_id: UUID,
        name: Optional[str],
        repo_urls: list[str],
        options: dict,
    ) -> BatchJob:
        """Create a new batch job.

        Args:
            client_id: Client ID.
            name: Optional batch name.
            repo_urls: List of repository URLs.
            options: Additional options.

        Returns:
            BatchJob: Created batch job.
        """
        batch = BatchJob(
            client_id=client_id,
            name=name,
            total_jobs=len(repo_urls),
            status="pending",
            job_ids=[],
        )
        self._session.add(batch)
        await self._session.flush()
        return batch

    async def update_job_ids(
        self, batch_id: UUID, job_ids: list[UUID]
    ) -> Optional[BatchJob]:
        """Update batch job with job IDs.

        Args:
            batch_id: Batch job ID.
            job_ids: List of job IDs.

        Returns:
            Updated batch job if found, None otherwise.
        """
        batch = await self.get_by_id(batch_id)
        if not batch:
            return None

        batch.job_ids = job_ids
        await self._session.flush()
        return batch

    async def update_progress(
        self, batch_id: UUID, completed: int, failed: int
    ) -> Optional[BatchJob]:
        """Update batch job progress.

        Args:
            batch_id: Batch job ID.
            completed: Number of completed jobs.
            failed: Number of failed jobs.

        Returns:
            Updated batch job if found, None otherwise.
        """
        batch = await self.get_by_id(batch_id)
        if not batch:
            return None

        batch.completed_jobs = completed
        batch.failed_jobs = failed

        # Update status if all jobs are done
        if completed + failed >= batch.total_jobs:
            batch.status = "completed"

        await self._session.flush()
        return batch

    async def delete(self, batch_id: UUID) -> bool:
        """Delete a batch job.

        Args:
            batch_id: Batch job ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        batch = await self.get_by_id(batch_id)
        if not batch:
            return False

        await self._session.delete(batch)
        await self._session.flush()
        return True

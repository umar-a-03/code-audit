"""Queue protocol (abstract interface).

Defines the contract for job queue implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable
from dataclasses import dataclass


@dataclass
class JobStatus:
    """Job status information."""

    id: str
    status: str  # queued, started, finished, failed, cancelled
    created_at: str
    started_at: str | None
    ended_at: str | None
    result: Any | None
    error: str | None
    progress: int | None
    metadata: dict[str, Any]


class Queue(ABC):
    """Job queue protocol.

    All queue implementations (RQ, Celery, etc.) must implement this interface.
    """

    @abstractmethod
    async def enqueue(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Enqueue a job.

        Args:
            func: Async function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Job ID.
        """
        pass

    @abstractmethod
    async def get_job_status(self, job_id: str) -> JobStatus | None:
        """Get job status.

        Args:
            job_id: Job ID.

        Returns:
            Job status or None.
        """
        pass

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.

        Args:
            job_id: Job ID.

        Returns:
            True if job was cancelled.
        """
        pass

    @abstractmethod
    async def get_queue_size(self) -> int:
        """Get current queue size.

        Returns:
            Number of jobs in queue.
        """
        pass

    @abstractmethod
    async def get_failed_jobs(self) -> list[str]:
        """Get IDs of failed jobs.

        Returns:
            List of failed job IDs.
        """
        pass

    @abstractmethod
    async def retry_job(self, job_id: str) -> str | None:
        """Retry a failed job.

        Args:
            job_id: Job ID.

        Returns:
            New job ID or None.
        """
        pass

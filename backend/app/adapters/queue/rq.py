"""RQ (Redis Queue) adapter.

Provides job queue functionality using RQ.
"""

from typing import Any, Callable

from rq import Queue
from rq.job import Job
from redis import Redis

from app.config import get_settings

settings = get_settings()


class JobQueue:
    """Job queue wrapper using RQ."""

    def __init__(self, redis: Redis | None = None, queue_name: str | None = None) -> None:
        """Initialize job queue.

        Args:
            redis: Redis client instance.
            queue_name: Queue name.
        """
        self.redis = redis or Redis.from_url(settings.REDIS_URL)
        self.queue_name = queue_name or settings.RQ_QUEUE_NAME
        self._queue: Queue | None = None

    @property
    def queue(self) -> Queue:
        """Get or create RQ queue.

        Returns:
            Queue: RQ queue instance.
        """
        if self._queue is None:
            self._queue = Queue(
                self.queue_name,
                connection=self.redis,
                default_timeout=settings.RQ_JOB_TIMEOUT,
                result_ttl=settings.RQ_RESULT_TTL,
                failure_ttl=settings.RQ_FAILURE_TTL,
            )
        return self._queue

    def enqueue(
        self,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Job:
        """Enqueue a job.

        Args:
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Job: RQ job instance.
        """
        job = self.queue.enqueue(func, *args, **kwargs)
        return job

    def enqueue_at(
        self,
        scheduled_time: Any,  # datetime
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Job:
        """Enqueue a job to run at a specific time.

        Args:
            scheduled_time: When to run the job.
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Job: RQ job instance.
        """
        job = self.queue.enqueue_at(scheduled_time, func, *args, **kwargs)
        return job

    def enqueue_in(
        self,
        time_delta: Any,  # timedelta
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Job:
        """Enqueue a job to run after a time delta.

        Args:
            time_delta: Time to wait before running.
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.

        Returns:
            Job: RQ job instance.
        """
        job = self.queue.enqueue_in(time_delta, func, *args, **kwargs)
        return job

    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID.

        Args:
            job_id: Job ID.

        Returns:
            Job: RQ job instance or None.
        """
        return Job.fetch(job_id, connection=self.redis)

    def get_job_status(self, job_id: str) -> str | None:
        """Get job status.

        Args:
            job_id: Job ID.

        Returns:
            Job status string or None.
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        return job.get_status()

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.

        Args:
            job_id: Job ID.

        Returns:
            bool: True if job was cancelled.
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        job.cancel()
        return True

    def get_queue_size(self) -> int:
        """Get current queue size.

        Returns:
            int: Number of jobs in queue.
        """
        return len(self.queue)

    def get_queued_job_ids(self) -> list[str]:
        """Get IDs of all queued jobs.

        Returns:
            List of job IDs.
        """
        return self.queue.job_ids

    def empty_queue(self) -> int:
        """Empty the queue.

        Returns:
            int: Number of jobs removed.
        """
        return self.queue.empty()

    def get_failed_jobs(self) -> list[Job]:
        """Get all failed jobs.

        Returns:
            List of failed jobs.
        """
        return self.queue.failed_job_registry.get_job_ids()

    def retry_failed_job(self, job_id: str) -> Job | None:
        """Retry a failed job.

        Args:
            job_id: Job ID.

        Returns:
            New job instance or None.
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        return job.requeue()


# Global queue instance
_global_queue: JobQueue | None = None


def get_queue() -> JobQueue:
    """Get global job queue instance.

    Returns:
        JobQueue: Global job queue.
    """
    global _global_queue
    if _global_queue is None:
        _global_queue = JobQueue()
    return _global_queue


# Decorator for queueing functions
def queueable(
    queue_name: str | None = None,
    timeout: int | None = None,
    result_ttl: int | None = None,
):
    """Decorator to make a function queueable.

    Args:
        queue_name: Queue name to use.
        timeout: Job timeout in seconds.
        result_ttl: Result TTL in seconds.

    Returns:
        Decorated function.
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Job:
            queue = JobQueue(queue_name=queue_name)
            return queue.enqueue(func, *args, **kwargs)

        wrapper.queue = func  # Store original function
        return wrapper

    return decorator

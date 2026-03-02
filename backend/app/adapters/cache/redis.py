"""Redis cache adapter.

Provides caching functionality using Redis.
"""

import json
from typing import Any

from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from app.config import get_settings

settings = get_settings()


# Redis key prefixes
JOB_STATUS_PREFIX = "job:status:"
CACHE_RESULT_PREFIX = "cache:result:"
RATE_LIMIT_PREFIX = "rate_limit:"
ACTIVE_JOBS_PREFIX = "jobs:active:"
BATCH_PROGRESS_PREFIX = "batch:progress:"
CHANNEL_JOB_PREFIX = "channel:job:"


def get_redis() -> Redis:
    """Get synchronous Redis client.

    Returns:
        Redis: Synchronous Redis client.
    """
    return Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
    )


async def get_async_redis() -> AsyncRedis:
    """Get asynchronous Redis client.

    Returns:
        AsyncRedis: Asynchronous Redis client.
    """
    return AsyncRedis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
    )


class RedisCache:
    """Redis cache wrapper."""

    def __init__(self, redis: Redis) -> None:
        """Initialize Redis cache.

        Args:
            redis: Redis client instance.
        """
        self.redis = redis

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None.
        """
        value = self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds.

        Returns:
            bool: True if successful.
        """
        serialized = json.dumps(value)
        if ttl:
            return self.redis.setex(key, ttl, serialized)
        return self.redis.set(key, serialized)

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            bool: True if key was deleted.
        """
        return bool(self.redis.delete(key))

    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Cache key.

        Returns:
            bool: True if key exists.
        """
        return bool(self.redis.exists(key))

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter.

        Args:
            key: Counter key.
            amount: Amount to increment.

        Returns:
            int: New counter value.
        """
        return self.redis.incrby(key, amount)

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for key.

        Args:
            key: Cache key.
            ttl: Time to live in seconds.

        Returns:
            bool: True if successful.
        """
        return bool(self.redis.expire(key, ttl))

    def ttl(self, key: str) -> int:
        """Get remaining time to live.

        Args:
            key: Cache key.

        Returns:
            int: TTL in seconds, -1 if no expiry, -2 if key doesn't exist.
        """
        return self.redis.ttl(key)


class JobStatusCache:
    """Cache for storing job status and progress updates."""

    def __init__(self, cache: RedisCache) -> None:
        """Initialize job status cache.

        Args:
            cache: Redis cache instance.
        """
        self.cache = cache

    def set_status(
        self,
        job_id: str,
        status: str,
        progress: int | None = None,
        current_file: str | None = None,
        worker: str | None = None,
    ) -> None:
        """Set job status.

        Args:
            job_id: Job ID.
            status: Job status.
            progress: Progress percentage (0-100).
            current_file: Currently processing file.
            worker: Worker name.
        """
        key = f"{JOB_STATUS_PREFIX}{job_id}"
        data = {"status": status}

        if progress is not None:
            data["progress"] = progress
        if current_file:
            data["current_file"] = current_file
        if worker:
            data["worker"] = worker

        self.cache.set(key, data, ttl=3600)  # 1 hour

    def get_status(self, job_id: str) -> dict | None:
        """Get job status.

        Args:
            job_id: Job ID.

        Returns:
            Job status data or None.
        """
        key = f"{JOB_STATUS_PREFIX}{job_id}"
        return self.cache.get(key)


class RateLimitChecker:
    """Rate limiting using Redis."""

    def __init__(self, cache: RedisCache) -> None:
        """Initialize rate limit checker.

        Args:
            cache: Redis cache instance.
        """
        self.cache = cache

    def check_rate_limit(
        self,
        client_id: str,
        limit: int,
        period: int,
    ) -> tuple[bool, int]:
        """Check if client has exceeded rate limit.

        Args:
            client_id: Client ID.
            limit: Maximum requests allowed.
            period: Time period in seconds.

        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        key = f"{RATE_LIMIT_PREFIX}{client_id}"
        current = self.cache.redis.get(key)

        if current is None:
            self.cache.redis.setex(key, period, 1)
            return True, limit - 1

        count = int(current)
        if count >= limit:
            return False, 0

        self.cache.redis.incr(key)
        return True, limit - count - 1


class ActiveJobsTracker:
    """Track active jobs per client."""

    def __init__(self, cache: RedisCache) -> None:
        """Initialize active jobs tracker.

        Args:
            cache: Redis cache instance.
        """
        self.cache = cache

    def add_job(self, client_id: str, job_id: str) -> None:
        """Add active job.

        Args:
            client_id: Client ID.
            job_id: Job ID.
        """
        key = f"{ACTIVE_JOBS_PREFIX}{client_id}"
        self.cache.redis.sadd(key, job_id)

    def remove_job(self, client_id: str, job_id: str) -> None:
        """Remove active job.

        Args:
            client_id: Client ID.
            job_id: Job ID.
        """
        key = f"{ACTIVE_JOBS_PREFIX}{client_id}"
        self.cache.redis.srem(key, job_id)

    def count_jobs(self, client_id: str) -> int:
        """Count active jobs for client.

        Args:
            client_id: Client ID.

        Returns:
            int: Number of active jobs.
        """
        key = f"{ACTIVE_JOBS_PREFIX}{client_id}"
        return self.cache.redis.scard(key)


class BatchProgressTracker:
    """Track batch job progress."""

    def __init__(self, cache: RedisCache) -> None:
        """Initialize batch progress tracker.

        Args:
            cache: Redis cache instance.
        """
        self.cache = cache

    def set_progress(
        self,
        batch_id: str,
        total: int,
        completed: int,
        failed: int,
    ) -> None:
        """Set batch progress.

        Args:
            batch_id: Batch job ID.
            total: Total jobs.
            completed: Completed jobs.
            failed: Failed jobs.
        """
        key = f"{BATCH_PROGRESS_PREFIX}{batch_id}"
        data = {
            "total": total,
            "completed": completed,
            "failed": failed,
        }
        self.cache.set(key, data, ttl=86400)  # 24 hours

    def get_progress(self, batch_id: str) -> dict | None:
        """Get batch progress.

        Args:
            batch_id: Batch job ID.

        Returns:
            Batch progress data or None.
        """
        key = f"{BATCH_PROGRESS_PREFIX}{batch_id}"
        return self.cache.get(key)

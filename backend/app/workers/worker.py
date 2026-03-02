"""RQ Worker entry point.

Run with: python -m app.workers.worker
Or with RQ: rq worker --url redis://localhost:6379/0
"""

import sys
from redis import Redis
from rq import Worker

from app.config import get_settings

settings = get_settings()


def run_worker() -> None:
    """Run the RQ worker."""
    redis = Redis.from_url(settings.REDIS_URL)

    with Worker(
        [settings.RQ_QUEUE_NAME],
        connection=redis,
        name=f"worker-{settings.ENVIRONMENT}",
    ) as worker:
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    run_worker()

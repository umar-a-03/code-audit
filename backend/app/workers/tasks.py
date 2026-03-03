"""RQ Task definitions.

These functions can be enqueued and executed by RQ workers.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from rq import get_current_job
from sqlalchemy import select

from app.config import get_settings
from app.adapters.persistence.session import async_session_maker
from app.adapters.persistence.models.audit import AnalysisJob, AnalysisResult
from app.adapters.persistence.repositories import AnalysisJobRepository

settings = get_settings()
logger = logging.getLogger(__name__)


async def _update_job_status(job_id: str, status: str, error_message: str = None):
    """Update job status in database.

    Args:
        job_id: Job ID.
        status: New status.
        error_message: Optional error message.
    """
    async with async_session_maker() as session:
        repo = AnalysisJobRepository(session)
        job = await repo.get_by_id(uuid.UUID(job_id))
        if job:
            job.status = status
            if status == "running":
                job.started_at = datetime.now(timezone.utc)
            elif status in ["completed", "failed"]:
                job.completed_at = datetime.now(timezone.utc)
            if error_message:
                job.error_message = error_message
            await session.commit()
            logger.info(f"Updated job {job_id} status to {status}")
        else:
            logger.error(f"Job {job_id} not found when updating status")


async def _create_analysis_result(job_id: str, client_id: str, summary: dict):
    """Create analysis result in database.

    Args:
        job_id: Job ID.
        client_id: Client ID.
        summary: Analysis summary.
    """
    async with async_session_maker() as session:
        result = AnalysisResult(
            job_id=uuid.UUID(job_id),
            client_id=uuid.UUID(client_id),
            summary=summary,
        )
        session.add(result)
        await session.commit()
        logger.info(f"Created analysis result for job {job_id}")


async def _analyze_repository_async(
    job_id: str,
    repo_url: str,
    branch: str,
    client_id: str,
    options: dict,
) -> dict:
    """Async wrapper for repository analysis.

    Args:
        job_id: Analysis job ID.
        repo_url: Repository URL.
        branch: Branch to analyze.
        client_id: Client ID.
        options: Analysis options.

    Returns:
        Analysis results.
    """
    # Update status to running
    await _update_job_status(job_id, "running")

    # Step 1: Cloning repository
    logger.info(f"Cloning repository {repo_url}")
    await _update_job_status(job_id, "cloning")
    await asyncio.sleep(0.5)

    # Step 2: Scanning file tree
    logger.info("Scanning file tree")
    await _update_job_status(job_id, "scanning")
    await asyncio.sleep(0.5)

    # Step 3: Running rule engine
    logger.info("Running rule engine")
    await _update_job_status(job_id, "analyzing")
    await asyncio.sleep(0.5)

    # Step 4: AI review
    logger.info("Running AI review")
    await _update_job_status(job_id, "ai_review")
    await asyncio.sleep(0.5)

    # Step 5: Scoring
    logger.info("Calculating scores")
    await _update_job_status(job_id, "scoring")
    await asyncio.sleep(0.5)

    # Placeholder result
    result = {
        "job_id": job_id,
        "status": "completed",
        "summary": {
            "total_files": 42,
            "total_lines": 1500,
            "languages": {"python": 60, "javascript": 30, "html": 10},
            "quality_score": 75,
        },
    }

    # Create analysis result in database
    await _create_analysis_result(job_id, client_id, result["summary"])

    # Update status to completed
    await _update_job_status(job_id, "completed")

    logger.info(f"Completed analysis for {repo_url}")
    return result


def analyze_repository(
    job_id: str,
    repo_url: str,
    branch: str,
    client_id: str,
    options: dict,
) -> dict:
    """Analyze a repository (background task).

    Args:
        job_id: Analysis job ID.
        repo_url: Repository URL.
        branch: Branch to analyze.
        client_id: Client ID.
        options: Analysis options.

    Returns:
        Analysis results.
    """
    rq_job = get_current_job()
    if rq_job:
        rq_job.connection_id = str(uuid.uuid4())

    logger.info(f"Starting analysis for {repo_url} (branch: {branch})")

    try:
        # Run all async operations in a single event loop
        return asyncio.run(_analyze_repository_async(job_id, repo_url, branch, client_id, options))
    except Exception as e:
        logger.error(f"Analysis failed for {repo_url}: {e}", exc_info=True)
        # Update status to failed with error message in a new event loop (since the first one is gone)
        try:
            asyncio.run(_update_job_status(job_id, "failed", str(e)))
        except Exception as e2:
            logger.error(f"Failed to update job status to failed: {e2}", exc_info=True)
        raise


def generate_report(
    job_id: str,
    format_type: str = "markdown",
) -> str:
    """Generate audit report (background task).

    Args:
        job_id: Analysis job ID.
        format_type: Report format (markdown, html, json).

    Returns:
        Generated report content.
    """
    logger.info(f"Generating {format_type} report for job {job_id}")

    # TODO: Implement report generation:
    # 1. Fetch analysis results
    # 2. Format according to template
    # 3. Include charts/visualizations
    # 4. Add AI insights

    return f"# Audit Report\n\nJob ID: {job_id}\n\nAnalysis complete."


def batch_analyze(
    batch_id: str,
    repo_urls: list[str],
    client_id: str,
) -> dict:
    """Analyze multiple repositories in batch (background task).

    Args:
        batch_id: Batch job ID.
        repo_urls: List of repository URLs.
        client_id: Client ID.

    Returns:
        Batch results summary.
    """
    logger.info(f"Starting batch analysis {batch_id} with {len(repo_urls)} repositories")

    # TODO: Implement batch analysis:
    # 1. Create individual analysis jobs
    # 2. Track progress
    # 3. Aggregate results

    return {
        "batch_id": batch_id,
        "total_jobs": len(repo_urls),
        "completed_jobs": 0,
        "failed_jobs": 0,
    }

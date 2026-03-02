"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    service: str = settings.APP_NAME
    version: str = settings.APP_VERSION
    environment: str = settings.ENVIRONMENT


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Basic health check endpoint.

    Returns:
        HealthResponse: Service health status.
    """
    return HealthResponse()


@router.get("/health/ready", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def readiness_check() -> HealthResponse:
    """Readiness check - indicates if the service can handle requests.

    Returns:
        HealthResponse: Service readiness status.
    """
    # TODO: Add checks for database, Redis, etc.
    return HealthResponse(status="ready")


@router.get("/health/live", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def liveness_check() -> HealthResponse:
    """Liveness check - indicates if the container is still running.

    Returns:
        HealthResponse: Service liveness status.
    """
    return HealthResponse(status="alive")

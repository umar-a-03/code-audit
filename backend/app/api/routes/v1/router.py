"""API v1 router - aggregates all v1 endpoints."""

from fastapi import APIRouter

# Import route modules
import app.api.routes.v1.dashboard as dashboard
import app.api.routes.v1.audits as audits
import app.api.routes.v1.projects as projects
import app.api.routes.v1.api_keys as api_keys

router = APIRouter()

# Include route modules
router.include_router(dashboard.router)
router.include_router(audits.router)
router.include_router(projects.router)
router.include_router(api_keys.router)

# Placeholder endpoint to verify v1 router is working
@router.get("/")
async def v1_root() -> dict[str, str]:
    """V1 API root endpoint.

    Returns:
        dict: API information.
    """
    return {
        "message": "Code Audit API v1",
        "docs": "/docs",
    }

"""FastAPI application factory and configuration."""

import contextlib
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, status
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.routes.v1.router import router as v1_router
from app.api.routes.health import router as health_router
from app.api.exceptions import (
    add_exception_handlers,
    APIException,
    NotFoundException,
    BadRequestException,
)
from app.logging.config import setup_logging
from app.adapters.persistence.session import engine

settings = get_settings()

# Setup logging
setup_logging()
dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": settings.LOG_FORMAT,
                "use_colors": True,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": settings.LOG_LEVEL, "handlers": ["default"]},
    }
)

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Code Audit API...")

    # Verify database connection
    try:
        async with engine.begin() as conn:
            # Run a simple query to verify connection
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    # TODO: Initialize Redis connection
    # TODO: Verify migrations (optional - can be done separately)

    yield

    # Shutdown
    logger.info("Shutting down Code Audit API...")
    # Dispose database engine
    await engine.dispose()
    logger.info("Database connections closed")
    # TODO: Close Redis connections


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests."""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Status: {response.status_code}")
        return response

    # Exception handlers
    add_exception_handlers(app)

    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Create app instance
app = create_app()

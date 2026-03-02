"""Logging configuration."""

import logging
import sys

from app.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Setup application logging.

    Configures logging based on settings:
    - Console logging to stdout
    - Optional file logging
    - Log level based on DEBUG flag
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout)
    ]

    # Add file handler if configured
    if settings.LOG_FILE:
        handlers.append(logging.FileHandler(settings.LOG_FILE))

    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=handlers,
    )

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

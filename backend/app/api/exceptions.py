"""Custom exceptions and exception handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class APIException(Exception):
    """Base API exception."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Internal server error",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize API exception.

        Args:
            status_code: HTTP status code.
            message: Error message.
            details: Additional error details.
        """
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundException(APIException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize not found exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            details=details,
        )


class BadRequestException(APIException):
    """Bad request exception."""

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize bad request exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            details=details,
        )


class UnauthorizedException(APIException):
    """Unauthorized exception."""

    def __init__(
        self,
        message: str = "Unauthorized",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize unauthorized exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            details=details,
        )


class ForbiddenException(APIException):
    """Forbidden exception."""

    def __init__(
        self,
        message: str = "Forbidden",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize forbidden exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            details=details,
        )


class ConflictException(APIException):
    """Conflict exception."""

    def __init__(
        self,
        message: str = "Conflict",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize conflict exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            details=details,
        )


class ValidationException(APIException):
    """Validation exception."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize validation exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            details=details,
        )


class RateLimitException(APIException):
    """Rate limit exceeded exception."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize rate limit exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            details=details,
        )


class ServiceUnavailableException(APIException):
    """Service unavailable exception."""

    def __init__(
        self,
        message: str = "Service unavailable",
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize service unavailable exception.

        Args:
            message: Error message.
            details: Additional error details.
        """
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            details=details,
        )


def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        """Handle custom API exceptions.

        Args:
            request: FastAPI request.
            exc: API exception.

        Returns:
            JSONResponse: Error response.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(status.HTTP_404_NOT_FOUND)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle 404 not found errors.

        Args:
            request: FastAPI request.
            exc: Exception.

        Returns:
            JSONResponse: Error response.
        """
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "message": "The requested resource was not found",
                    "path": request.url.path,
                }
            },
        )

    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle 500 internal server errors.

        Args:
            request: FastAPI request.
            exc: Exception.

        Returns:
            JSONResponse: Error response.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "message": "An unexpected error occurred",
                }
            },
        )

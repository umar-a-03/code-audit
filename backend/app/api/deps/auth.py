"""FastAPI dependencies for authentication."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.adapters.persistence.models.client import Client as ClientModel
from app.adapters.persistence.repositories import ClientRepository
from app.dependencies import DBSessionDep


async def get_current_user(
    session: DBSessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> ClientModel:
    """Get the current authenticated user from JWT token.

    Verifies the JWT token and fetches the user from the database.

    Args:
        credentials: HTTP Bearer credentials from request.
        session: Database session.

    Returns:
        ClientModel: Authenticated client from database.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate JWT token
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token subject
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    client_repo = ClientRepository(session)
    client = await client_repo.get_by_id(user_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return client


# Dependency injection alias
CurrentUserDep = Annotated[ClientModel, Depends(get_current_user)]

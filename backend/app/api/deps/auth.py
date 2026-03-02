"""FastAPI dependencies for authentication."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import create_client, Client as SupabaseClient

from app.config import get_settings
from app.adapters.persistence.models.client import Client as ClientModel
from app.adapters.persistence.repositories import ClientRepository
from app.dependencies import DBSessionDep

settings = get_settings()

# Supabase client for token verification
supabase = create_client(
    settings.SUPABASE_URL or "",
    settings.SUPABASE_SERVICE_ROLE_KEY or "",
)


async def get_current_user(
    session: DBSessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> ClientModel:
    """Get the current authenticated user from Supabase JWT token.

    Verifies the JWT token from Supabase and fetches/creates the user info
    in the database.

    Args:
        credentials: HTTP Bearer credentials from request.
        session: Database session.

    Returns:
        ClientModel: Authenticated client from database.

    Raises:
        HTTPException: 401 if token is invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        # Verify JWT and get user from Supabase
        user_response = await supabase.auth.get_user(
            jwt=credentials.credentials,
        )

        if not user_response.data.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        # Get user data from Supabase
        user = user_response.data.user
        email = user.email
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found in user profile",
            )

        # Get or create client record in database
        client_repo = ClientRepository(session)
        client = await client_repo.get_or_create_by_oauth(
            oauth_id=user.id,
            email=email,
            name=user.user_metadata.get("name", email.split("@")[0]),
            oauth_provider="google",
        )

        return client

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )


# Dependency injection alias
CurrentUserDep = Annotated[ClientModel, Depends(get_current_user)]

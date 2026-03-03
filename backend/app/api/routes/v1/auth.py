"""Authentication routes for login, register, and user management."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.api.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
)
from app.api.deps.auth import CurrentUserDep
from app.adapters.persistence.repositories import ClientRepository
from app.dependencies import DBSessionDep

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: DBSessionDep,
) -> AuthResponse:
    """Register a new user with email and password.

    Args:
        request: Registration request with email, password, and optional name.
        session: Database session.

    Returns:
        AuthResponse: JWT token and user data.

    Raises:
        HTTPException: 400 if email already registered.
    """
    client_repo = ClientRepository(session)

    # Check if user already exists
    existing_client = await client_repo.get_by_email(request.email)
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user with hashed password
    password_hash = get_password_hash(request.password)
    client = await client_repo.create_with_password(
        email=request.email,
        password_hash=password_hash,
        name=request.name,
    )

    # Generate access token
    access_token = create_access_token(
        data={"sub": str(client.id)},
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=client.id,
            email=client.email,
            name=client.name,
            is_active=client.is_active,
            created_at=client.created_at,
            updated_at=client.updated_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    session: DBSessionDep,
) -> AuthResponse:
    """Login with email and password.

    Args:
        request: Login request with email and password.
        session: Database session.

    Returns:
        AuthResponse: JWT token and user data.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    client_repo = ClientRepository(session)

    # Get user by email
    client = await client_repo.get_by_email(request.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not client.password_hash or not verify_password(request.password, client.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(
        data={"sub": str(client.id)},
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=client.id,
            email=client.email,
            name=client.name,
            is_active=client.is_active,
            created_at=client.created_at,
            updated_at=client.updated_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token.

    Returns:
        UserResponse: Current user data.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout the current user.

    Since JWT tokens are stateless, the client is responsible for
    removing the token from local storage. This endpoint provides
    a consistent API for logout operations.

    Returns:
        dict: Success message.
    """
    return {"message": "Successfully logged out"}

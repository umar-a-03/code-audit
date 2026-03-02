"""API Keys API endpoints.

Manages user API keys for AI providers (OpenAI, Anthropic, etc.).
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status as status

from app.api.deps.auth import CurrentUserDep
from app.api.schemas.api_key import (
    CreateApiKeyRequest,
    ApiKeyResponse,
    ApiKeyListResponse,
)
from app.core.services.api_key import ApiKeyService
from app.api.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.get("", response_model=list[ApiKeyListResponse])
async def list_api_keys(
    current_user: CurrentUserDep,
) -> list[ApiKeyListResponse]:
    """List all API keys for the current user.

    Returns:
        list[ApiKeyListResponse]: List of API keys (masked).
    """
    api_key_service = ApiKeyService()
    keys = await api_key_service.list_keys(current_user.id)

    return [
        ApiKeyListResponse(
            id=key["id"],
            provider=key["provider"],
            key_name=key["key_name"],
            is_active=key["is_active"],
            created_at=key["created_at"],
            last_used_at=key["last_used_at"],
            key_preview=key["key_preview"],
        )
        for key in keys
    ]


@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: CreateApiKeyRequest,
    current_user: CurrentUserDep,
) -> ApiKeyResponse:
    """Store a new API key (encrypted at rest).

    Args:
        request: API key creation data.

    Returns:
        ApiKeyResponse: Created API key info.

    Raises:
        HTTPException: 400 if validation fails, 409 if key already exists.
    """
    api_key_service = ApiKeyService()

    try:
        api_key = await api_key_service.create_key(
            client_id=current_user.id,
            provider=request.provider,
            key=request.key.get_secret_value(),
            key_name=request.key_name,
        )
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return ApiKeyResponse(
        id=api_key.id,
        client_id=api_key.client_id,
        provider=api_key.provider,
        key_name=api_key.key_name,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        key_hash=api_key.key_hash,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    current_user: CurrentUserDep,
):
    """Delete an API key.

    Args:
        key_id: API key ID.

    Raises:
        HTTPException: 404 if key not found.
    """
    api_key_service = ApiKeyService()

    try:
        success = await api_key_service.delete_key(key_id, current_user.id)
        if not success:
            raise NotFoundException("API key not found")
    except ValueError as e:
        if "not found" in str(e):
            raise NotFoundException(str(e))
        raise

"""API Key schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, SecretStr, HttpUrl


class CreateApiKeyRequest(BaseModel):
    """Request schema for creating an API key."""

    provider: Literal["openai", "anthropic", "gemini", "github"] = Field(
        ..., description="AI provider"
    )
    key: SecretStr = Field(..., description="API key (will be encrypted)")
    key_name: Optional[str] = Field(None, max_length=100)


class ApiKeyResponse(BaseModel):
    """Response schema for an API key."""

    id: UUID
    client_id: UUID
    provider: str
    key_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    # Never expose the actual key in responses
    key_hash: str


class ApiKeyListResponse(BaseModel):
    """Response schema for API key list."""

    id: UUID
    provider: str
    key_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    # Masked key preview (first 4 chars only)
    key_preview: str  # e.g., "sk-***"

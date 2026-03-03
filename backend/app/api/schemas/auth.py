"""Authentication schemas for request/response validation."""

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    name: Optional[str] = Field(None, max_length=255, description="User display name")


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: UUID
    email: str
    name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserResponse = Field(..., description="Authenticated user data")


class AuthErrorResponse(BaseModel):
    """Response schema for authentication errors."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")

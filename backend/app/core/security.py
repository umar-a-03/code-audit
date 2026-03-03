"""Security utilities for password hashing and JWT token handling."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Password hashing context - use argon2 which supports longer passwords
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify.
        hashed_password: The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using argon2.

    Args:
        password: The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: The data to encode in the token (typically {'sub': user_id}).
        expires_delta: Optional custom expiration time delta.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode.

    Returns:
        dict | None: The decoded token payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a JWT refresh token with longer expiration.

    Args:
        data: The data to encode in the token (typically {'sub': user_id}).

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt

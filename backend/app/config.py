"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Code Audit API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered code audit platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/codeaudit",
        description="Async PostgreSQL database URL",
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for queue and cache",
    )
    REDIS_DB: int = 0
    REDIS_CACHE_DB: int = 1
    REDIS_MAX_CONNECTIONS: int = 50

    # Security
    SECRET_KEY: SecretStr = Field(
        default="change-me-in-production-use-openssl-rand-hex-32",
        description="Secret key for JWT encoding",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Encryption (for API keys)
    ENCRYPTION_KEY: SecretStr = Field(
        default="change-me-in-production-use-32-byte-url-safe-base64",
        description="Fernet key for encrypting sensitive data",
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:5174", "http://localhost:5172", "http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"])

    # File Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    UPLOAD_DIR: str = "./uploads"
    STORAGE_MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # AWS S3 (if using S3 storage)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: SecretStr | None = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str | None = None

    # Worker Settings
    RQ_QUEUE_NAME: str = "default"
    RQ_JOB_TIMEOUT: int = 3600  # 1 hour
    RQ_RESULT_TTL: int = 86400  # 24 hours
    RQ_FAILURE_TTL: int = 86400  # 24 hours

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Analysis Settings
    MAX_CONCURRENT_JOBS_PER_CLIENT: int = 5
    ANALYSIS_TIMEOUT_SECONDS: int = 3600
    MAX_REPO_SIZE_MB: int = 500
    ALLOWED_FILE_EXTENSIONS: list[str] = [
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".kt",
        ".go",
        ".rs",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".php",
        ".rb",
        ".swift",
        ".scala",
        ".sh",
        ".yaml",
        ".yml",
        ".json",
        ".xml",
        ".sql",
        ".md",
        ".txt",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_FILE: str | None = None

    # Feature Flags
    ENABLE_BATCH_ANALYSIS: bool = True
    ENABLE_SCHEDULING: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Cached application settings.
    """
    return Settings()


# For direct access
settings = get_settings()

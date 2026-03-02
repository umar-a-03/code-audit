# Code Audit Backend

FastAPI backend for the Code Audit Platform - an AI-powered code analysis platform.

## Architecture

This backend follows **Hexagonal (Ports & Adapters) Architecture** for scalability and maintainability:

```
app/
├── api/              # API Layer - Routes, schemas, middleware
├── core/             # Domain Layer - Business logic, entities, ports
├── adapters/         # Infrastructure - Database, AI, VCS, cache implementations
├── workers/          # Background job processors
├── security/         # Authentication, authorization, encryption
├── logging/          # Logging configuration
└── utils/            # Utility functions
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Poetry

### Installation

```bash
# Install dependencies
poetry install

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Running Locally

```bash
# Start database and Redis (via Docker)
docker-compose up -d db redis

# Run database migrations
alembic upgrade head

# Start API server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start worker (in another terminal)
poetry run python -m app.workers.worker
```

### Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See [`.env.example`](.env.example) for all available options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `ENCRYPTION_KEY` - For encrypting API keys
- `GITHUB_CLIENT_ID/SECRET` - OAuth credentials
- `GOOGLE_CLIENT_ID/SECRET` - OAuth credentials

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## Running Workers

```bash
# Single worker
poetry run python -m app.workers.worker

# Multiple workers with different names
poetry run rq worker --url redis://localhost:6379/0 --name worker-1 &
poetry run rq worker --url redis://localhost:6379/0 --name worker-2 &
```

## Development

### Code Quality

```bash
# Format code
poetry run black app/
poetry run isort app/

# Lint
poetry run ruff check app/

# Type check
poetry run mypy app/
```

### Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_audit.py
```

## Project Structure

### API Layer (`app/api/`)
- `routes/` - API endpoints organized by version and resource
- `schemas/` - Pydantic models for request/response validation
- `deps/` - FastAPI dependency injection
- `middleware.py` - CORS, logging, auth middleware
- `exceptions.py` - Custom exception handlers

### Domain Layer (`app/core/`)
- `domain/` - Business entities and value objects
- `services/` - Business logic / use cases
- `ports/` - Abstract interfaces for external dependencies

### Adapters (`app/adapters/`)
- `persistence/` - PostgreSQL ORM models and repositories
- `ai/` - AI provider implementations (OpenAI, Anthropic)
- `vcs/` - Version control adapters (GitHub, GitLab)
- `cache/` - Redis cache implementation
- `queue/` - RQ queue wrapper
- `storage/` - File storage (local, S3)

### Workers (`app/workers/`)
- `worker.py` - RQ worker entry point
- `tasks.py` - Task definitions
- `jobs/` - Specific job implementations

## Adding New Features

### New API Endpoint

1. Create schema in `app/api/schemas/`
2. Create route in `app/api/routes/v1/`
3. Register in `app/api/routes/v1/router.py`
4. Create service in `app/core/services/`
5. Create repository in `app/adapters/persistence/repositories/`

### New AI Provider

1. Create adapter in `app/adapters/ai/{provider}.py`
2. Implement `AIProvider` protocol from `app/core/ports/ai_provider.py`
3. Register in `app/adapters/ai/factory.py`

### New VCS Platform

1. Create adapter in `app/adapters/vcs/{platform}.py`
2. Implement `VCSProvider` protocol from `app/core/ports/vcs.py`
3. Register in `app/adapters/vcs/factory.py`

## License

MIT

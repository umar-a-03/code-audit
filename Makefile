# Code Audit Platform - Makefile
# Convenient commands for development and deployment

.PHONY: help build up down restart logs clean install db-migrate db-shell test lint

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Docker compose command
COMPOSE := docker compose
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml

## ===========================================
## Help
## ===========================================

help: ## Show this help message
	@echo '$(BLUE)Code Audit Platform - Available Commands$(NC)'
	@echo ''
	@echo '$(YELLOW)Quick Start:$(NC)'
	@echo '  1. $(YELLOW)make setup$(NC)         - Create .env files'
	@echo '  2. Edit .env files with your Supabase credentials'
	@echo '  3. $(YELLOW)make up-docker-dev$(NC) - Start everything with hot reload'
	@echo ''
	@echo '$(BLUE)✨ Docker handles:$(NC) dependencies, migrations, startup'
	@echo ''
	@echo '$(GREEN)Docker Commands:$(NC)'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | grep -E 'Docker|up|down|restart|logs|clean'
	@echo ''
	@echo '$(GREEN)Database Commands:$(NC)'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | grep -E 'db-|migrate'
	@echo ''
	@echo '$(GREEN)Development Commands:$(NC)'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' | grep -E 'dev|install|test|lint'

## ===========================================
## Docker Commands
## ===========================================

up: ## Start all services (migrations run automatically)
	@echo '$(BLUE)Starting all services...$(NC)'
	$(COMPOSE) up -d --build
	@echo '$(GREEN)Services started!$(NC)'
	@echo '  Backend:  http://localhost:8080'
	@echo '  Frontend: http://localhost:5164'
	@echo '  API Docs: http://localhost:8000/docs'
	@echo '  Redis UI: http://localhost:8081 (with --profile tools)'
	@echo ''
	@echo '$(YELLOW)Note:$(NC) Migrations run automatically on startup'

up-dev: ## Start services in development mode with hot reload
	@echo '$(BLUE)Starting development services...$(NC)'
	$(COMPOSE) up -d postgres redis
	@echo '$(GREEN)Database services started!$(NC)'
	@echo 'Run $(YELLOW)make dev$(NC) to start backend and frontend with hot reload'

up-docker-dev: ## Start ALL services in Docker with hot reload (migrations automatic)
	@echo '$(BLUE)Starting all services in Docker with hot reload...$(NC)'
	$(COMPOSE_DEV) up  --build
	@echo '$(GREEN)Services started with hot reload!$(NC)'
	@echo '  Backend:  http://localhost:8080 (auto-reload on code change)'
	@echo '  Frontend: http://localhost:5164 (Vite HMR)'
	@echo ''
	@echo '$(YELLOW)Note:$(NC) Migrations run automatically on startup'

down: ## Stop all services
	@echo '$(BLUE)Stopping all services...$(NC)'
	$(COMPOSE) down

restart: ## Restart all services
	@echo '$(BLUE)Restarting all services...$(NC)'
	$(COMPOSE) restart

logs: ## Show logs from all services (follow mode)
	$(COMPOSE) logs -f

logs-backend: ## Show backend logs
	$(COMPOSE) logs -f api

logs-frontend: ## Show frontend logs
	$(COMPOSE) logs -f frontend

logs-db: ## Show database logs
	$(COMPOSE) logs -f postgres

logs-dev: ## Show logs for docker-dev services
	$(COMPOSE_DEV) logs -f

ps: ## Show running containers
	$(COMPOSE) ps

ps-dev: ## Show running containers in dev mode
	$(COMPOSE_DEV) ps

down-dev: ## Stop docker-dev services
	@echo '$(BLUE)Stopping development services...$(NC)'
	$(COMPOSE_DEV) down
	$(COMPOSE) ps

clean: ## Stop and remove all containers, volumes, and images
	@echo '$(RED)Cleaning up all resources...$(NC)'
	$(COMPOSE) down -v --remove-orphans
	@echo '$(GREEN)Cleanup complete!$(NC)'

clean-volumes: ## Remove all volumes (WARNING: deletes all data)
	@echo '$(RED)Removing all volumes...$(NC)'
	docker volume rm code-audit-postgres_data code-audit-redis_data code-audit-uploads_data code-audit-repos_data 2>/dev/null || true
	@echo '$(GREEN)Volumes removed!$(NC)'

## ===========================================
## Database Commands
## ===========================================

db-migrate: ## Run database migrations
	@echo '$(BLUE)Running database migrations...$(NC)'
	cd $(BACKEND_DIR) && alembic upgrade head
	@echo '$(GREEN)Migrations complete!$(NC)'

db-rollback: ## Rollback last migration
	@echo '$(BLUE)Rolling back last migration...$(NC)'
	cd $(BACKEND_DIR) && alembic downgrade -1
	@echo '$(GREEN)Rollback complete!$(NC)'

db-reset: ## Reset database (drop and recreate all tables)
	@echo '$(RED)Resetting database...$(NC)'
	cd $(BACKEND_DIR) && alembic downgrade base
	$(MAKE) db-migrate
	@echo '$(GREEN)Database reset complete!$(NC)'

db-shell: ## Open PostgreSQL shell
	docker exec -it code-audit-db psql -U postgres -d codeaudit

db-migrations: ## Create a new migration (usage: make db-migrations NAME="add_users_table")
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m $(NAME)

## ===========================================
## Development Commands
## ===========================================

dev: ## Start backend and frontend in development mode (hot reload)
	@echo '$(BLUE)Starting development servers...$(NC)'
	@tmux new-session -d -s codeaudit \; \
		send-keys 'cd $(BACKEND_DIR) && poetry run uvicorn app.main:app --reload --host 0.0.0.0' C-m \; \
		split-window -h \; \
		send-keys 'cd $(FRONTEND_DIR) && npm run dev' C-m \; \
		attach-session
	@echo '$(GREEN)Development servers started in tmux!$(NC)'
	@echo 'Press Ctrl+B then D to detach'

dev-backend: ## Start only backend in development mode
	@echo '$(BLUE)Starting backend development server...$(NC)'
	cd $(BACKEND_DIR) && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start only frontend in development mode
	@echo '$(BLUE)Starting frontend development server...$(NC)'
	cd $(FRONTEND_DIR) && npm run dev

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo '$(BLUE)Installing backend dependencies...$(NC)'
	cd $(BACKEND_DIR) && poetry install
	@echo '$(GREEN)Backend dependencies installed!$(NC)'

install-frontend: ## Install frontend dependencies
	@echo '$(BLUE)Installing frontend dependencies...$(NC)'
	cd $(FRONTEND_DIR) && npm install
	@echo '$(GREEN)Frontend dependencies installed!$(NC)'

## ===========================================
## Testing Commands
## ===========================================

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo '$(BLUE)Running backend tests...$(NC)'
	cd $(BACKEND_DIR) && poetry run pytest

test-frontend: ## Run frontend tests
	@echo '$(BLUE)Running frontend tests...$(NC)'
	cd $(FRONTEND_DIR) && npm test

test-coverage: ## Run backend tests with coverage report
	@echo '$(BLUE)Running backend tests with coverage...$(NC)'
	cd $(BACKEND_DIR) && poetry run pytest --cov=app --cov-report=html --cov-report=term

## ===========================================
## Linting Commands
## ===========================================

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Run backend linter (ruff)
	@echo '$(BLUE)Linting backend code...$(NC)'
	cd $(BACKEND_DIR) && poetry run ruff check app/
	@echo '$(GREEN)Backend linting complete!$(NC)'

lint-frontend: ## Run frontend linter (eslint)
	@echo '$(BLUE)Linting frontend code...$(NC)'
	cd $(FRONTEND_DIR) && npm run lint
	@echo '$(GREEN)Frontend linting complete!$(NC)'

format-backend: ## Format backend code with ruff
	@echo '$(BLUE)Formatting backend code...$(NC)'
	cd $(BACKEND_DIR) && poetry run ruff check --fix app/
	cd $(BACKEND_DIR) && poetry run black app/
	@echo '$(GREEN)Backend code formatted!$(NC)'

format-frontend: ## Format frontend code with eslint
	@echo '$(BLUE)Formatting frontend code...$(NC)'
	cd $(FRONTEND_DIR) && npm run lint -- --fix
	@echo '$(GREEN)Frontend code formatted!$(NC)'

## ===========================================
## Build Commands
## ===========================================

build: build-backend build-frontend ## Build all Docker images

build-backend: ## Build backend Docker image
	@echo '$(BLUE)Building backend Docker image...$(NC)'
	$(COMPOSE) build api
	@echo '$(GREEN)Backend image built!$(NC)'

build-frontend: ## Build frontend Docker image
	@echo '$(BLUE)Building frontend Docker image...$(NC)'
	$(COMPOSE) build frontend
	@echo '$(GREEN)Frontend image built!$(NC)'

rebuild: ## Rebuild all images without cache
	@echo '$(BLUE)Rebuilding all images...$(NC)'
	$(COMPOSE) build --no-cache
	@echo '$(GREEN)Images rebuilt!$(NC)'

build-dev: ## Build development images
	@echo '$(BLUE)Building development images...$(NC)'
	$(COMPOSE_DEV) build
	@echo '$(GREEN)Development images built!$(NC)'

rebuild-dev: ## Rebuild development images without cache
	@echo '$(BLUE)Rebuilding development images...$(NC)'
	$(COMPOSE_DEV) build --no-cache
	@echo '$(GREEN)Development images rebuilt!$(NC)'

## ===========================================
## Production Commands
## ===========================================

prod-up: ## Start production services
	@echo '$(BLUE)Starting production services...$(NC)'
	$(COMPOSE) --profile production up -d

prod-build: ## Build production images
	@echo '$(BLUE)Building production images...$(NC)'
	$(COMPOSE) --profile production build

prod-deploy: prod-build prod-up ## Build and deploy production
	@echo '$(GREEN)Production deployed!$(NC)'

## ===========================================
## Utility Commands
## ===========================================

shell-backend: ## Open shell in backend container
	docker exec -it code-audit-api sh

shell-frontend: ## Open shell in frontend container
	docker exec -it code-audit-frontend sh

shell-db: ## Open shell in database container
	docker exec -it code-audit-db sh

setup: ## Initial project setup (creates .env files)
	@echo '$(BLUE)Running initial setup...$(NC)'
	@echo '1. Creating .env files from examples...'
	@test -f $(BACKEND_DIR)/.env || cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env
	@test -f $(FRONTEND_DIR)/.env || cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env
	@echo '$(GREEN)✓$(NC) .env files created'
	@echo ''
	@echo '$(YELLOW)NOTE:$(NC) Docker handles migrations automatically on startup!'
	@echo ''
	@echo 'Next steps:'
	@echo '  1. Edit backend/.env and frontend/.env with your credentials'
	@echo '  2. Configure Supabase (see docs/SUPABASE_SETUP.md)'
	@echo '  3. Run $(YELLOW)make up$(NC) or $(YELLOW)make up-docker-dev$(NC)'
	@echo ''
	@echo 'That'\''s it! Migrations, dependencies - everything is automatic.'

setup-local: ## Setup for local development (non-Docker)
	@echo '$(BLUE)Setting up local development environment...$(NC)'
	@echo '1. Creating .env files...'
	@test -f $(BACKEND_DIR)/.env || cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env
	@test -f $(FRONTEND_DIR)/.env || cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env
	@echo '2. Installing dependencies locally...'
	$(MAKE) install
	@echo '3. Starting database services...'
	$(COMPOSE) up -d postgres redis
	@echo '4. Running migrations...'
	@sleep 3
	$(MAKE) db-migrate
	@echo '$(GREEN)Local setup complete!$(NC)'
	@echo 'Run $(YELLOW)make dev$(NC) to start backend and frontend locally'

check-env: ## Check if .env files exist and show status
	@echo '$(BLUE)Checking environment files...$(NC)'
	@test -f $(BACKEND_DIR)/.env && echo '  $(GREEN)✓$(NC) backend/.env exists' || echo '  $(RED)✗$(NC) backend/.env missing'
	@test -f $(FRONTEND_DIR)/.env && echo '  $(GREEN)✓$(NC) frontend/.env exists' || echo '  $(RED)✗$(NC) frontend/.env missing'
	@echo ''
	@test -f $(BACKEND_DIR)/.env && test -f $(FRONTEND_DIR)/.env || \
		echo '$(YELLOW)Run: make setup$(NC) to create .env files from examples'
	@test -f $(BACKEND_DIR)/.env && test -f $(FRONTEND_DIR)/.env || exit 1
	@echo '$(GREEN)All environment files ready!$(NC)'

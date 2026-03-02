# Code Audit Platform - Makefile

.PHONY: help setup dev prod up down logs db-migrate test lint clean install

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend

COMPOSE := docker compose

help:
	@echo 'Available commands:'
	@echo '  setup      - Create .env files from examples'
	@echo '  dev        - Start development services (hot reload)'
	@echo '  dev-restart - Clean restart dev services (fixes port conflicts)'
	@echo '  prod       - Start production services'
	@echo '  up         - Start all services'
	@echo '  down       - Stop all services'
	@echo '  logs       - Show logs (follow mode)'
	@echo '  db-migrate - Run database migrations'
	@echo '  db-shell   - Open PostgreSQL shell'
	@echo '  install    - Install all dependencies'
	@echo '  test       - Run all tests'
	@echo '  lint       - Run all linters'
	@echo '  clean      - Remove containers and volumes'

setup:
	@test -f $(BACKEND_DIR)/.env || cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env
	@test -f $(FRONTEND_DIR)/.env || cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env
	@echo '.env files created. Edit them with your credentials.'

dev:
	@echo 'Starting development services...'
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up --build

prod:
	@echo 'Starting production services...'
	$(COMPOSE) --profile production up -d --build

up:
	@echo 'Starting all services...'
	$(COMPOSE) up -d

down:
	@echo 'Stopping all services...'
	$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml down --remove-orphans || true
	$(COMPOSE) down --remove-orphans || true

logs:
	$(COMPOSE) logs -f

db-migrate:
	cd $(BACKEND_DIR) && alembic upgrade head

db-shell:
	docker exec -it code-audit-db psql -U postgres -d codeaudit

install:
	cd $(BACKEND_DIR) && poetry install
	cd $(FRONTEND_DIR) && npm install

test:
	cd $(BACKEND_DIR) && poetry run pytest
	cd $(FRONTEND_DIR) && npm test

lint:
	cd $(BACKEND_DIR) && poetry run ruff check app/
	cd $(FRONTEND_DIR) && npm run lint

clean:
	@echo 'Cleaning up...'
	$(COMPOSE) down -v --remove-orphans

clean-all: ## Clean everything including networks (fixes persistent port issues)
	@echo 'Deep cleaning...'
	$(COMPOSE) down -v --remove-orphans
	docker network prune -f
	docker container prune -f

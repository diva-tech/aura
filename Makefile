.PHONY: help build up down logs clean test lint format install requirements

# Default target
.DEFAULT_GOAL := help

PYTHON := python3
DOCKER_COMPOSE := docker-compose

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)AURA v1.0 - Local Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  make up              # Start all services (equiv: docker-compose up -d)"
	@echo "  make down            # Stop all services"
	@echo "  make logs            # View service logs"
	@echo "  make test            # Run all tests"
	@echo ""

# Docker Compose Commands
up: ## Start all services (docker-compose up -d)
	@echo "$(GREEN)Starting AURA services...$(NC)"
	$(DOCKER_COMPOSE) build --quiet
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Services started!$(NC)"
	@echo "   Dashboard: http://localhost:8000"
	@echo "   API Docs:  http://localhost:8000/docs"

down: ## Stop all services
	@echo "$(GREEN)Stopping AURA services...$(NC)"
	$(DOCKER_COMPOSE) down

restart: down up ## Restart all services

logs: ## View service logs (-f for follow)
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## View backend logs only
	$(DOCKER_COMPOSE) logs -f backend

logs-db: ## View database logs only
	$(DOCKER_COMPOSE) logs -f postgres

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

build: ## Build Docker images
	$(DOCKER_COMPOSE) build

# Development Commands
shell-backend: ## Open shell in backend container
	$(DOCKER_COMPOSE) exec backend bash

shell-db: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) exec postgres psql -U aura -d aura

redis-cli: ## Open Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

# Testing
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	cd apps/backend && $(PYTHON) -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	cd apps/backend && $(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	cd apps/backend && $(PYTHON) -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	cd apps/backend && $(PYTHON) -m pytest tests/integration/ -v

test-watch: ## Run tests in watch mode (requires pytest-watch)
	cd apps/backend && ptw tests/

# Linting & Formatting
lint: ## Run linters (ruff, mypy)
	@echo "$(GREEN)Linting code...$(NC)"
	cd apps/backend && ruff check src/ tests/
	cd apps/backend && mypy src/

format: ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(NC)"
	cd apps/backend && ruff format src/ tests/
	cd apps/backend && ruff check --fix src/ tests/

check: lint test ## Run lints and tests

# Setup & Installation
install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	cd apps/backend && pip install -e ".[dev]"

requirements: ## Generate requirements.txt
	cd apps/backend && pip freeze > requirements.txt

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	cd apps/backend && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	cd apps/backend && alembic revision --autogenerate -m "$(MSG)"

# Database Commands
db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)WARNING: This will destroy all database data!$(NC)"
	@read -p "Are you sure? (yes/no) " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(DOCKER_COMPOSE) exec -T postgres psql -U aura -d aura -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	fi

db-seed: ## Seed database with sample data
	@echo "$(GREEN)Seeding database...$(NC)"
	cd apps/backend && $(PYTHON) -c "from scripts.seed import seed_database; seed_database()"

# Documentation
docs: ## Generate API documentation
	@echo "$(GREEN)Documentation is available at http://localhost:8000/docs$(NC)"

docs-build: ## Build documentation
	cd docs && make html

# Cleanup
clean: ## Clean up temporary files and caches
	@echo "$(GREEN)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-all: clean down ## Clean everything and stop services
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✅ Complete cleanup done$(NC)"

# Git & CI
lint-commit: ## Lint staged files (pre-commit hook)
	cd apps/backend && pre-commit run --all-files

git-setup: ## Setup git hooks
	pre-commit install

# Development Utilities
validate: ## Validate docker-compose.yml
	$(DOCKER_COMPOSE) config

version: ## Show AURA version
	@grep "APPLICATION_VERSION" apps/backend/src/aura_backend/main.py

env-check: ## Check if required env vars are set
	@echo "$(BLUE)Checking environment...$(NC)"
	@command -v docker >/dev/null 2>&1 || (echo "$(RED)✗ Docker not found$(NC)" && exit 1)
	@command -v docker-compose >/dev/null 2>&1 || (echo "$(RED)✗ Docker Compose not found$(NC)" && exit 1)
	@echo "$(GREEN)✅ Environment check passed$(NC)"

# Development with Local Run Script
run: ## Start AURA using ./run.sh
	@if [ -f run.sh ]; then bash run.sh; else echo "$(RED)run.sh not found$(NC)"; fi

run-win: ## Start AURA using ./run.ps1 (Windows)
	@if exist run.ps1 (powershell -ExecutionPolicy Bypass -File run.ps1) else (echo "$(RED)run.ps1 not found$(NC)")

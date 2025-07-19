# ============================================================================
# Makefile - Build Automation
# ============================================================================

# Create: Makefile
.PHONY: help install dev test build docker clean deploy

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)AI Knowledge Library - Available Commands$(NC)"
	@echo "$(YELLOW)==========================================$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

dev: ## Run development server
	@echo "$(BLUE)Starting development server...$(NC)"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-docker: ## Run development with Docker
	@echo "$(BLUE)Starting development with Docker...$(NC)"
	docker-compose up --build

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v

lint: ## Run code linting
	@echo "$(BLUE)Running code linting...$(NC)"
	flake8 app/ tests/
	black app/ tests/ --check
	isort app/ tests/ --check-only
	mypy app/

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	black app/ tests/
	isort app/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Docker images built$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Containers started$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Containers stopped$(NC)"

docker-logs: ## Show Docker logs
	docker-compose logs -f

init-db: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	python scripts/init_db.py
	@echo "$(GREEN)✅ Database initialized$(NC)"

load-sample-data: ## Load sample data
	@echo "$(BLUE)Loading sample data...$(NC)"
	python scripts/load_sample_data.py
	@echo "$(GREEN)✅ Sample data loaded$(NC)"

backup-db: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	python scripts/backup_data.py
	@echo "$(GREEN)✅ Database backed up$(NC)"

clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	pip-audit
	bandit -r app/

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)Deploying to staging...$(NC)"
	docker-compose -f docker-compose.staging.yml up -d --build
	@echo "$(GREEN)✅ Deployed to staging$(NC)"

deploy-prod: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "$(GREEN)✅ Deployed to production$(NC)"

health-check: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	curl -f http://localhost:8000/health/ || echo "$(RED)❌ Health check failed$(NC)"

setup: install init-db load-sample-data ## Complete setup (install + init + sample data)
	@echo "$(GREEN)🎉 Setup completed! Run 'make dev' to start the server$(NC)"

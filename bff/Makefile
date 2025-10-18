# Makefile for Connet.AI BFF Development
.PHONY: help install test lint format docker-build docker-start docker-start-full docker-stop docker-clean docker-restart docker-status docker-shell docker-test docker-test-quick debug-start debug-stop debug-logs debug-clean

# Default target
help:
	@echo "Connet.AI BFF - Available Commands:"
	@echo ""
	@echo "🐍 Python/FastAPI:"
	@echo "  install         - Install Python dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black and isort"
	@echo "  run            - Run development server locally"
	@echo ""
	@echo "🐳 Docker (Full Environment):"
	@echo "  docker-build    - Build all Docker images"
	@echo "  docker-start    - Start all services (BFF + DB + Redis + MailHog)"
	@echo "  docker-start-full - Start all services and show logs"
	@echo "  docker-stop     - Stop all Docker services"
	@echo "  docker-clean    - Clean Docker containers and volumes"
	@echo "  docker-restart  - Restart all services"
	@echo "  docker-status   - Show Docker containers status"
	@echo "  docker-shell    - Open shell in BFF container"
	@echo "  docker-test     - Test all Docker services"
	@echo "  docker-test-quick - Quick Docker health check"
	@echo ""
	@echo "🔧 Debug Environment (DB + Redis only):"
	@echo "  debug-start     - Start PostgreSQL + Redis for local debugging"
	@echo "  debug-stop      - Stop debug environment"
	@echo "  debug-logs      - Show debug environment logs"
	@echo "  debug-clean     - Clean debug environment (remove data)"
	@echo ""
	@echo "📋 Database:"
	@echo "  db-migrate      - Run database migrations"
	@echo "  db-reset        - Reset database (WARNING: deletes all data)"
	@echo "  db-shell        - Open database shell"
	@echo ""
	@echo "🌍 Environment Management:"
	@echo "  env-list        - List all environment files"
	@echo "  env-create      - Create environment files from template"
	@echo "  env-validate    - Validate environment files"
	@echo "  env-set-local   - Set active environment to local"
	@echo "  env-set-uat     - Set active environment to UAT"
	@echo "  env-set-prod    - Set active environment to production"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean          - Clean Python cache files"
	@echo "  clean-all      - Clean everything (Python + Docker)"

# Development commands
install:
	pip install -r requirements.txt

dev:
	python scripts/start_dev.py

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/
	mypy app/

format:
	black app/
	isort app/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/

# Docker commands
docker-build:
	docker build -t connet-ai-bff .

docker-run:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bff

# Enhanced Docker commands for local development
docker-start:
	chmod +x scripts/docker-start.sh && ./scripts/docker-start.sh

docker-start-full:
	chmod +x scripts/docker-start.sh && ./scripts/docker-start.sh --with-tools

docker-stop:
	chmod +x scripts/docker-stop.sh && ./scripts/docker-stop.sh

docker-clean:
	chmod +x scripts/docker-stop.sh && ./scripts/docker-stop.sh --remove-volumes --remove-images

docker-restart:
	make docker-stop && make docker-start

docker-status:
	docker-compose -f docker-compose.local.yml ps

docker-shell:
	docker-compose -f docker-compose.local.yml exec bff bash

docker-test:
	chmod +x scripts/test-docker.sh && ./scripts/test-docker.sh

docker-test-quick:
	chmod +x scripts/test-docker.sh && ./scripts/test-docker.sh --quick

# Database commands
db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-reset:
	alembic downgrade base
	alembic upgrade head

# Utility commands
setup-env:
	python scripts/create_env.py

# Production deployment
deploy-staging:
	@echo "Deploying to staging..."
	# Add staging deployment commands here

deploy-prod:
	@echo "Deploying to production..."
	# Add production deployment commands here

# Debug Environment Commands
debug-start:
	@echo "🔧 Starting debug environment (PostgreSQL + Redis)..."
	@chmod +x scripts/debug-start.sh
	@./scripts/debug-start.sh

debug-stop:
	@echo "🛑 Stopping debug environment..."
	@chmod +x scripts/debug-stop.sh
	@./scripts/debug-stop.sh

debug-logs:
	@echo "📋 Showing debug environment logs..."
	@docker-compose -f docker-compose.debug.yml logs -f

debug-clean:
	@echo "🧹 Cleaning debug environment and data..."
	@docker-compose -f docker-compose.debug.yml down -v
	@docker volume prune -f
	@echo "⚠️  All debug data has been removed!"

# Environment management commands
env-list:
	@echo "🌍 Environment Files Status:"
	@python scripts/manage_env.py list

env-create:
	@echo "🌍 Creating environment files from template..."
	@python scripts/manage_env.py create local
	@python scripts/manage_env.py create uat
	@python scripts/manage_env.py create prod
	@python scripts/manage_env.py create test
	@echo "✅ Environment files created successfully!"

env-validate:
	@echo "🌍 Validating environment files..."
	@python scripts/manage_env.py validate local
	@python scripts/manage_env.py validate uat
	@python scripts/manage_env.py validate prod
	@python scripts/manage_env.py validate test

env-set-local:
	@echo "🌍 Setting active environment to local..."
	@python scripts/manage_env.py set local

env-set-uat:
	@echo "🌍 Setting active environment to UAT..."
	@python scripts/manage_env.py set uat

env-set-prod:
	@echo "🌍 Setting active environment to production..."
	@python scripts/manage_env.py set prod
# Makefile for Connet.AI BFF Service

.PHONY: help install dev test lint format clean docker-build docker-run docker-down

# Default target
help:
	@echo "Connet.AI BFF Service - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Start development server"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code"
	@echo "  clean      - Clean temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-down  - Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  db-upgrade   - Run database migrations"
	@echo "  db-downgrade - Rollback database migrations"
	@echo ""
	@echo "Utilities:"
	@echo "  setup-env    - Create .env file from template"

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
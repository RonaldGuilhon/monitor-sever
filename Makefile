.PHONY: help install test lint format typecheck clean build run

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"

install-gui: ## Install with GUI dependencies
	pip install -e ".[dev,gui]"

test: ## Run tests with coverage
	pytest --cov=monitor_server --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	pytest tests/ -m "not integration"

lint: ## Run linter
	ruff check src/ tests/

format: ## Format code
	ruff format src/ tests/
	black src/ tests/

typecheck: ## Run type checker
	mypy src/ --ignore-missing-imports

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: ## Build the package
	python -m build

run: ## Run the application
	python -m monitor_server

run-gui: ## Run GUI version
	python main.py

docker-build: ## Build Docker image
	docker build -t server-monitor .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

setup-dev: ## Setup development environment
	pip install -e ".[dev]"
	pre-commit install

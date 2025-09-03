# Server Monitor - Makefile
# This Makefile provides convenient commands for development and deployment tasks

.PHONY: help install install-dev setup clean test lint format build run run-console run-gui docker-build docker-run

# Default target
help:
	@echo "Server Monitor - Available Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make setup        - Setup virtual environment and install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting (flake8, mypy)"
	@echo "  make format       - Format code (black)"
	@echo "  make clean        - Clean build artifacts and cache"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Run GUI mode (default)"
	@echo "  make run-gui      - Run GUI mode explicitly"
	@echo "  make run-console  - Run console mode"
	@echo ""
	@echo "Building:"
	@echo "  make build        - Build executable with PyInstaller"
	@echo "  make build-onefile - Build single executable file"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo ""

# Setup virtual environment
setup:
	@echo "Setting up virtual environment..."
	python -m venv venv
	@echo "Activating virtual environment and installing dependencies..."
	@if [ -f "venv/bin/activate" ]; then \
		. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt; \
	else \
		venv\Scripts\activate && pip install --upgrade pip && pip install -r requirements.txt; \
	fi
	@echo "Setup complete!"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy pre-commit pyinstaller

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src/monitor_server --cov-report=html --cov-report=term

# Run linting
lint:
	@echo "Running flake8..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "Running mypy..."
	mypy src/monitor_server --ignore-missing-imports

# Format code
format:
	@echo "Formatting code with black..."
	black src/ tests/ --line-length=88
	@echo "Code formatted!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@if [ -d "build" ]; then rm -rf build; fi
	@if [ -d "dist" ]; then rm -rf dist; fi
	@if [ -d "*.egg-info" ]; then rm -rf *.egg-info; fi
	@if [ -d "__pycache__" ]; then find . -name "__pycache__" -type d -exec rm -rf {} +; fi
	@if [ -d ".pytest_cache" ]; then rm -rf .pytest_cache; fi
	@if [ -d "htmlcov" ]; then rm -rf htmlcov; fi
	@if [ -f ".coverage" ]; then rm -f .coverage; fi
	@echo "Clean complete!"

# Run application in GUI mode
run:
	@echo "Starting Server Monitor (GUI mode)..."
	python run.py --mode gui

run-gui:
	@echo "Starting Server Monitor (GUI mode)..."
	python run.py --mode gui

# Run application in console mode
run-console:
	@echo "Starting Server Monitor (Console mode)..."
	python run.py --mode console

# Build executable with PyInstaller
build:
	@echo "Building executable..."
	pyinstaller --name="ServerMonitor" \
		--windowed \
		--onedir \
		--add-data="src/monitor_server/config:config" \
		--add-data="data:data" \
		--hidden-import="tkinter" \
		--hidden-import="matplotlib" \
		--hidden-import="requests" \
		--hidden-import="ping3" \
		run.py
	@echo "Build complete! Executable is in dist/ServerMonitor/"

# Build single executable file
build-onefile:
	@echo "Building single executable file..."
	pyinstaller --name="ServerMonitor" \
		--windowed \
		--onefile \
		--add-data="src/monitor_server/config:config" \
		--add-data="data:data" \
		--hidden-import="tkinter" \
		--hidden-import="matplotlib" \
		--hidden-import="requests" \
		--hidden-import="ping3" \
		run.py
	@echo "Build complete! Executable is dist/ServerMonitor.exe"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t server-monitor .

docker-run:
	@echo "Running Docker container..."
	docker run -it --rm \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		server-monitor

# Install package in development mode
install-package:
	@echo "Installing package in development mode..."
	pip install -e .

# Create distribution packages
dist:
	@echo "Creating distribution packages..."
	python setup.py sdist bdist_wheel
	@echo "Distribution packages created in dist/"

# Upload to PyPI (requires credentials)
upload:
	@echo "Uploading to PyPI..."
	twine upload dist/*

# Run pre-commit hooks
pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
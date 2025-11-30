.PHONY: help install dev build test lint clean ci

# Default target
help:
	@echo "Available targets:"
	@echo "  install    - Install all dependencies (frontend + backend)"
	@echo "  dev        - Run development servers (frontend + backend)"
	@echo "  build      - Build production bundles"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linters"
	@echo "  clean      - Clean build artifacts"
	@echo "  ci         - Run full CI suite locally"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pnpm install
	cd backend && poetry install

# Run development servers
dev:
	@echo "Starting development servers..."
	@echo "Run 'make dev-frontend' and 'make dev-backend' in separate terminals"

dev-frontend:
	cd frontend && pnpm dev

dev-backend:
	cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Build for production
build:
	@echo "Building production bundles..."
	cd frontend && pnpm build

# Run tests
test:
	@echo "Running tests..."
	cd backend && poetry run pytest
	@echo "Frontend tests not yet configured"

# Run linters
lint:
	@echo "Running linters..."
	cd backend && poetry run ruff check . || true
	cd frontend && pnpm lint || true

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/.next
	rm -rf frontend/node_modules
	rm -rf backend/.pytest_cache
	rm -rf backend/__pycache__

# Run local CI
ci:
	@echo "Running local CI..."
	@echo "This will run linters and tests"
	$(MAKE) lint
	$(MAKE) test

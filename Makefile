# Multi-Agent Tour Guide - Makefile (UV Edition)
# ============================================================================
# UV is a fast Python package installer written in Rust
# Install: curl -LsSf https://astral.sh/uv/install.sh | sh
# Docs: https://docs.astral.sh/uv/
# ============================================================================

.PHONY: help install sync dev test lint format run run-demo run-queue run-streaming run-instant run-sequential run-verbose clean

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║   🗺️  Multi-Agent Tour Guide - UV Commands                   ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  📦 Package Management (UV)"
	@echo "  ─────────────────────────────────────────────────────────────"
	@echo "  install      Install UV (if not installed)"
	@echo "  sync         Sync dependencies (production)"
	@echo "  dev          Sync with dev dependencies"
	@echo "  all          Sync all dependencies (dev + api + apis)"
	@echo "  lock         Update uv.lock file"
	@echo "  add PKG=x    Add a package (e.g., make add PKG=requests)"
	@echo ""
	@echo "  🚀 Running"
	@echo "  ─────────────────────────────────────────────────────────────"
	@echo "  run          Run tour guide in demo mode"
	@echo "  run-queue    Run with queue synchronization (shows all hops)"
	@echo "  run-streaming Run streaming simulation"
	@echo "  run-instant  Run with instant parallel processing"
	@echo "  run-verbose  Run with DEBUG logging (see all traffic)"
	@echo "  run-family   Run with family-friendly profile"
	@echo "  run-api      Start REST API server"
	@echo "  shell        Open Python shell with project context"
	@echo ""
	@echo "  🧪 Testing"
	@echo "  ─────────────────────────────────────────────────────────────"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-cov     Run tests with coverage"
	@echo ""
	@echo "  🔍 Code Quality"
	@echo "  ─────────────────────────────────────────────────────────────"
	@echo "  lint         Check code (ruff + mypy)"
	@echo "  format       Format code (ruff)"
	@echo "  check        Run all checks (lint + test)"
	@echo ""
	@echo "  🧹 Cleanup"
	@echo "  ─────────────────────────────────────────────────────────────"
	@echo "  clean        Remove cache files"
	@echo "  clean-all    Remove cache + venv"
	@echo ""

# ============================================================================
# UV Installation
# ============================================================================

install:
	@echo "📦 Installing UV..."
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "✅ UV installed!"
	@uv --version

# ============================================================================
# Dependency Management
# ============================================================================

sync:
	@echo "📦 Syncing production dependencies..."
	uv sync
	@echo "✅ Dependencies synced!"

dev:
	@echo "📦 Syncing dev dependencies..."
	uv sync --extra dev
	@echo "✅ Dev dependencies synced!"

all:
	@echo "📦 Syncing all dependencies..."
	uv sync --all-extras
	@echo "✅ All dependencies synced!"

lock:
	@echo "🔒 Updating lock file..."
	uv lock
	@echo "✅ Lock file updated!"

add:
	@echo "➕ Adding package: $(PKG)"
	uv add $(PKG)

add-dev:
	@echo "➕ Adding dev package: $(PKG)"
	uv add --dev $(PKG)

remove:
	@echo "➖ Removing package: $(PKG)"
	uv remove $(PKG)

upgrade:
	@echo "⬆️ Upgrading all packages..."
	uv lock --upgrade
	uv sync

# ============================================================================
# Running
# ============================================================================

run:
	@echo "🚀 Running tour guide (demo mode)..."
	uv run python main.py --demo

run-demo: run

run-queue:
	@echo "🚀 Running with queue mode (recommended - shows all hops)..."
	uv run python main.py --demo --mode queue

run-streaming:
	@echo "🚀 Running with streaming mode..."
	uv run python main.py --demo --mode streaming --interval 5

run-stream: run-streaming

run-instant:
	@echo "🚀 Running with instant mode..."
	uv run python main.py --demo --mode instant

run-sequential:
	@echo "🚀 Running with sequential mode..."
	uv run python main.py --demo --mode sequential

run-interactive:
	@echo "🚀 Running interactive setup..."
	uv run python main.py --interactive

run-family:
	@echo "🚀 Running with family profile..."
	uv run python main.py --demo --mode queue --profile family --min-age 5

run-history:
	@echo "🚀 Running with history buff profile..."
	uv run python main.py --demo --mode queue --profile history

run-verbose:
	@echo "🚀 Running with DEBUG logging..."
	LOG_LEVEL=DEBUG uv run python main.py --demo --mode queue

run-api:
	@echo "🌐 Starting API server..."
	uv run --extra api uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

shell:
	@echo "🐍 Opening Python shell..."
	uv run python

ipython:
	@echo "🐍 Opening IPython shell..."
	uv run ipython

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "🧪 Running unit tests (excludes e2e tests that require API keys)..."
	uv run pytest tests/ --ignore=tests/e2e -v

test-unit:
	@echo "🧪 Running unit tests only..."

test-e2e:
	@echo "🧪 Running e2e tests (requires API keys)..."
	uv run pytest tests/e2e -v

test-all:
	@echo "🧪 Running ALL tests including e2e..."
	uv run pytest tests/ -v

test-unit-only:
	@echo "🧪 Running unit tests..."
	uv run pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	uv run pytest tests/integration/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

# ============================================================================
# Code Quality
# ============================================================================

lint:
	@echo "🔍 Running ruff linter..."
	uv run ruff check src/ tests/
	@echo "🔍 Running mypy type checker..."
	uv run mypy src/

format:
	@echo "✨ Formatting code with ruff..."
	uv run ruff format src/ tests/
	@echo "🔧 Fixing imports with ruff..."
	uv run ruff check --fix src/ tests/

check: lint test
	@echo "✅ All checks passed!"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info .mypy_cache .ruff_cache
	@echo "✅ Cleaned!"

clean-all: clean
	@echo "🧹 Removing virtual environment..."
	rm -rf .venv
	@echo "✅ All cleaned!"

# ============================================================================
# Docker (optional)
# ============================================================================

docker-build:
	docker build -t multi-agent-tour-guide .

docker-run:
	docker run -it --rm multi-agent-tour-guide

# ============================================================================
# Project Setup (first time)
# ============================================================================

setup: install dev
	@echo "🎉 Project setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and add your API keys"
	@echo "  2. Run 'make run' to start the demo"
	@echo ""

# ============================================================================
# Info
# ============================================================================

info:
	@echo "📦 UV Version:"
	@uv --version
	@echo ""
	@echo "🐍 Python Version:"
	@uv run python --version
	@echo ""
	@echo "📋 Installed Packages:"
	@uv pip list

tree:
	@uv pip tree

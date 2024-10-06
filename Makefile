.PHONY: help install lint format typecheck test clean publish

# Variables for test directories
AMALFI_TEST_DIR=amalfi
AMALFI_CORE_TEST_DIR=amalfi_core
EXAMPLES_TEST_DIR=examples

# Default test directories
TEST_DIRS=$(AMALFI_TEST_DIR) $(AMALFI_CORE_TEST_DIR) $(EXAMPLES_TEST_DIR)

# Default target
help:
	@echo "Available commands:"
	@echo "  make install             - Install project dependencies"
	@echo "  make lint                - Run linter (Ruff)"
	@echo "  make format              - Run code formatter (Ruff)"
	@echo "  make typecheck           - Run type checker (Pyright)"
	@echo "  make test [pkg=...]  - Run tests (optionally specify pkg)"
	@echo "                             Packages: amalfi, amalfi_core, examples"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make all                 - Run lint, format, typecheck, and test"
	@echo "  make publish             - Build and publish Amalfi to PyPI"

# Install dependencies
install:
	poetry install

# Run linter
lint:
	poetry run ruff check .

# Run formatter
format:
	poetry run ruff check --fix .

# Run type checker
typecheck:
	poetry run pyright

# Run tests
test:
ifeq ($(pkg),)
	@echo "Running all tests..."
	poetry run pytest $(TEST_DIRS)
else ifeq ($(pkg),amalfi)
	@echo "Running tests for 'amalfi' package..."
	poetry run pytest $(AMALFI_TEST_DIR)
else ifeq ($(pkg),amalfi_core)
	@echo "Running tests for 'amalfi_core' package..."
	poetry run pytest $(AMALFI_CORE_TEST_DIR)
else ifeq ($(pkg),examples)
	@echo "Running tests for 'examples'..."
	poetry run pytest $(EXAMPLES_TEST_DIR)
else
	@echo "Unknown package: '$(pkg)'. Available options are: amalfi, amalfi_core, examples."
	@exit 1
endif

# Clean up build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all checks
all: lint format typecheck test

# Publish to PyPI
publish:
	@echo "Building and publishing Amalfi to PyPI..."
	cd amalfi && poetry build && poetry publish

.PHONY: help install lint format typecheck test clean publish

# Variables for test directories
AMALFI_DIR=amalfi
EXAMPLES_DIR=examples

# Default test directories
TEST_DIRS=$(AMALFI_DIR) $(EXAMPLES_DIR)

# Default target
help:
	@echo "Available commands:"
	@echo "  make install             - Install project dependencies"
	@echo "  make lint                - Run linter (Ruff)"
	@echo "  make format              - Run code formatter (Ruff)"
	@echo "  make typecheck           - Run type checker (Pyright)"
	@echo "  make test [pkg=...]      - Run tests (optionally specify pkg)"
	@echo "                             Packages: amalfi, examples"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make all                 - Run lint, format, typecheck, and test"
	@echo "  make publish             - Build and publish Amalfi to PyPI"
	@echo "  make example [name=...]  - Run examples, specify name"
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
	poetry run pytest $(AMALFI_DIR)
else ifeq ($(pkg),examples)
	@echo "Running tests for 'examples'..."
	poetry run pytest $(EXAMPLES_DIR)
else
	@echo "Unknown package: '$(pkg)'. Available options are: amalfi, examples."
	@exit 1
endif

# Clean up build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run all checks for CI/CD
ci: lint format typecheck test

# Publish to PyPI
publish:
	@echo "Building and publishing Amalfi to PyPI..."
	cd amalfi && poetry build && poetry publish

# Run example
example:
	@echo "\nRunning examples for $(name)..."
ifeq ($(name),)
	@echo "No example name specified."
	@echo "Usage: make example name=<example_name>"
	@echo "Available examples:"
	@echo "  pipelines"
	@echo "  stream"
	@echo "  etl_users_and_activities"

	@exit 1
endif

# Pipelines
ifeq ($(name),pipelines)
	poetry run python $(EXAMPLES_DIR)/pipelines.py
endif

# Streams
ifeq ($(name),stream)
	poetry run python $(EXAMPLES_DIR)/streams/__init__.py
endif

# ETL
ifeq ($(name),etl_users_and_activities)
	poetry run python $(EXAMPLES_DIR)/etl/etl_users_and_activities.py
endif

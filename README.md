# Amalfi: Simple functional programming in modern Python

Amalfi is an open-source library for working with functional programming in modern Python, with a focus on simplicity, type safety, and asynchronous programming. It is designed to make functional programming accessible and easy to use, while leveraging the power of modern Python, including async/await, coroutines, and concurrency, always keeping ergonomy in mind.


## Development and Contribution Guide

This monorepo contains the source code for the Amalfi project, including the `amalfi` and `amalfi_core` packages, as well as example usage.

## Development Environment

This project uses Poetry for dependency management and includes a `Makefile` with common commands.

### Prerequisites

- Python 3.12 or higher
- Poetry

### Setting Up the Environment

1. **Install Dependencies**

   ```bash
   make install
   ```

   This command will install all the required dependencies for the project using Poetry.

2. **Recommended VS Code Extensions**

   - [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
   - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

   The included settings will configure Ruff for linting and formatting, and Pyright (via Pylance) for type checking.

   If you're not using VS Code, configure your editor to use:

   - Ruff for linting and formatting
   - Pyright for type checking

## Available Commands

You can use the `Makefile` to perform common tasks in the project.

### Installation

- **Install Project Dependencies**

  ```bash
  make install
  ```

### Linting and Formatting

- **Run Linter (Ruff)**

  ```bash
  make lint
  ```

- **Run Code Formatter (Ruff)**

  ```bash
  make format
  ```

### Type Checking

- **Run Type Checker (Pyright)**

  ```bash
  make typecheck
  ```

### Testing

- **Run All Tests**

  ```bash
  make test
  ```

  This command runs all tests across the repository.

- **Run Tests for a Specific Package**

  You can specify a package to test by passing the `pkg` variable:

  ```bash
  make test pkg=amalfi
  make test pkg=amalfi_core
  make test pkg=examples
  ```

  Available package options are:

  - `amalfi`
  - `amalfi_core`
  - `examples`

### Cleaning Build Artifacts

- **Clean Build Artifacts**

  ```bash
  make clean
  ```

  This command removes build artifacts like `__pycache__`, `.pytest_cache`, and compiled Python files.

### Run All Checks

- **Run Lint, Format, Type Check, and Tests**

  ```bash
  make all
  ```

### Publishing to PyPI

- **Build and Publish Amalfi to PyPI**

  ```bash
  make publish
  ```

  Steps to publish:

  1. Navigate to the `amalfi` directory: `cd amalfi`
  2. Update the version number in `amalfi/pyproject.toml`
  3. Ensure you have the necessary credentials for PyPI
  4. Run the publish command: `make publish`

## Project Structure

```
amalfi/
├── amalfi/                # 'amalfi' package source code
│   ├── __init__.py
│   └── ...
├── amalfi_core/           # 'amalfi_core' package source code
│   ├── amalfi_core/
│   │   ├── __init__.py
│   │   └── ...
│   └── pyproject.toml     # pyproject.toml for 'amalfi_core'
├── examples/              # Example usage and tests
│   └── ...
├── pyproject.toml         # Root pyproject.toml
├── Makefile               # Makefile with common commands
└── README.md              # This README file
```

## Testing Importantly

If you encounter import errors when running tests, ensure:

- Packages are installed in editable mode (handled by `make install`).
- `__init__.py` files are present in all package directories.
- You're running tests within the Poetry environment.

## Contributing

Contributions are welcome! Please ensure that you:

- Write tests for any new functionality.
- Run `make all` to ensure code quality checks pass.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



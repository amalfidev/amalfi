# Amalfi: Simple functional programming in modern Python

Amalfi is an open-source library for working with functional programming in modern Python, with a focus on simplicity, type safety, and asynchronous programming.

It is designed to make functional programming accessible and easy to use, while leveraging the power of modern Python. It considers type hints and async/await to be first class citizens, always keeping ergonomy in mind.

## Installation

```bash
# using pip
pip install amalfi
# using poetry
poetry install amalfi
```

## Quickstart

```python
from amalfi import Pipeline

def add_one(x: int) -> int:
    return x + 1

def multiply_by_two(x: int) -> int:
    return x * 2

pipeline = Pipeline.pipe(3) | add_one | multiply_by_two
result = pipeline()
print(result) # Output: 8
```

```python
from amalfi import as_async

@as_async
def add_one(x: int) -> int:
    return x + 1

```

## Development and Contribution Guide

This monorepo contains the source code for the Amalfi project, including the `amalfi` and subpackages packages, as well as example usage.

### Development Environment

This project uses Poetry for dependency management and includes a `Makefile` with common commands.

#### Prerequisites

- Python 3.12 or higher
- Poetry

#### Setting Up the Environment

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

### Available Commands

You can use the `Makefile` to perform common tasks in the project.

- **Install Project Dependencies**

  ```bash
  make install
  ```

- **Run Linter (Ruff)**

  ```bash
  make lint
  ```

- **Run Code Formatter (Ruff)**

  ```bash
  make format
  ```

- **Run Type Checker (Pyright)**

  ```bash
  make typecheck
  ```

- **Run All Tests**

  ```bash
  make test
  ```

  This command runs all tests across the repository.

- **Run Tests for a Specific Package**

  You can specify a package to test by passing the `pkg` variable:

  ```bash
  make test pkg=amalfi
  make test pkg=examples
  ```

  Available package options are:

  - `amalfi`
  - `examples`


- **Clean Build Artifacts**

  ```bash
  make clean
  ```

  This command removes build artifacts like `__pycache__`, `.pytest_cache`, and compiled Python files.

- **Run Lint, Format, Type Check, and Tests**

  ```bash
  make ci
  ```

### Publishing to PyPI
In order to publish to PyPI, you need to have the necessary credentials. You can set them up by running `poetry config pypi-token.pypi <your_token>`.

You can get your PyPI token by going to your [PyPI account settings](https://pypi.org/manage/account/).

Once you have your token, you can run the following command to publish the package to PyPI:

```bash
make publish
```

#### Steps to publish:

  1. Navigate to the `amalfi` directory: `cd amalfi`
  2. Update the version number in `amalfi/pyproject.toml`
  3. Ensure you have the necessary credentials for PyPI
  4. Run the publish command: `make publish`

### Project Structure

```
amalfi/
├── amalfi/                # 'amalfi' package source code
│   ├── __init__.py
│   └── ...
├── examples/              # Example usage and tests
│   └── ...
├── pyproject.toml         # Root pyproject.toml
├── Makefile               # Makefile with common commands
└── README.md              # This README file
```

### Testing Considerations

If you encounter import errors when running tests, ensure:

- Packages are installed in editable mode (handled by `make install`).
- `__init__.py` files are present in all package directories.
- You're running tests within the Poetry environment.

## Contributing

Contributions are welcome! Please ensure that you:

- Write tests for any new functionality.
- Run `make ci` to ensure code quality checks pass.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



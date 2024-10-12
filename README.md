# Amalfi: Simple Functional Programming for Modern Python

Amalfi is an open-source library for working with functional programming for modern Python, with a strong focus on type safety,
asynchronous programming and simplicity.

It is designed to make functional programming accessible and easy to use, while leveraging the power of modern Python.
It considers type hints and async/await to be first class citizens, always keeping simplicity and a pythonic feel in mind.

The core concepts of Amalfi are:
- **Pipelining**: Chain functions together to form pipelines, synchronously or asynchronously.
- **Streaming**: Chain generators together to form streams, synchronously or asynchronously.
- **Operators**: Building blocks to create pipelines and streams, chaining them together to form more complex data flows.
- **Monads**: Abstraction to handle computations that may fail or return nothing, providing a safe and expressive way to handle errors and side effects.

The core idea is to create pipelines and streams that are fully type safe, composable, chainable, lazy and that support both sync and async operations.

**IMPORTANT**: The library is still under early development, and the public API is subject to change.


A big shoutout to these libraries that heavily inspired Amalfi: [RxPy](https://github.com/ReactiveX/RxPY), [fp-ts](https://github.com/gcanti/fp-ts), [Elixir's pipelines](https://elixir-lang.org/getting-started/mix-otp/supervisor-and-toplevel.html#the-pipeline-operator), and the [Effect TS Library](https://effect.website).



## Installation

```bash
# using pip
pip install amalfi

# using poetry
poetry install amalfi
```

## Quickstart

```python
import asyncio
from amalfi.pipeline import Pipeline
from dataclasses import dataclass, asdict

@dataclass
class User:
    id: int
    name: str

async def fetch_user(user_id: int) -> User:
    await asyncio.sleep(0.1)
    return User(id=user_id, name="John Doe")

def process_user(user: User) -> User:
    updated_fields = {"name": user.name + " Doe"}
    return User(**(asdict(user) | updated_fields))

async def save_user(user: User) -> User:
    await asyncio.sleep(0.1)
    print(f"Saving user: {user.id}")
    return user

pipeline = await (
    Pipeline.apipe(3)
    | fetch_user
    | process_user
    | save_user
)

user = await pipeline.run()
print(json.dumps(asdict(user)))
# Output after ~0.2s:
# > Saving user: 3
# > {"id":3,"name":"John Doe Doe"}
```

## Documentation and Usage
See the [**amalfi package README**](amalfi/README.md) for more detailed documentation.

See the [**examples**](examples/README.md) directory for comprehensive examples of how to use Amalfi.

## Why another functional programming library for Python?
Amalfi aims to fill the gap between functional programming and modern Python by being type-safe, async-friendly and easy to use,
with a focus on simplicity and a pythonic feel.

While libraries like RxPy and functoolz/itertoolz have been instrumental in bringing functional paradigms to Python,
Amalfi brings several new features and improvements to the table.

### Key Innovations Introduced by Amalfi
1. **Type Safety with Modern Python**
   - **Type Hints as First-Class Citizens:** Amalfi emphasizes type safety by leveraging Python's type hints extensively. This ensures that pipelines and streams are fully type-safe, reducing runtime errors and improving code reliability.
  
   - **Strict mode ready:** Amalfi is designed to work well with type checkers like mypy and pyright in strict mode, ensuring that type hints are respected and errors are raised at runtime if type hints are violated.
   
   - **TypeVar and Generic Types:** Amalfi uses `TypeVar` and `Generic` types to create generic operators that can be reused with different types, while ensuring type safety.
  
   - **Support for TypeGuard Predicates:** Functions like `filter_` and `afilter` support type narrowing using TypeGuard predicates, enhancing static type checking and code clarity.

2. **Unified Pipelining/Streaming for Sync/Async Operations**
   - **Seamless Integration of Synchronous and Asynchronous Functions:** Amalfi treats both synchronous and asynchronous functions as first-class citizens, allowing developers to chain them together effortlessly within the same pipeline.
  
   - **Consistent API with `Pipeline`/`AsyncPipeline` and `Stream`/`AsyncStream`:** These classes provide a uniform interface for building pipelines and streams, whether your functions are synchronous or asynchronous. This contrasts with libraries like RxPy, which primarily focus on asynchronous observable streams, and functoolz/itertoolz, which are synchronous.
  
3. **Ergonomic Operators and Fluent Interface**
   - **Overloaded Operators for Chaining:** Amalfi uses the `|` operator to chain functions in a pipeline, making the code intuitive and resembling Unix pipelines or functional languages like F# and Elixir.
  
   - **Easy-to-Use Functional Operators:** With operators like `map_`, `amap`, `filter_`, and `afilter`, Amalfi provides a rich set of tools that are both ergonomic and type-safe.

4. **Lazy Evaluation with Type Safety**
   - **Composability and Laziness:** Amalfi's pipelines and streams are designed to be lazy, executing only when needed. This allows for performance optimizations and efficient handling of large data sets.
  
   - **Support for Generators and Async Generators:** Amalfi can handle both generators (Iterable) and async generators (AsyncIterable) within its streaming capabilities, providing flexibility in how data is processed.

5. **Emphasis on Modern Python Features**
   - **Async/Await Integration:** By embracing async and await, Amalfi allows developers to build asynchronous pipelines that are clear and concise.
  
   - **Advanced Typing Support:** Utilizes modern Python typing features such as `TypeVar`, `Generic`, and `TypeGuard` to enhance the developer experience.

6. **Monadic Constructs for Error Handling**
   - **Maybe and Either Monads:** Amalfi introduces monadic abstractions like `Maybe` and `Result` for handling computations that may fail or return nothing, providing a functional approach to error handling without exceptions.
  
   - **Functional Utilities for Monads:** Functions like `map_maybe`, `bind_maybe`, `map_result`, and `bind_result` help in chaining computations with built-in error propagation.

7. **Enhanced Ergonomics and Readability**
   - **Fluent API Design:** The chainable methods and operator overloading allow for building complex pipelines in a readable and maintainable way.
  
   - **Reduced Boilerplate:** By focusing on ergonomics, Amalfi reduces the amount of code needed to perform common functional programming tasks.

8. **Developer-Friendly Features**
   - **Utilities for Common Patterns:** Functions like `as_async` make it easy to convert synchronous functions to asynchronous ones, aiding in code reuse.
  
   - **Support for Caching and Memoization:** Amalfi includes utilities like `memoize` and `lazy` to optimize computations.

---

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



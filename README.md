# Amalfi: Simple Functional Programming for Modern Python

Amalfi is an open-source library for working with functional programming for modern Python, with a strong focus on type safety, asynchronous programming and ergonomy.

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
from amalfi.pipeline import Fn, AsyncPipeline, Pipeline

def add_one(x: int) -> int:
    return x + 1

async def wait_and_multiply_by_two(x: int) -> int:
    await asyncio.sleep(0.1)
    return x * 2

divide_by_two: Fn[int, float] = lambda x: x / 2.0

pipeline = (
  AsyncPipeline.pipe(3) # asynchronous pipeline that needs to be awaited
  | add_one 
  | wait_and_multiply_by_two 
  | divide_by_two
)

result = await pipeline.run() # Output: 4 (after 0.2s)
# or just call it directly
result = await pipeline()

# change the input
pipeline = pipeline.with_input(10)
result = await pipeline() # Output: 11 (after 0.2s)

# or use the step method to use lambdas directly in a type-safe manner
pipeline = (
  Pipeline.pipe(3) # synchronous pipeline
  .step(lambda x: x + 1)
  .step(lambda x: x * 2)
  .step(lambda x: x / 2.0)
)

result = pipeline() # Output: 5.5
result = pipeline.with_input(10).run() # Output: 11
```

## Usage

### Core Function types
The following types are useful to annotate functions and methods and are used throughout the library. They aim to be as simple and intuitive as possible, and provide ergonomy when working with type annotated functions.

#### `Fn`: The Function Type
A type alias for a synchronous function that takes an input of type `I` and returns an output of type `O`. This represents a callable (function or method) that can be invoked with a single argument of type `I` and returns a value of type `O`. 

  **Usage examples**:
  ```python
  add_one: Fn[int, int] = lambda x: x + 1
  # Equivalent to:
  add_one: Callable[[int], int] = lambda x: x + 1
  ```

#### `AsyncFn`: The Asynchronous Function Type
A type alias for an asynchronous function that takes an input of type `I` and returns an output of type `O`. This represents a callable (function or method) that can be invoked with a single argument of type `I` and returns a coroutine that eventually produces a value of type `O`.

  **Usage examples:**
  ```python
  async def wait_and_add_one(x: int) -> int:
      await asyncio.sleep(1)
      return x + 1

  add_one_async: AsyncFn[int, int] = wait_and_add_one
  # Equivalent to:
  add_one_async: Callable[[int], Coroutine[Any, Any, int]] = wait_and_add_one

  # Usage
  result = await add_one_async(5)  # Output: 6 (after 1 second delay)
  ```

#### `IterFn`: The Iterable Function Type
A type alias for a synchronous function that takes an iterable of type `Iterable[I]` and returns an iterable of type `Iterable[O]`. This represents a callable (function or method) that can be invoked with an iterable of type `Iterable[I]` and returns an iterable of type `Iterable[O]`.

  **Usage examples:**
  ```python
  add_one_to_each: IterFn[int, int] = lambda xs: (x + 1 for x in xs)
  # Equivalent to:
  add_one_to_each: Callable[[Iterable[int]], Iterable[int]] = lambda xs: (x + 1 for x in xs)

  numbers = [1, 2, 3]
  result = add_one_to_each(numbers)
  print(list(result))  # Output: [2, 3, 4]
  ```

#### `AsyncIterFn`: The Asynchronous Iterable Function Type
A type alias for an asynchronous function that takes an iterable of type `Iterable[I]` and returns an iterable of type `Iterable[O]`. This represents a callable (function or method) that can be invoked with an iterable of type `Iterable[I]` and returns a coroutine that eventually produces an iterable of type `Iterable[O]`.

  **Usage examples:**
  ```python
  async def add_one_to_each_async(xs: Iterable[int]) -> Iterable[int]:
      await asyncio.sleep(1)
      return (x + 1 for x in xs)

  add_one_to_each_async_fn: AsyncIterFn[int, int] = add_one_to_each_async
  # Equivalent to:
  add_one_to_each_async_fn: Callable[[Iterable[int]], Coroutine[Any, Any, Iterable[int]]]

  numbers = [1, 2, 3]
  result = await add_one_to_each_async_fn(numbers)
  print(list(result))  # Output: [2, 3, 4] (after 1 second delay)
  ```

### Utilities
The following utilities are useful to work with functions and are used throughout the library as well. They can become handy when working with the library in a type-safe manner.

#### `as_async`: Convert a function from sync to async
Converts a synchronous function to an asynchronous function. If the input function is already asynchronous, it will be returned as is. This can be used as a decorator.
Useful for working with sync functions in an async context, or for converting sync methods to async.

**Usage examples:**
  ```python
  from amalfi import as_async, AsyncFn, Fn

  # Converting a synchronous function to asynchronous
  def add_one(x: int) -> int:
      return x + 1

  add_one_async = as_async(add_one)

  result = await add_one_async(1)
  print(result)  # Output: 2


  # Using `as_async` as a decorator
  @as_async
  def add_one(x: int) -> int:
      return x + 1

  result = await add_one(1)
  print(result)  # Output: 2


  # Converting a lambda function to asynchronous
  add_one_async: AsyncFn[int, int] = as_async(lambda x: x + 1)

  result = await add_one_async(1)
  print(result)  # Output: 2


  # Converting a synchronous lambda function stored in a variable
  add_one: Fn[int, int] = lambda x: x + 1
  add_one_async = as_async(add_one)

  result = await add_one_async(1)
  print(result)  # Output: 2
  ```

## Pipelining

### Pipelines
- **Pipeline**: Chain synchronous functions using the `|` operator.
- **AsyncPipeline**: Chain asynchronous (and synchronous) functions using the `|` operator.
- **pipe / pipe_async**: Initialize pipelines with an input value.
- **`|` Operator**: Use the bitwise OR operator to chain functions in a pipeline.
- **step**: Add a function to the pipeline.

### Operators
#### Mapping
- `map_`: Apply a function over an iterable, possibly asynchronously.
- `amap`: Async version of `map_`. Analogous to `asyncio.gather` but for pipelines.
```python
from amalfi.ops import amap, map_

def add_one(x: int) -> int:
    return x + 1

result = Pipeline.pipe([1, 2, 3]) | map_(add_one) | sum
print(result) # 9

async def wait_and_multiply_by_two(x: int) -> int:
    await asyncio.sleep(0.1) # Simulate some async work
    return x * 2

result = AsyncPipeline.pipe([1, 2, 3]) | amap(wait_and_multiply_by_two) | sum
print(result) # Output: 12 (after 0.1s)
```

#### Filtering
- `afilter`: Async version of `filter_`.
- `filter_`: Filter items in an iterable based on a predicate.

```python
from amalfi.ops import afilter, filter_

def is_even(x: int) -> bool:
    return x % 2 == 0

pipeline = Pipeline.pipe([1, 2, 3, 4]) | filter_(is_even) | sum
result = pipeline.run() # Output: 6

async def async_is_even(x: int) -> bool:
    await asyncio.sleep(0.1) # Simulate some async work
    return x % 2 == 0

result = await (
  AsyncPipeline.pipe([1, 2, 3, 4])
  | afilter(async_is_even)  # [2, 4]
  | sum
).run() # Output: 6 (after 0.1s)
```

##### TODO:
- **reduce_ / areduce**: Reduce an iterable to a single value using a binary function.
- **fork**: Split the data flow to multiple functions.
- **apply**: Apply a function to an argument list.
- **chain**: Compose multiple functions together.
- **compose**: Create a new function by composing multiple functions from right to left.
- **partial**: Partially apply a function by fixing some arguments.
- **curry**: Transform a function into a sequence of functions each taking a single argument.
- **then**: Continue a computation after a promise or future resolves.
- **tap**: Perform a side effect within a pipeline without altering the data flow.
- **to_async**: Convert a synchronous function to an asynchronous one.
- **to_thread**: Run a function in a separate thread.
- **to_process**: Run a function in a separate process.

## Monads

### Maybe / Option Monad

- **Maybe Monad**: Represent computations that may return a value or nothing.
  - **Just(value)**: Represents a computation that successfully returned a value.
  - **Nothing**: Represents a computation that did not return a value.
- **Functions**:
  - **map_maybe**: Apply a function to the value inside a `Maybe`, if it exists.
  - **bind_maybe**: Chain computations that return a `Maybe`, propagating `Nothing` if encountered.

### Either Monad / Result Type

- **Either Monad**: Encapsulate a value or an error for error handling without exceptions.
  - **Success(value)**: Represents a successful computation.
  - **Failure(error)**: Represents a computation that resulted in an error.
- **Functions**:
  - **map_either**: Apply a function to the value inside a `Success`, or propagate the `Failure`.
  - **bind_either**: Chain computations that return an `Either`, propagating `Failure` if encountered.

### Utilities for Monads

- **from_optional**: Convert an optional value to a `Maybe` monad.
- **from_exception**: Convert a function that may throw an exception into one that returns an `Either`.

## Error Handling

- **try_catch**: Catch exceptions in pipeline steps and handle them.
- **retry**: Retry a function upon failure with customizable retry logic.

### Utilities
- **memoize**: Cache function results to optimize repeated computations.
- **lazy**: Delay evaluation of a function until its result is needed.
- **thunk**: Represent a deferred computation.
- **pattern_match**: Simplify complex conditional logic with pattern matching.

### Parallel and Concurrent Execution
- **parallel_map**: Apply a function to items of an iterable in parallel.
- **concurrent_pipeline**: Execute pipeline steps concurrently when possible.

## Asynchronous Programming
- **as_async**: Convert synchronous functions to asynchronous ones.
- **async_helpers**: Utilities for working with async iterables and functions.
  - **async_take**, **async_drop**, **async_chunk**: Manipulate async iterables.
- **debounce_async**: Prevent a function from being called too frequently.
- **throttle_async**: Ensure a function is called at most once in a specified time frame.
- **as_concurrent_futures**: Convert async functions to work with concurrent futures.
- **as_threadpool**: Run functions in a thread pool executor.
- **as_processpool**: Run functions in a process pool executor.

## Functional Data Structures
- **Immutable Collections**: Provide immutable lists, dictionaries, and sets.
- **Sequence**: Functional sequence operations with immutability guarantees.

## Additional Functional Utilities
- **Function Composition**: Tools for composing simple functions into more complex ones.
- **Type Classes and Protocols**: Extend functionality through structural typing.


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



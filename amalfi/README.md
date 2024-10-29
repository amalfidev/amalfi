# Amalfi: Documentation and Usage


### Table of Contents
- [Amalfi: Documentation and Usage](#amalfi-documentation-and-usage)
    - [Table of Contents](#table-of-contents)
    - [Examples](#examples)
  - [Core Function types](#core-function-types)
    - [`Fn`: The Function Type](#fn-the-function-type)
    - [`AsyncFn`: The Asynchronous Function Type](#asyncfn-the-asynchronous-function-type)
    - [`IterFn`: The Iterable Function Type](#iterfn-the-iterable-function-type)
    - [`AsyncIterFn`: The Asynchronous Iterable Function Type](#asynciterfn-the-asynchronous-iterable-function-type)
  - [Pipelining](#pipelining)
    - [Pipelines](#pipelines)
  - [Operators](#operators)
    - [Map](#map)
    - [Filtering](#filtering)
    - [Reducing](#reducing)
    - [Collecting](#collecting)
    - [Tapping](#tapping)
  - [Utilities](#utilities)
    - [`as_async`: Convert a function from sync to async](#as_async-convert-a-function-from-sync-to-async)
    - [TODO:](#todo)
  - [Monads](#monads)
    - [Maybe / Option Monad](#maybe--option-monad)
    - [Either Monad / Result Type](#either-monad--result-type)
    - [Utilities for Monads](#utilities-for-monads)
  - [Error Handling](#error-handling)
    - [Utilities](#utilities-1)
    - [Parallel and Concurrent Execution](#parallel-and-concurrent-execution)
  - [Asynchronous Programming](#asynchronous-programming)
  - [Functional Data Structures](#functional-data-structures)
  - [Additional Functional Utilities](#additional-functional-utilities)

### Examples
See the [examples](../examples/README.md) directory for more advanced usage.

## Core Function types
The following types are useful to annotate functions and methods and are used throughout the library. They aim to be as simple and intuitive as possible, and provide ergonomy when working with type annotated functions.

### `Fn`: The Function Type
A type alias for a synchronous function that takes an input of type `I` and returns an output of type `O`. This represents a callable (function or method) that can be invoked with a single argument of type `I` and returns a value of type `O`. 

  **Usage examples**:
  ```python
  add_one: Fn[int, int] = lambda x: x + 1
  # Equivalent to:
  add_one: Callable[[int], int] = lambda x: x + 1
  ```

### `AsyncFn`: The Asynchronous Function Type
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

### `IterFn`: The Iterable Function Type
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

### `AsyncIterFn`: The Asynchronous Iterable Function Type
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


## Pipelining

### Pipelines
- **Pipeline**: Chain synchronous functions using the `|` operator.
- **AsyncPipeline**: Chain asynchronous (and synchronous) functions using the `|` operator.
- **pipe / pipe_async**: Initialize pipelines with an input value.
- **`|` Operator**: Use the bitwise OR operator to chain functions in a pipeline.
- **step**: Add a function to the pipeline.

## Operators
### Map
The map operators apply a function over an iterable. 
- `map_`: synchronous version.
- `amap`: asynchronous version. Analogous to `asyncio.gather` but for pipelines.

```python
from amalfi import apipe, pipe
from amalfi.ops import amap, map_

def add_one(x: int) -> int:
    return x + 1

result = pipe([1, 2, 3]) | map_(add_one) | sum
print(result) # 9

async def wait_and_multiply_by_two(x: int) -> int:
    await asyncio.sleep(0.001) # Simulate some async work
    return x * 2

result = apipe([1, 2, 3]) | amap(wait_and_multiply_by_two) | sum
print(result) # Output: 12 (after 0.1s)
```

### Filtering
The filtering operators filter items in an iterable based on a predicate.

- `filter_`: synchronous version.
- `afilter`: asynchronous version.

Both `filter_` and `afilter` support type narrowing using `TypeGuard` predicates for improved type safety.

```python
from amalfi import apipe, pipe
from amalfi.ops import afilter, filter_

def is_even(x: int) -> bool:
    return x % 2 == 0

pipeline = pipe([1, 2, 3, 4]) | filter_(is_even) | sum
result = pipeline.run() # Output: 6

async def async_is_even(x: int) -> bool:
    await asyncio.sleep(0.001) # Simulate some async work
    return x % 2 == 0

result = await (
  apipe([1, 2, 3, 4])
  | afilter(async_is_even)  # [2, 4]
  | sum
).run() # Output: 6 (after 0.1s)
```

### Reducing
The reducing operators reduce or fold an iterable to a single value using a binary function.
- `reduce_`: synchronous version.
- `areduce`: asynchronous version. It is concurrent and will evaluate the binary function concurrently for each pair of elements in the iterable in a sequential (not parallel) manner.

```python
from amalfi import apipe, pipe
from amalfi.ops import areduce, reduce_

result = Pipeline.pipe([1, 2, 3, 4]) | reduce_(lambda x, y: x + y)
print(result) # Output: 10


async def async_add(x: int, y: int) -> int:
    await asyncio.sleep(0.001)
    return x + y

result = await apipe([1, 2, 3, 4]).step(areduce(async_add)).run()
print(result) # Output: 10 (after 0.4s = 0.1s per pair of elements)
```

### Collecting
The collecting operators collect or gather the items from an iterator into a list, using a generator function to yield processed items.
- `collect`: synchronous version.
- `acollect`: asynchronous version.

```python
from amalfi import apipe, pipe
from amalfi.ops import collect, acollect

def yield_items(xs: Iterable[int]) -> Generator[int, None, None]: # dummy generator
    for x in xs:
        yield x

pipeline = pipe([1, 2, 3]) | collect(yield_items) | sum
print(pipeline.run()) # Output: 6

async def async_yield_items(xs: Iterable[int]) -> AsyncIterator[int]:
    for x in xs:
        await asyncio.sleep(0.001)
        yield x

pipeline = apipe([1, 2, 3]) | acollect(async_yield_items) | sum
print(await pipeline.run()) # Output: 6 (after 0.3s)
```

### Tapping
The tapping operators perform a synchronous or asynchronous side effect within a pipeline without interrupting the data flow. They are useful for debugging, logging, etc.

It is important to note that in order to ensure the data is not altered, the tapping function should not alter the input value, otherwise the pipeline will not be pure and the data will be altered.

- `tap`: synchronous version.
- `atap`: asynchronous version.

```python
from amalfi import apipe, pipe
from amalfi.ops import atap, tap

pipeline = pipe([1, 2, 3]) | tap(print) | sum
print(pipeline.run()) # Output: 6
# prints: [1, 2, 3]

async def async_print(x: int):
    await asyncio.sleep(0.001)
    print(x)

pipeline = apipe([1, 2, 3]) | atap(async_print) | sum
print(await pipeline.run()) # Output: 6 (after 0.3s)
# prints: [1, 2, 3] (after 0.3s)
```

## Utilities
The following utilities are useful to work with functions and are used throughout the library as well. They can become handy when working with the library in a type-safe manner.

### `as_async`: Convert a function from sync to async
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


### TODO:
- Operators: see https://rxjs.dev/guide/operators#transformation-operators
  - reduce / areduce
  - catch_error
  - retry / retry_when
  - reverse
  - sort
  - count
  - max / min
  - fork / afork
  - starmap
  - group_by
  - partition
  - scan
  - zip
  - next / last
  - chain
  - flat_map
  - enumerate
  - zip_longest
  - zip_with_next
  - sorted
  - reversed
  - unique
  - intersperse
- **chain**: Compose multiple functions together.
- **partial**: Partially apply a function by fixing some arguments.
- **curry**: Transform a function into a sequence of functions each taking a single argument.
- **then**: Continue a computation after a promise or future resolves.
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
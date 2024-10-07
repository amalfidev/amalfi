from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, cast


def identity[T](value: T) -> T:
    return value


def as_async[I, O](
    fn: Callable[[I], O | Coroutine[Any, Any, O]],
) -> Callable[[I], Coroutine[Any, Any, O]]:
    """
    Convert a sync function to an async function.
    """

    async def async_fn(x: I) -> O:
        result = (await fn(x)) if inspect.iscoroutinefunction(fn) else fn(x)
        return cast(O, result)

    return async_fn


class Pipeline[I, O]:
    """
    A generic pipeline class for chaining callables using the `|` operator.

    This class allows the creation of pipelines where each step is a callable
    function. The steps are composed together, enabling a fluent interface
    for processing data through a series of transformations.

    **Type Parameters:**
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    **Attributes:**
    - `input`: The initial input value for the pipeline.
    - `fn`: A callable representing the chained functions of the pipeline.

    **Examples:**

    Basic usage with integer transformations:

    ```python
    from amalfi import pipeline

    def add_one(x: int) -> int:
        return x + 1

    def multiply_by_two(x: int) -> int:
        return x * 2

    # Create a pipeline that adds one and then multiplies by two
    my_pipeline = Pipeline.pipe(3) | add_one | multiply_by_two

    result = my_pipeline()  # (3 + 1) * 2 = 8
    print(result)  # Output: 8
    ```

    Chaining multiple functions with different return types:

    ```python
    from amalfi import pipeline

    def square(x: int) -> int:
        return x * x

    def to_string(x: int) -> str:
        return f"Result is {x}"

    def shout(s: str) -> str:
        return s.upper() + "!"

    # Create a pipeline that squares a number, converts to string, and shouts it
    my_pipeline = Pipeline.pipe(5) | square | to_string | shout

    result = my_pipeline()  # Square 5, convert, and shout
    print(result)  # Output: "RESULT IS 25!"
    ```

    Using built-in functions within the pipeline:

    ```python
    from amalfi import pipeline

    # Create a pipeline that converts to string and gets the length
    my_pipeline = Pipeline.pipe(12345) | str | len

    result = my_pipeline()
    print(result)  # Output: 5
    ```
    """

    input: I
    fn: Callable[[I], O]

    def __init__(self, input: I, fn: Callable[[I], O]):
        """
        Initialize the `Pipeline` with an input value and a function.

        **Args:**
        - `input`: The initial input value for the pipeline.
        - `fn`: A callable that takes an input of type `I` and returns
        an output of type `O`.
        """
        self.input = input
        self.fn = fn

    def __call__(self) -> O:
        """
        Execute the pipeline on the stored input.

        **Returns:**
        - The result of processing the input through the pipeline functions.
        """
        return self.fn(self.input)

    def chain[U](self, fn: Callable[[O], U]) -> Pipeline[I, U]:
        """
        Chain another function to the pipeline.

        This method creates a new `Pipeline` instance that composes the current pipeline
        function with the provided function `fn`.

        **Args:**
        - `fn`: A callable that takes an input of type `O` and returns
        an output of type `U`. Defaults to the identity function.

        **Returns:**
        - A new `Pipeline` instance that represents the composition of the
        current pipeline and the provided function.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Pipeline(self.input, composed_fn)

    def __or__[U](self, fn: Callable[[O], U]) -> Pipeline[I, U]:
        """
        Chain another function to the pipeline using the `|` operator.
        Alias for `#chain` method.
        """

        return self.chain(fn)

    def with_input(self, value: I) -> Pipeline[I, O]:
        self.input = value
        return self

    @classmethod
    def pipe[T](cls, input: T) -> Pipeline[T, T]:
        """
        Create a new AsyncPipeline instance with the given input.

        **Args:**
        - `input`: The initial input value for the pipeline.

        **Returns:**
        - A new `AsyncPipeline` instance initialized with the given input.
        """

        return Pipeline[T, T](input, identity)

    @classmethod
    def pipe_async[T](cls, input: T) -> AsyncPipeline[T, T]:
        """
        Create a new AsyncPipeline instance with the given input.

        **Args:**
        - `input`: The initial input value for the pipeline.

        **Returns:**
        - A new `AsyncPipeline` instance initialized with the given input.
        """

        return AsyncPipeline.pipe(input)


class AsyncPipeline[I, O]:
    """
    An asynchronous pipeline class for chaining both sync and async callables
    using the `|` operator.

    This class allows the creation of pipelines where each step can be either a
    synchronous or asynchronous callable function. The steps are composed together,
    enabling a fluent interface for processing data through a series of
    transformations.

    **Type Parameters:**
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    **Attributes:**
    - `input`: The initial input value for the pipeline.
    - `fn`: An async callable representing the chained functions of the pipeline.

    **Examples:**

    Basic usage with mixed sync and async functions:

    ```python
    from amalfi import async_pipeline
    import asyncio

    def add_one(x: int) -> int:
        return x + 1

    async def multiply_by_two(x: int) -> int:
        await asyncio.sleep(0.1)  # Simulate async operation
        return x * 2

    # Create an async pipeline that adds one and then multiplies by two
    my_pipeline = AsyncPipeline.pipe(3) | add_one | multiply_by_two

    result = asyncio.run(my_pipeline())  # (3 + 1) * 2 = 8
    print(result)  # Output: 8
    ```
    """

    value: I
    fn: Callable[[I], Coroutine[Any, Any, O]]

    def __init__(self, input: I, fn: Callable[[I], O | Coroutine[Any, Any, O]]):
        """
        Initialize the `AsyncPipeline` with an input value and a function.
        If the function is not async, it will be wrapped in an async wrapper in
        order to be able to chain it with other async functions.

        **Args:**
        - `input`: The initial input value for the pipeline.
        - `fn`: A callable that takes an input of type `I` and returns
        an output of type `O` or an Coroutine[Any, Any, O].
        """
        self.input = input
        self.fn = as_async(fn)

    async def __call__(self) -> O:
        """
        Execute the pipeline on the stored input.

        **Returns:**
        - The result of processing the input through the pipeline functions.
        """
        return await self.fn(self.input)

    def chain[U](
        self, fn: Callable[[O], U | Coroutine[Any, Any, U]]
    ) -> AsyncPipeline[I, U]:
        """
        Chain another function to the pipeline.

        This method creates a new `AsyncPipeline` instance that composes the
        current pipeline function with the provided function `fn`, that can be
        either sync or async.

        **Args:**
        - `fn`: A callable that takes an input of type `O` and returns
        an output of type `U`. Defaults to the identity function.

        **Returns:**
        - A new `AsyncPipeline` instance that represents the composition of the
        current pipeline and the provided function.
        """

        async def composed_fn(value: I) -> U:
            return await as_async(fn)(await self.fn(value))

        return AsyncPipeline(self.input, composed_fn)

    def __or__[U](
        self, fn: Callable[[O], U | Coroutine[Any, Any, U]]
    ) -> AsyncPipeline[I, U]:
        """
        Chain another sync or async function to the pipeline using the `|` operator.
        Alias for `#chain` method.
        """

        return self.chain(fn)

    def with_input(self, value: I) -> AsyncPipeline[I, O]:
        self.input = value
        return self

    @classmethod
    def pipe[T](cls, input: T) -> AsyncPipeline[T, T]:
        """
        Create a new AsyncPipeline instance with the given input.

        **Args:**
        - `input`: The initial input value for the pipeline.

        **Returns:**
        - A new `AsyncPipeline` instance initialized with the given input.
        """

        return AsyncPipeline[T, T](input, identity)

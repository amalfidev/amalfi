from __future__ import annotations

from .core import AsyncFn, Fn, as_async, identity


class Pipeline[I, O]:
    """
    A generic pipeline class for chaining callables using the `|` operator.

    This class allows the creation of pipelines where each step is a callable
    function. The steps are composed together, enabling a fluent interface
    for processing data through a series of transformations.

    Type Parameters:
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    Attributes:
    - `input`: The initial input value for the pipeline.
    - `fn`: A callable representing the chained functions of the pipeline.

    Examples:

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
    fn: Fn[I, O]

    def __init__(self, input: I, fn: Fn[I, O]):
        """Initialize the `Pipeline` with an input value and a function."""
        self.input = input
        self.fn = fn

    def __call__(self) -> O:
        """Execute the pipeline on the stored input."""
        return self.run()

    def run(self) -> O:
        """Execute the pipeline on the stored input."""
        return self.fn(self.input)

    def step[U](self, fn: Fn[O, U]) -> Pipeline[I, U]:
        """
        Adds a function as a step to the pipeline.

        This method creates a new `Pipeline` instance that composes the current pipeline
        function with the provided function `fn`.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Pipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U]) -> Pipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#step` method.
        """

        return self.step(fn)

    def with_input(self, value: I) -> Pipeline[I, O]:
        """Change the input value of the pipeline."""
        self.input = value
        return self

    def concat[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline.
        """

        def concat_fn(value: I) -> U:
            return other.fn(self.fn(value))

        return Pipeline(self.input, concat_fn)

    def __add__[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines using the `+` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)

    @classmethod
    def pipe[T](cls, input: T) -> Pipeline[T, T]:
        """Create a new AsyncPipeline instance with the given input."""
        return Pipeline[T, T](input, identity)

    @classmethod
    def apipe[T](cls, input: T) -> AsyncPipeline[T, T]:
        """Create a new AsyncPipeline instance with the given input."""
        return AsyncPipeline.pipe(input)


class AsyncPipeline[I, O]:
    """
    An asynchronous pipeline class for chaining both sync and async callables
    using the `|` operator.

    This class allows the creation of pipelines where each step can be either a
    synchronous or asynchronous callable function. The steps are composed together,
    enabling a fluent interface for processing data through a series of
    transformations.

    Type Parameters:
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    Attributes:
    - `input`: The initial input value for the pipeline.
    - `fn`: An async callable representing the chained functions of the pipeline.

    Examples:

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
    fn: AsyncFn[I, O]

    def __init__(self, input: I, fn: Fn[I, O] | AsyncFn[I, O]):
        """
        Initialize the `AsyncPipeline` with an input value and a function.
        If the function is not async, it will be wrapped in an async wrapper in
        order to be able to chain it with other async functions.
        """
        self.input = input
        self.fn = as_async(fn)

    async def __call__(self) -> O:
        """Execute the pipeline on the stored input."""
        return await self.run()

    async def run(self):
        """Execute the pipeline on the stored input."""
        return await self.fn(self.input)

    def step[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline.

        This method creates a new `AsyncPipeline` instance that composes the
        current pipeline function with the provided function `fn`, that can be
        either sync or async.
        """

        async def composed_fn(value: I) -> U:
            return await as_async(fn)(await self.fn(value))

        return AsyncPipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#step` method.
        """
        return self.step(fn)

    def with_input(self, value: I) -> AsyncPipeline[I, O]:
        """Change the input value of the pipeline."""
        self.input = value
        return self

    def concat[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline.
        """

        async def concat_fn(value: I) -> U:
            return await other.fn(await self.fn(value))

        return AsyncPipeline(self.input, concat_fn)

    def __add__[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines using the `+` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)

    @classmethod
    def pipe[T](cls, input: T) -> AsyncPipeline[T, T]:
        """Create a new AsyncPipeline instance with the given input."""
        return AsyncPipeline[T, T](input, as_async(identity))

    @classmethod
    def from_sync[T, U](cls, pipeline: Pipeline[T, U]) -> AsyncPipeline[T, U]:
        """
        Convert a synchronous pipeline to an asynchronous one,
        using the original input value.
        """

        return AsyncPipeline(pipeline.input, as_async(pipeline.fn))

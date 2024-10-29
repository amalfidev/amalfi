from __future__ import annotations

from .core import AsyncFn, Fn, as_async, identity


class Pipeline[I, O]:
    """
    A generic pipeline class for chaining callables.

    This class allows the creation of pipelines where each step is a callable
    function. The steps are composed together, enabling a fluent interface
    for processing data through a series of transformations.

    Type Parameters:
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    Attributes:
    - `input`: The initial input value for the pipeline.
    - `fn`: A callable representing the chained functions of the pipeline.

    Examples
    --------

    Basic usage with integer transformations:

    ```python
    from amalfi.pipeline import pipe, Pipeline

    def add_one(x: int) -> int:
        return x + 1

    def multiply_by_two(x: int) -> int:
        return x * 2

    # Create a pipeline that adds one and then multiplies by two
    my_pipeline = Pipeline.pipe(3) | add_one | multiply_by_two
    # or
    my_pipeline = pipe(3) | add_one | multiply_by_two
    # or
    my_pipeline = pipe(3).then(add_one).then(multiply_by_two)

    result = my_pipeline()  # (3 + 1) * 2 = 8
    print(result)  # Output: 8
    ```

    Chaining multiple functions with different return types:

    ```python
    from amalfi.pipeline import pipe

    def square(x: int) -> int:
        return x * x

    def to_string(x: int) -> str:
        return f"Result is {x}"

    def shout(s: str) -> str:
        return s.upper() + "!"

    # Create a pipeline that squares a number, converts to string, and shouts it
    my_pipeline = pipe(5) | square | to_string | shout
    # or
    my_pipeline = Pipeline(5) | square | to_string | shout
    # or
    my_pipeline = pipe(5).then(square).then(to_string).then(shout)

    result = my_pipeline()  # Square 5, convert, and shout
    print(result)  # Output: "RESULT IS 25!"
    ```

    Using built-in functions within the pipeline:

    ```python
    from amalfi.pipeline import pipe

    # Create a pipeline that converts to string and gets the length
    my_pipeline = pipe(12345) | str | len

    result = my_pipeline()
    print(result)  # Output: 5
    ```
    """

    input: I
    fn: Fn[I, O]

    def __init__(self, input: I, fn: Fn[I, O] = identity):
        """
        Initialize the `Pipeline` with an input value and a function,
        defaulting to the identity function if none is provided.
        """
        self.input = input
        self.fn = fn

    def __call__(self) -> O:
        """
        Execute the pipeline on the stored input using the stored function.
        Alias for `#run` method.
        """
        return self.run()

    def run(self) -> O:
        """Execute the pipeline on the stored input using the stored function."""
        return self.fn(self.input)

    def then[U](self, fn: Fn[O, U]) -> Pipeline[I, U]:
        """
        Adds a function as a step to the pipeline.

        This method creates a new `Pipeline` instance that composes the current pipeline
        function with the provided function `fn`.

        Examples
        --------
        >>> def add_one(x: int) -> int:
                return x + 1
        >>> my_pipeline = pipe(3).then(add_one).then(lambda x: x * 2)
        >>> my_pipeline()  # (3 + 1) * 2 = 8
        8
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Pipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U]) -> Pipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#then` method.

        Examples
        --------
        >>> def add_one(x: int) -> int:
                return x + 1
        >>> double = lambda x: x * 2
        >>> my_pipeline = pipe(3) | add_one | double
        >>> my_pipeline()  # (3 + 1) * 2 = 8
        8
        """

        return self.then(fn)

    def with_input(self, value: I) -> Pipeline[I, O]:
        """
        Change the input value of the pipeline.

        Args:
            value (I): The new input value for the pipeline.

        Returns:
            Pipeline[I, O]: The pipeline with the updated input, as a chained call.
        """
        self.input = value
        return self

    def concat[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline.

        Args:
            other (Pipeline[O, U]): The other pipeline to concatenate with.

        Returns:
            Pipeline[I, U]: The new concatenated pipeline, with the input value of
            the current pipeline as input.

        Examples
        --------
        >>> def add_one(x: int) -> int:
                return x + 1
        >>> pipeline_a = pipe(3) | add_one
        >>> pipeline_b = pipe(4) | lambda x: x * 2
        >>> pipeline_a.concat(pipeline_b).run()  # (3 + 1) * 2 = 8
        8
        """

        def concat_fn(value: I) -> U:
            return other.fn(self.fn(value))

        return Pipeline(self.input, concat_fn)

    def __gt__[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines using the `>` operator.
        Alias for `#concat` method.

        Examples
        --------
        >>> def add_one(x: int) -> int:
                return x + 1
        >>> pipeline_a = pipe(3) | add_one
        >>> pipeline_b = pipe(4) | lambda x: x * 2
        >>> concat_pipeline = pipeline_a > pipeline_b  # (3 + 1) * 2 = 8
        >>> concat_pipeline()
        8
        """
        return self.concat(other)

    def to_async(self) -> AsyncPipeline[I, O]:
        """Convert the pipeline to an asynchronous pipeline.

        Returns:
            AsyncPipeline[I, O]: The asynchronous pipeline.

        Examples
        --------
        >>> def add_one(x: int) -> int:
                return x + 1
        >>> async def wait_and_add_one(x: int) -> int:
                await asyncio.sleep(0.001)
                return x + 1
        >>> pipeline = pipe(3) | lambda x: x + 1
        >>> async_pipeline = pipeline.to_async().step(wait_and_add_one)
        >>> result = await async_pipeline()  # (3 + 1) + 1 = 5
        5
        """
        return AsyncPipeline(self.input, as_async(self.fn))


def pipe[T](input: T, fn: Fn[T, T] | None = None) -> Pipeline[T, T]:
    """Alias for the `Pipeline` constructor."""
    return Pipeline(input, fn or identity)


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

    Examples
    --------
    Basic usage with mixed sync and async functions:

    ```python
    from amalfi.pipeline import apipe, AsyncPipeline
    import asyncio

    def add_one(x: int) -> int:
        return x + 1

    async def multiply_by_two(x: int) -> int:
        await asyncio.sleep(0.001)  # Simulate async operation
        return x * 2

    # Create an async pipeline that adds one and then multiplies by two
    my_pipeline = apipe(3) | add_one | multiply_by_two
    # or
    my_pipeline = apipe(3) | add_one | multiply_by_two
    # or
    my_pipeline = apipe(3).then(add_one).then(multiply_by_two)

    result = asyncio.run(my_pipeline())  # (3 + 1) * 2 = 8
    print(result)  # Output: 8
    ```
    """

    value: I
    fn: AsyncFn[I, O]

    def __init__(self, input: I, fn: Fn[I, O] | AsyncFn[I, O] = identity):
        """
        Initialize the `AsyncPipeline` with an input value and a function,
        defaulting to the identity function if none is provided.

        If the function is not async, it will be converted using an async wrapper
        in order to be able to chain it with other async functions.
        """
        self.input = input
        self.fn = as_async(fn)

    async def __call__(self) -> O:
        """Execute the pipeline on the stored input using the stored function.
        Alias for `#run` method."""
        return await self.run()

    async def run(self) -> O:
        """Execute the pipeline on the stored input using the stored function."""
        return await self.fn(self.input)

    def then[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline.

        This method creates a new `AsyncPipeline` instance that composes the
        current pipeline function with the provided function `fn`, that can be
        either sync or async.

        Examples
        --------
        >>> async def wait_and_add_one(x: int) -> int:
                await asyncio.sleep(0.001)
                return x + 1
        >>> my_pipeline = apipe(3).then(wait_and_add_one).then(lambda x: x * 2)
        >>> result = await my_pipeline()  # (3 + 1) * 2 = 8
        8
        """

        async def composed_fn(value: I) -> U:
            return await as_async(fn)(await self.fn(value))

        return AsyncPipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#then` method.

        Examples
        --------
        >>> async def wait_and_add_one(x: int) -> int:
                await asyncio.sleep(0.001)
                return x + 1
        >>> my_pipeline = apipe(3) | wait_and_add_one | (lambda x: x * 2)
        >>> result = await my_pipeline()  # (3 + 1) * 2 = 8
        8
        """
        return self.then(fn)

    def with_input(self, value: I) -> AsyncPipeline[I, O]:
        """
        Change the input value of the pipeline.

        Args:
            value (I): The new input value for the pipeline.

        Returns:
            AsyncPipeline[I, O]: The pipeline with the updated input, as a chained call.
        """
        self.input = value
        return self

    def concat[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline.

        Args:
            other (AsyncPipeline[O, U]): The other pipeline to concatenate with.

        Returns:
            AsyncPipeline[I, U]: The new concatenated pipeline, with the input value of
            the current pipeline as input.

        Examples
        --------
        >>> async def wait_and_add_one(x: int) -> int:
                await asyncio.sleep(0.001)
                return x + 1
        >>> pipeline_a = apipe(3) | wait_and_add_one
        >>> pipeline_b = apipe(4) | lambda x: x * 2
        >>> pipeline_a.concat(pipeline_b)()  # (3 + 1) * 2 = 8
        8
        """

        async def concat_fn(value: I) -> U:
            return await other.fn(await self.fn(value))

        return AsyncPipeline(self.input, concat_fn)

    def __gt__[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines using the `>` operator.
        Alias for `#concat` method.

        Examples
        --------
        >>> async def wait_and_add_one(x: int) -> int:
                await asyncio.sleep(0.001)
                return x + 1
        >>> pipeline_a = apipe(3) | wait_and_add_one
        >>> pipeline_b = apipe(4) | lambda x: x * 2
        >>> concat_pipeline = pipeline_a > pipeline_b  # (3 + 1) * 2 = 8
        >>> result = await concat_pipeline()
        8
        """
        return self.concat(other)


def apipe[T](
    input: T, fn: Fn[T, T] | AsyncFn[T, T] | None = None
) -> AsyncPipeline[T, T]:
    """Alias for the `AsyncPipeline` constructor."""
    return AsyncPipeline(input, fn or identity)

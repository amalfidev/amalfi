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
    """

    input: I
    fn: Fn[I, O]

    def __init__(self, input: I, fn: Fn[I, O] = identity):
        """
        Initialize the `Pipeline` with an input value and a function,
        defaulting to the identity function if none is provided.

        Args:
            input (I): The initial input value for the pipeline.
            fn (Fn[I, O]): The function to apply to the input value.
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
        Adds a function as a step to the pipeline. Returns a chained call.

        This method creates a new `Pipeline` instance that composes the current pipeline
        function with the provided function `fn`.

        Args:
            fn (Fn[O, U]): The function to add to the pipeline.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Pipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U]) -> Pipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#then` method.
        """

        return self.then(fn)

    def with_input(self, value: I) -> Pipeline[I, O]:
        """
        Change the input value of the pipeline. Returns a chained call.

        Args:
            value (I): The new input value for the pipeline.
        """
        self.input = value
        return self

    def concat[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline. The new concatenated pipeline, with the input value of
        the current pipeline as input.

        Args:
            other (Pipeline[O, U]): The other pipeline to concatenate with.
        """

        def concat_fn(value: I) -> U:
            return other.fn(self.fn(value))

        return Pipeline(self.input, concat_fn)

    def __gt__[U](self, other: Pipeline[O, U]) -> Pipeline[I, U]:
        """
        Concatenate two pipelines using the `>` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)

    def to_async(self) -> AsyncPipeline[I, O]:
        """Convert the pipeline to an asynchronous pipeline. Returns a chained call."""
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
    """

    value: I
    fn: AsyncFn[I, O]

    def __init__(self, input: I, fn: Fn[I, O] | AsyncFn[I, O] = identity):
        """
        Initialize the `AsyncPipeline` with an input value and a function,
        defaulting to the identity function if none is provided.

        If the function is not async, it will be converted using an async wrapper
        in order to be able to chain it with other async functions.

        Args:
            input (I): The initial input value for the pipeline.
            fn (Fn[I, O] | AsyncFn[I, O]): The function to apply to the input value.
        """
        self.input = input
        self.fn = as_async(fn)

    async def run(self) -> O:
        """Execute the pipeline on the stored input using the stored function."""
        return await self.fn(self.input)

    async def __call__(self) -> O:
        """Execute the pipeline on the stored input using the stored function.
        Alias for `#run` method."""
        return await self.run()

    def then[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline. Returns a chained call.

        This method creates a new `AsyncPipeline` instance that composes the
        current pipeline function with the provided function `fn`, that can be
        either sync or async.

        Args:
            fn (Fn[O, U] | AsyncFn[O, U]): The function to add to the pipeline.
        """

        async def composed_fn(value: I) -> U:
            return await as_async(fn)(await self.fn(value))

        return AsyncPipeline(self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncPipeline[I, U]:
        """
        Adds a function as a step to the pipeline using the `|` operator.
        Alias for `#then` method.
        """
        return self.then(fn)

    def with_input(self, value: I) -> AsyncPipeline[I, O]:
        """
        Change the input value of the pipeline. Returns the pipeline with the
        updated input, as a chained call.

        Args:
            value (I): The new input value for the pipeline.
        """
        self.input = value
        return self

    def concat[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines. The output of the current pipeline is passed
        as input to the other pipeline, regardless of the input value of the
        other pipeline.

        The new concatenated pipeline, with the input value of the current pipeline
        as input.

        Args:
            other (AsyncPipeline[O, U]): The other pipeline to concatenate with.

        """

        async def concat_fn(value: I) -> U:
            return await other.fn(await self.fn(value))

        return AsyncPipeline(self.input, concat_fn)

    def __gt__[U](self, other: AsyncPipeline[O, U]) -> AsyncPipeline[I, U]:
        """
        Concatenate two pipelines using the `>` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)


def apipe[T](
    input: T, fn: Fn[T, T] | AsyncFn[T, T] | None = None
) -> AsyncPipeline[T, T]:
    """Alias for the `AsyncPipeline` constructor."""
    return AsyncPipeline(input, fn or identity)

from __future__ import annotations

from typing import AsyncIterable, AsyncIterator, Iterable, Iterator

from .core import AsyncFn, Fn, as_async, identity


class Stream[I, O]:
    input: Iterable[I]
    fn: Fn[I, O]

    def __init__(self, input: Iterable[I], fn: Fn[I, O]):
        """Initialize the `Stream` with an input value and a function."""
        self.input = input
        self.fn = fn

    def __iter__(self) -> Iterator[O]:
        """Execute the stream on the stored input."""
        for item in self.input:
            yield self.fn(item)

    def collect(self) -> list[O]:
        """Execute the stream on the stored input and collect the results."""
        return list(self.__iter__())

    def step[U](self, fn: Fn[O, U]) -> Stream[I, U]:
        """
        Adds a function as a step to the stream.

        This method creates a new `Stream` instance that composes the current stream
        function with the provided function `fn`.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Stream[I, U](self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U]) -> Stream[I, U]:
        """
        Adds a function as a step to the stream using the `|` operator.
        Alias for `#step` method.
        """

        return self.step(fn)

    def with_input(self, value: Iterable[I]) -> Stream[I, O]:
        """Change the input value of the stream."""
        return Stream(value, self.fn)

    def concat[U](self, other: Stream[O, U]) -> Stream[I, U]:
        """
        Concatenate two streams. The output of the current stream is passed
        as input to the other stream, regardless of the input value of the
        other stream.
        """

        def concat_fn(value: I) -> U:
            return other.fn(self.fn(value))

        return Stream[I, U](self.input, concat_fn)

    def __add__[U](self, other: Stream[O, U]) -> Stream[I, U]:
        """
        Concatenate two streams using the `+` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)

    @classmethod
    def ingest[T](cls, input: Iterable[T]) -> Stream[T, T]:
        """Create a new Stream instance with the given input."""

        return Stream(input, identity)

    @classmethod
    def aingest[T](cls, input: AsyncIterable[T]) -> AsyncStream[T, T]:
        """Create a new AsyncStream instance with the given input."""
        return AsyncStream(input, as_async(identity))


class AsyncStream[I, O]:
    input: AsyncIterable[I]
    fn: AsyncFn[I, O]

    def __init__(self, input: AsyncIterable[I], fn: AsyncFn[I, O]):
        self.input = input
        self.fn = fn

    async def __aiter__(self) -> AsyncIterator[O]:
        """Execute the stream on the stored input asynchronously."""
        async for item in self.input:
            yield await self.fn(item)

    async def collect(self) -> list[O]:
        """Execute the stream on the stored input and collect the results."""
        return [item async for item in self.__aiter__()]

    def step[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncStream[I, U]:
        """Adds a function as a step to the stream."""

        async def composed_fn(value: I) -> U:
            return await as_async(fn)(await self.fn(value))

        return AsyncStream[I, U](self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncStream[I, U]:
        """
        Adds a function as a step to the stream using the `|` operator.
        Alias for `#step` method.
        """
        return self.step(fn)

    def with_input(self, value: AsyncIterable[I]) -> AsyncStream[I, O]:
        """Change the input value of the stream."""
        return AsyncStream(value, self.fn)

    def concat[U](self, other: AsyncStream[O, U]) -> AsyncStream[I, U]:
        """
        Concatenate two streams. The output of the current stream is passed
        as input to the other stream, regardless of the input value of the
        other stream.
        """

        async def concat_fn(value: I) -> U:
            return await other.fn(await self.fn(value))

        return AsyncStream[I, U](self.input, concat_fn)

    @classmethod
    def ingest[T](cls, input: AsyncIterable[T]) -> AsyncStream[T, T]:
        """Create a new AsyncStream instance with the given input."""
        return AsyncStream(input, as_async(identity))

    @classmethod
    def from_sync[T](cls, stream: Stream[T, T]) -> AsyncStream[T, T]:
        """
        Convert a synchronous stream to an asynchronous one,
        using the original input value.
        """

        async def async_input() -> AsyncIterator[T]:
            for item in stream.input:
                yield item

        return AsyncStream(async_input(), as_async(stream.fn))

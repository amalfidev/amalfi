from __future__ import annotations

from itertools import islice, takewhile
from typing import Iterable, Iterator, overload

from .core import Fn


class Stream[I]:
    _iter: Iterable[I]

    def __init__(self, input: Iterable[I]):
        """Initialize the `Stream` with an input value and a function."""
        self._iter = input

    @classmethod
    def from_str(cls, value: str) -> Stream[str]:
        return Stream([value])

    @classmethod
    def from_bytes(cls, value: bytes) -> Stream[bytes]:
        return Stream([value])

    def __iter__(self) -> Iterator[I]:
        """Execute the stream on the input."""
        yield from self._iter

    def __repr__(self) -> str:
        return f"Stream({self._iter.__repr__()})"

    @overload
    def collect(self, into: None = None) -> list[I]: ...

    @overload
    def collect[T](self, into: Fn[Iterable[I], T]) -> T: ...

    def collect[T](self, into: Fn[Iterable[I], T] | None = None) -> T | list[I]:
        """
        Execute the stream on the input and collect the results into a custom
        collection type, which defaults to a list.
        """
        if not into:
            return list(self)
        return into(self)

    def map[O](self, fn: Fn[I, O]) -> Stream[O]:
        """
        Adds a mapping step to the stream, returning a new stream of the
        mapped values.
        """

        return Stream(map(fn, self))

    def filter(self, fn: Fn[I, bool]) -> Stream[I]:
        """
        Adds a filtering step to the stream, returning a new stream of the
        filtered values.
        """
        return Stream(filter(fn, self))

    def take(self, n: int) -> Stream[I]:
        """Take the first `n` values from the stream."""
        return Stream(islice(self, n))

    def take_while(self, fn: Fn[I, bool]) -> Stream[I]:
        """Take values from the stream while the predicate is true."""
        return Stream(takewhile(fn, self))

    # def list(self) -> list[I]:
    #     return self.collect(list)

    # def tuple(self) -> tuple[I, ...]:
    #     return self.collect(tuple)

    # def set(self) -> set[I]:
    #     return self.collect(set)

    # def deque(self) -> deque[I]:
    #     return self.collect(deque)

    # @classmethod
    # def aingest[T](cls, input: AsyncIterable[T]) -> AsyncStream[T, T]:
    #     """Create a new AsyncStream instance with the given input."""
    #     return AsyncStream(input, as_async(identity))


# class AsyncStream[I, O]:
#     input: AsyncIterable[I]
#     fn: AsyncFn[I, O]

#     def __init__(self, input: AsyncIterable[I], fn: AsyncFn[I, O]):
#         self.input = input
#         self.fn = fn

#     async def __aiter__(self) -> AsyncIterator[O]:
#         """Execute the stream on the stored input asynchronously."""
#         async for item in self.input:
#             yield await self.fn(item)

#     async def collect(self) -> list[O]:
#         """Execute the stream on the stored input and collect the results."""
#         return [item async for item in self.__aiter__()]

#     def map[U](self, fn: Fn[O, U] | AsyncFn[O, U]) -> AsyncStream[I, U]:
#         """Adds a mapping function to the stream."""

#         async def composed_fn(value: I) -> U:
#             return await as_async(fn)(await self.fn(value))

#         return AsyncStream[I, U](self.input, composed_fn)

#     def with_input(self, value: AsyncIterable[I]) -> AsyncStream[I, O]:
#         """Change the input value of the stream."""
#         return AsyncStream(value, self.fn)

#     def concat[U](self, other: AsyncStream[O, U]) -> AsyncStream[I, U]:
#         """
#         Concatenate two streams. The output of the current stream is passed
#         as input to the other stream, regardless of the input value of the
#         other stream.
#         """

#         async def concat_fn(value: I) -> U:
#             return await other.fn(await self.fn(value))

#         return AsyncStream[I, U](self.input, concat_fn)

#     @classmethod
#     def ingest[T](cls, input: AsyncIterable[T]) -> AsyncStream[T, T]:
#         """Create a new AsyncStream instance with the given input."""
#         return AsyncStream(input, as_async(identity))

#     @classmethod
#     def from_sync[T](cls, stream: Stream[T, T]) -> AsyncStream[T, T]:
#         """
#         Convert a synchronous stream to an asynchronous one,
#         using the original input value.
#         """

#         async def async_input() -> AsyncIterator[T]:
#             for item in stream.input:
#                 yield item

#         return AsyncStream(async_input(), as_async(stream.fn))

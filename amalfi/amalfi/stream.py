from __future__ import annotations

from itertools import islice, takewhile
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator, overload

from .core import Fn, as_aiter


class Stream[I]:
    _iter: Iterable[I]

    def __init__(self, input: Iterable[I]):
        """Initialize the `Stream` with an input value and a function."""
        self._iter = input

    def __iter__(self) -> Iterator[I]:
        """Iterate over the stream"""
        yield from self._iter

    def __repr__(self) -> str:
        return f"Stream({self._iter.__repr__()})"

    @classmethod
    def from_str(cls, value: str) -> Stream[str]:
        return Stream([value])

    @classmethod
    def from_bytes(cls, value: bytes) -> Stream[bytes]:
        return Stream([value])

    def to_async(self) -> AsyncStream[I]:
        """Convert the stream to an async stream."""
        return AsyncStream(as_aiter(self))

    # region: --collect
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

    # endregion --collect

    # region: --ops
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

    # endregion --ops


stream = Stream
"""Alias for the `Stream` constructor."""

# TODO:
# - operators: see https://rxjs.dev/guide/operators#transformation-operators
# -- gather (list, tuple, set, deque, custom fn), seq/parallel
# -- to_pipe
# -- amap / afilter
# -- reduce / areduce
# -- count
# -- fork / afork
# -- group_by
# -- partition
# -- scan
# -- tap
# -- zip
# -- chain
# -- flat_map
# -- enumerate
# -- zip_longest
# -- zip_with_next
# -- sorted
# -- reversed
# -- unique
# -- intersperse
# TODO: to pipe
# TODO: to async


class AsyncStream[I]:
    _aiter: AsyncIterable[I]

    def __init__(self, input: AsyncIterable[I]):
        self._aiter = input

    async def __aiter__(self) -> AsyncIterator[I]:
        async for item in self._aiter:
            yield item

    def __repr__(self) -> str:
        return f"AsyncStream({self._aiter.__repr__()})"

    # region: --collect
    @overload
    async def collect(self, into: None = None) -> list[I]: ...

    @overload
    async def collect[T](self, into: Fn[Iterable[I], T]) -> T: ...

    async def collect[T](self, into: Fn[Iterable[I], T] | None = None) -> T | list[I]:
        """
        Execute the stream on the input and collect the results into a custom
        collection type, which defaults to a list.
        """
        collected = [i async for i in self]
        return collected if not into else into(collected)

    # endregion --collect


astream = AsyncStream
"""Alias for the `AsyncStream` constructor."""

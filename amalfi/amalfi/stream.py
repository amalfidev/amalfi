from __future__ import annotations

from itertools import islice, takewhile
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator, overload

from .core import AsyncFn, Fn, as_aiter, as_async
from .pipeline import AsyncPipeline, Pipeline, apipe, pipe


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

    def to_async(self) -> AsyncStream[I]:
        """Convert the stream to an async stream."""
        return AsyncStream(as_aiter(self))

    def to_pipe(self) -> Pipeline[Iterable[I], Iterable[I]]:
        """Convert the stream to a pipeline."""
        return pipe(iter(self))

    def to_apipe(self) -> AsyncPipeline[Iterable[I], Iterable[I]]:
        """Convert the stream to an async pipeline."""
        return apipe(iter(self))

    # region: --collect
    @overload
    def collect(self, into: None = None) -> list[I]: ...

    @overload
    def collect[T](self, into: Fn[Iterable[I], T]) -> T: ...

    def collect[T](self, into: Fn[Iterable[I], T] | None = None) -> T | list[I]:
        """
        Execute the stream on the input and collect the results into a custom
        collector function, which defaults to a list.
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


def stream[I](input: Iterable[I]) -> Stream[I]:
    """Alias for the `Stream` constructor."""
    return Stream(input)


# TODO:
# - operators: see https://rxjs.dev/guide/operators#transformation-operators
# -- gather (list, tuple, set, deque, custom fn), seq/parallel
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
# - to_thread (asyncio, concurrent.futures, threading)
# - to_process (multiprocessing)
# - to_executor (concurrent.futures)
# - to_queue (multiprocessing)


class AsyncStream[I]:
    _aiter: AsyncIterable[I]

    def __init__(self, input: AsyncIterable[I]):
        self._aiter = input

    async def __aiter__(self) -> AsyncIterator[I]:
        async for item in self._aiter:
            yield item

    def __repr__(self) -> str:
        return f"AsyncStream({self._aiter.__repr__()})"

    async def to_pipe(self) -> Pipeline[Iterable[I], Iterable[I]]:
        """Convert the async stream to a pipeline."""
        return pipe(await self.collect())

    async def to_apipe(self) -> AsyncPipeline[Iterable[I], Iterable[I]]:
        """Convert the stream to an async pipeline."""
        return apipe(await self.collect())

    # region: --collect
    @overload
    async def collect(self, into: None = None) -> list[I]: ...

    @overload
    async def collect[T](self, into: Fn[Iterable[I], T]) -> T: ...

    async def collect[T](self, into: Fn[Iterable[I], T] | None = None) -> T | list[I]:
        """
        Execute the stream on the input and collect the results into a custom
        collector function, which defaults to a list.
        """
        collected = [i async for i in self]
        return collected if not into else into(collected)

    # endregion --collect

    # region: --ops
    def map[O](self, fn: Fn[I, O] | AsyncFn[I, O]) -> AsyncStream[O]:
        """
        Adds a mapping step to the stream, returning a new stream of the
        mapped values. The mapping function can be either synchronous or
        asynchronous.

        Example:
        ```python
        result = await astream([1, 2, 3]).map(lambda x: x + 1).collect()
        assert result == [2, 3, 4]
        ```
        """

        async def amap():
            async for i in self:
                yield await as_async(fn)(i)

        return AsyncStream(amap())

    # endregion --ops


def astream[I](input: AsyncIterable[I]) -> AsyncStream[I]:
    """Alias for the `AsyncStream` constructor."""
    return AsyncStream(input)

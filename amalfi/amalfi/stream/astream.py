from __future__ import annotations

from typing import AsyncIterable, AsyncIterator, Iterable, overload

from ..core import AsyncFn, Fn, as_async
from ..pipeline import AsyncPipeline, Pipeline, apipe, pipe


class AsyncStream[I]:
    """
    An asynchronous iterable stream of values that can be processed in a
    sequential manner by applying a series of synchronous or asynchronous
    transformations to the data.

    This class allows the creation of streams where each step is a function that
    transforms the data in an lazy manner. The steps are composed together,
    enabling a fluent interface for processing data through a series of
    transformations.

    Type Parameters:
    - `I`: The type of the items in the input iterable.

    Attributes:
    - `input`: The input iterable to the stream, to be transformed by the functions.

    Examples
    --------

    Basic usage with integer transformations:

    ```python
    from amalfi.stream import astream

    async def adouble(x: int) -> int:
        await asyncio.sleep(1) # Simulate async work
        return x * 2

    result = await astream([1, 2, 3]).map(adouble).take(2).collect()
    assert result == [2, 4]
    ```
    """

    _aiter: AsyncIterable[I]

    def __init__(self, input: AsyncIterable[I]):
        """Initialize the `AsyncStream` with an input async iterable."""
        self._aiter = input

    async def __aiter__(self) -> AsyncIterator[I]:
        """Iterate over the async stream"""
        async for item in self._aiter:
            yield item

    def __repr__(self) -> str:
        """Return a string representation of the async stream"""
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

            This method will consume the stream and return the collected result.
            If the stream is infinite, this method will never return.

            A custom collector can be passed. It should be a function that takes an
            iterable and returns the desired type `T`. It defaults to a list.

            Args:
                into (Fn[Iterable[I], T] | None): An optional custom collector function,
                which defaults to a list.

            Returns:
                T | list[I]: The collected result of the stream.

        Examples
        --------
        >>> result = await astream([1, 2, 3]).map(lambda x: x + 1).collect()
        >>> assert result == [2, 3, 4]

        >>> result = await (
                        astream([1, 2, 3])
                            .map(lambda x: x + 1)
                            .filter(lambda x: x % 2 == 0)
                            .take(2)
                            .collect(into=tuple)
                    )
        >>> assert result == (2, 4)
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

        Examples
        --------

        >>> result = await astream([1, 2, 3]).map(lambda x: x + 1).collect()
        [2, 3, 4]
        """

        async def amap():
            async for i in self:
                yield await as_async(fn)(i)

        return AsyncStream(amap())

    def filter(self, fn: Fn[I, bool] | AsyncFn[I, bool] | None) -> AsyncStream[I]:
        """
        Adds a filtering step to the stream, returning a new stream of the
        filtered values.

        Args:
            fn (Fn[I, bool] | AsyncFn[I, bool] | None): A synchronous or asynchronous
            filtering function. If `None` is passed, the stream will be filtered to
            exclude `None` values.

        Returns:
            AsyncStream[I]: a new stream of the filtered values

        Examples
        --------
        >>> result = await astream([1, 2, 3]).filter(lambda x: x % 2 == 0).collect()
        [2]
        >>> result = await astream([1, None, 3]).filter(None).collect()
        [1, 3]
        """

        async def afilter():
            async for i in self:
                if fn is None:
                    if i is not None:
                        yield i
                elif await as_async(fn)(i):
                    yield i

        return AsyncStream(afilter())

    def take(self, n: int) -> AsyncStream[I]:
        """
        Adds a take step to the stream, returning a new stream of at most the
        first `n` values.

        Args:
            n (int): The maximum number of items to take from the stream.

        Returns:
            AsyncStream[I]: A new stream containing at most `n` items from the
            original stream.

        Examples
        --------
        >>> result = await astream([1, 2, 3, 4]).take(2).collect()
        [1, 2]
        >>> result = await astream([1]).take(3).collect()
        [1]
        >>> result = await astream([]).take(2).collect()
        []
        """

        async def atake() -> AsyncIterator[I]:
            count = 0
            async for item in self:
                if count >= n:
                    break
                yield item
                count += 1

        return AsyncStream(atake())

    def take_while(self, fn: Fn[I, bool] | AsyncFn[I, bool]) -> AsyncStream[I]:
        """
        Adds a take_while step to the stream, returning a new stream of the
        values taken while the predicate is true.

        Args:
            fn (Fn[I, bool] | AsyncFn[I, bool]): A synchronous or asynchronous
            predicate function.

        Returns:
            AsyncStream[I]: A new stream containing the values taken while the
            predicate is true.

        Examples
        --------
        >>> result = await astream([1, 2, 3, 4]).take_while(lambda x: x < 3).collect()
        [1, 2]
        """

        async def atake_while() -> AsyncIterator[I]:
            async for item in self:
                if not await as_async(fn)(item):
                    break
                yield item

        return AsyncStream(atake_while())

    def default(self, default: I) -> AsyncStream[I]:
        """
        Returns a stream with the default value if the stream is empty.

        Args:
            default (I): The default value to return if the stream is empty

        Returns:
            AsyncStream[I]: a new stream with the default value if the stream is empty

        Examples
        --------
        >>> result = await astream(ayield_range(1, 4)).default(0).collect()
        [1, 2, 3]
        >>> result = await astream(ayield_range(1, 1)).default(0).collect()
        [0]
        """

        async def adefault() -> AsyncIterator[I]:
            is_empty = True
            async for item in self:
                is_empty = False
                yield item
            if is_empty:
                yield default

        return AsyncStream(adefault())

    # endregion --ops


def astream[I](input: AsyncIterable[I]) -> AsyncStream[I]:
    """Alias for the `AsyncStream` constructor."""
    return AsyncStream(input)

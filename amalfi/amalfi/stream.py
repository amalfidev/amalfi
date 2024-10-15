from __future__ import annotations

from itertools import islice, takewhile
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator, overload

from .core import AsyncFn, Fn, as_aiter, as_async
from .pipeline import AsyncPipeline, Pipeline, apipe, pipe


class Stream[I]:
    """
    A synchronous iterable stream of values that can be processed in a sequential
    manner by applying a series of synchronous transformations to the data.

    This class allows the creation of streams where each step is a function that
    transforms the data in an lazy manner. The steps are composed together,
    enabling a fluent interface for processing data through a series of
    transformations.

    Type Parameters:
    - `I`: The type of the items in the input iterable.

    Attributes:
    - `input`: The input iterable to the stream, to be transformed by the functions.

    Examples:

    Basic usage with integer transformations:

    ```python
    from amalfi.stream import stream

    def add_one(x: int) -> int:
        return x + 1

    def multiply_by_two(x: int) -> int:
        return x * 2

    # Create a stream that adds one and then multiplies by two
    result = (
        stream([1, 2, 3, 4, 5])
            .map(add_one)
            .filter(lambda x: x % 2 == 0)
            .take(2)
            .collect()
        )
    assert result == [2, 4]
    ```
    """

    _iter: Iterable[I]

    def __init__(self, input: Iterable[I]):
        """Initialize the `Stream` with an input iterable."""
        self._iter = input

    def __iter__(self) -> Iterator[I]:
        """Iterate over the stream"""
        yield from self._iter

    def __repr__(self) -> str:
        """Return a string representation of the stream"""
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

        This method will consume the stream and return the collected result.
        If the stream is infinite, this method will never return.

        A custom collector can be passed. It should be a function that takes an
        iterable and returns the desired type `T`. It defaults to a list.

        Args:
            into (Fn[Iterable[I], T] | None): An optional custom collector function,
            which defaults to a list.

        Returns:
            T | list[I]: The collected result of the stream.

        Example:
            >>> result = stream([1, 2, 3, 4, 5]).map(lambda x: x + 1).collect()
            >>> assert result == [2, 3, 4, 5, 6]
            >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect(into=tuple)
            >>> assert result == (2, 3, 4)
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

        Args:
            fn (Fn[I, O]): A synchronous mapping function

        Returns:
            Stream[O]: a new stream of the mapped values

        Example:
            >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect()
            >>> assert result == [2, 3, 4]
        """

        return Stream(map(fn, self))

    def filter(self, fn: Fn[I, bool]) -> Stream[I]:
        """
        Adds a filtering step to the stream, returning a new stream of the
        filtered values.

        Args:
            fn (Fn[I, bool]): A synchronous filtering function

        Returns:
            Stream[I]: a new stream of the filtered values

        Example:
            >>> result = stream([1, 2, 3]).filter(lambda x: x % 2 == 0).collect()
            >>> assert result == [2]
        """
        return Stream(filter(fn, self))

    def take(self, n: int) -> Stream[I]:
        """
        Take the first `n` values from the stream.

        Args:
            n (int): The number of values to take from the stream

        Returns:
            Stream[I]: a new stream of the first `n` values
        """
        return Stream(islice(self, n))

    def take_while(self, fn: Fn[I, bool]) -> Stream[I]:
        """
        Take values from the stream while the predicate is true.

        Args:
            fn (Fn[I, bool]): A synchronous predicate function

        Returns:
            Stream[I]: a new stream of the values taken while the predicate is true
        """
        return Stream(takewhile(fn, self))

    # endregion --ops


def stream[I](input: Iterable[I]) -> Stream[I]:
    """Alias for the `Stream` constructor.

    Example:
        >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect()
        >>> assert result == [2, 3, 4]
    """
    return Stream(input)


# TODO:
# - operators: see https://rxjs.dev/guide/operators#transformation-operators
# -- gather (list, tuple, set, deque, custom fn), seq/parallel
# -- afilter
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

    Examples:

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

        Example:
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

from __future__ import annotations

import asyncio
from inspect import isawaitable
from typing import Any, AsyncIterable, AsyncIterator, Iterable, cast, overload

from amalfi.ops.tap import atap

from ..core import AsyncFn, AsyncTFn, AsyncVFn, Fn, TFn, VFn, as_async
from ..pipeline import AsyncPipeline, apipe


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

    # region: --materialization
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
        """
        collected = [i async for i in self]
        return collected if not into else into(collected)

    async def pipe[O](
        self,
        then: Fn[
            AsyncPipeline[Iterable[I], Iterable[I]],
            AsyncPipeline[Iterable[I], O],
        ] = lambda p: p,
    ) -> O:
        """
        Collects the stream and reduces it using an async pipeline. The pipeline
        can be further transformed by the `then` function.

        Args:
            then (Fn[AsyncPipeline[
                Iterable[I], Iterable[I]],
                AsyncPipeline[Iterable[I], O]]
            ): A function that takes an async pipeline and returns a transformed
            async pipeline.
        """
        collected = await self.collect()
        return await then(apipe(collected)).run()

    # endregion --materialization

    # region: --ops
    def map[O](self, fn: Fn[I, O] | AsyncFn[I, O]) -> AsyncStream[O]:
        """
        Adds a mapping step to the stream, returning a new stream of the
        mapped values. The mapping function can be either synchronous or
        asynchronous. Returns a new stream of the mapped values.

        Args:
            fn (Fn[I, O] | AsyncFn[I, O]): A synchronous or asynchronous mapping
            function.
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
        """

        async def atake_while() -> AsyncIterator[I]:
            async for item in self:
                if not await as_async(fn)(item):
                    break
                yield item

        return AsyncStream(atake_while())

    def default(self, default_value: I) -> AsyncStream[I]:
        """
        Returns a stream with the default value if the stream is empty.

        Args:
            default_value (I): The default value to return if the stream is empty
        """

        async def adefault() -> AsyncIterator[I]:
            is_empty = True
            async for item in self:
                is_empty = False
                yield item
            if is_empty:
                yield default_value

        return AsyncStream(adefault())

    def tap(self, fn: Fn[I, Any] | AsyncFn[I, Any]) -> AsyncStream[I]:
        """
        Perform a synchronous or asynchronous side effect within a stream without
        altering the data flow.

        Args:
            fn (Fn[I, Any] | AsyncFn[I, Any]): A synchronous or asynchronous side
            effect function.
        """
        return self.map(atap(as_async(fn)))

    def reduce[O](
        self, fn: VFn[[O, I], O] | AsyncVFn[[O, I], O], initial: O
    ) -> AsyncStream[O]:
        """
        Reduce or fold the stream to a single value using a reducer function.
        Returns a new stream of the reduced value.

        Args:
            fn (VFn[[O, I], O] | AsyncVFn[[O, I], O]): A synchronous or asynchronous
            reducer function.
            initial (O): The initial value for the reduction.
        """

        async def areducer() -> AsyncIterator[O]:
            acc = initial
            if asyncio.iscoroutinefunction(fn):
                async for item in self:
                    acc = await fn(acc, item)
                yield acc
            else:
                sync_fn = cast(VFn[[O, I], O], fn)
                async for item in self:
                    acc = sync_fn(acc, item)
                yield acc

        return AsyncStream(areducer())

    def starmap[*P, O](self, fn: TFn[*P, O] | AsyncTFn[*P, O]) -> AsyncStream[O]:
        """
        Apply a synchronous or asynchronous tuple-unpacking function to each element
        of an iterable, yielding the mapped values. The stream must be an iterable of
        tuples, otherwise a `ValueError` is raised.

        Args:
            fn (TFn[*P, O] | AsyncTFn[*P, O]): A synchronous or asynchronous
            tuple-unpacking function

        Raises:
            ValueError: If the input is not an iterable of tuples
        """

        async def astarmapper() -> AsyncIterator[O]:
            async for item in self:
                if not isinstance(item, tuple):
                    raise ValueError(f"Expected tuple, got {type(item)}")

                if asyncio.iscoroutinefunction(fn):
                    yield await fn(*cast(tuple[*P], item))
                else:
                    sync_fn = cast(TFn[*P, O], fn)
                    yield sync_fn(*cast(tuple[*P], item))

        return AsyncStream(astarmapper())

    def await_(self) -> AsyncStream[I]:
        """
        Await the stream item.

        If the item is awaitable, it is awaited and the result is yielded.
        Otherwise, the item is yielded as is.

        Notes:
        - Useful to await the stream items when they are coroutines or awaitables
        and the `await` keyword is not available.
        """

        async def awaiter():
            async for item in self:
                if isawaitable(item):
                    yield cast(I, await item)
                else:
                    yield cast(I, item)

        return AsyncStream(awaiter())

    def chunk(
        self,
        size: int | None = None,
    ) -> AsyncStream[list[I]]:
        """Gather the stream into a list of chunks. If `size` is `None`, the entire
        stream is collected into a single chunk.

        Args:
            size (int): The size of each chunk.
        """

        async def chunker() -> AsyncIterator[list[I]]:
            if not size:
                chunk: list[I] = [item async for item in self]
                if chunk:
                    yield chunk
            else:
                assert size > 0, ValueError("Chunk size must be positive")
                chunk: list[I] = []
                async for item in self:
                    chunk.append(item)
                    if len(chunk) == size:
                        yield chunk
                        chunk = []
                if chunk:
                    yield chunk

        return AsyncStream(chunker())

    def mapzip[*O](
        self,
        fn: Fn[I, O] | AsyncFn[I, O],
    ) -> AsyncStream[tuple[I, *O]]:
        """Extend a stream with a tuple of functions that transform the stream items.

        The functions are applied in parallel, and the results are zipped together.
        If any function is asynchronous, the processing is awaited and the results
        are zipped together.

        Args:
            fn (Fn[I, O] | AsyncFn[I, O]): A synchronous or asynchronous function
        """

        async def mapzipper() -> AsyncIterator[tuple[I, *O]]:
            async for item in self:
                yield item, (await as_async(fn)(item))

        return AsyncStream(mapzipper())

    def zip_with[O](self, other: AsyncIterable[O]) -> AsyncStream[tuple[I, O]]:
        """Zip two streams together."""

        async def azip_with() -> AsyncIterator[tuple[I, O]]:
            it1, it2 = self.__aiter__(), other.__aiter__()
            while True:
                try:
                    i = await it1.__anext__()
                    o = await it2.__anext__()
                    yield i, o
                except StopAsyncIteration:
                    break

        return AsyncStream(azip_with())

    # endregion --ops


def astream[I](input: AsyncIterable[I]) -> AsyncStream[I]:
    """Alias for the `AsyncStream` constructor."""
    return AsyncStream(input)

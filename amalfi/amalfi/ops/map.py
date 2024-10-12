import asyncio
from typing import Iterable

from ..core import AsyncFn, AsyncIterFn, Fn, IterFn


def map_[I, O](fn: Fn[I, O]) -> IterFn[I, O]:
    """
    Apply a sync function to each element of an iterable,
    yielding the mapped values.
    """

    def mapper(iterable: Iterable[I]) -> Iterable[O]:
        for item in iterable:
            yield fn(item)

    return mapper


def amap[I, O](fn: AsyncFn[I, O]) -> AsyncIterFn[I, O]:
    """
    Apply an async function to each element of an iterable.
    Raises exceptions from the async function.

    Analogous to `asyncio.gather` but for pipelines.
    """

    async def async_map(iterable: Iterable[I]) -> Iterable[O]:
        return await asyncio.gather(*map_(fn)(iterable))

    return async_map


def try_amap[I, O](fn: AsyncFn[I, O]) -> AsyncIterFn[I, O | BaseException]:
    """
    Apply an async function to each element of an iterable and return a list of
    results or exceptions.

    Analogous to `asyncio.gather` with `return_exceptions=True` but for pipelines.
    """

    async def async_map(iterable: Iterable[I]) -> Iterable[O | BaseException]:
        return await asyncio.gather(*map_(fn)(iterable), return_exceptions=True)

    return async_map

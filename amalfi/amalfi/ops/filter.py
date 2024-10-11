import asyncio
from typing import Iterable

from amalfi.core import AsyncFn, AsyncIterFn, Fn, IterFn


def filter_[T](fn: Fn[T, bool] | None) -> IterFn[T, T]:
    """Filter elements of an iterable using a predicate function."""

    def inner(iterable: Iterable[T]) -> Iterable[T]:
        return filter(fn, iterable)

    return inner


def afilter[T](fn: AsyncFn[T, bool]) -> AsyncIterFn[T, T]:
    """
    Filter elements of an iterable using an async predicate function.
    It will concurrently evaluate the predicate function for each element.
    """

    async def inner(iterable: Iterable[T]) -> Iterable[T]:
        results = await asyncio.gather(*map(fn, iterable))
        return (val for (val, result) in zip(iterable, results) if result)

    return inner

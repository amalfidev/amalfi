import asyncio
from typing import Iterable, cast, overload

from ..core import AsyncFn, AsyncIterFn, AsyncTypeGuardFn, Fn, IterFn, TypeGuardFn


@overload
def filter_[T](fn: None) -> IterFn[T, T]: ...


@overload
def filter_[T, S](fn: TypeGuardFn[T, S]) -> IterFn[T, S]: ...


@overload
def filter_[T](fn: Fn[T, bool]) -> IterFn[T, T]: ...


def filter_[T, S](fn: Fn[T, bool] | TypeGuardFn[T, S] | None) -> IterFn[T, S]:
    """
    Filter elements of an iterable using a predicate function.

    This function supports TypeGuard predicates for type narrowing.
    """

    def inner(iterable: Iterable[T]) -> Iterable[S]:
        return cast(Iterable[S], filter(fn, iterable))

    return inner


@overload
def afilter[T, S](fn: AsyncTypeGuardFn[T, S]) -> AsyncIterFn[T, S]: ...


@overload
def afilter[T](fn: AsyncFn[T, bool]) -> AsyncIterFn[T, T]: ...


def afilter[T, S](
    fn: AsyncFn[T, bool] | AsyncTypeGuardFn[T, S],
) -> AsyncIterFn[T, S]:
    """
    Filter elements of an iterable using an async predicate function.
    It will concurrently evaluate the predicate function for each element.

    This function supports async TypeGuard predicates for type narrowing.
    """

    async def inner(iterable: Iterable[T]) -> Iterable[S]:
        results = await asyncio.gather(*map(fn, iterable))
        filtered = (val for val, result in zip(iterable, results) if result)
        return cast(Iterable[S], filtered)

    return inner

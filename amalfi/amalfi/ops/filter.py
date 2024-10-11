import asyncio
from typing import Iterable, Protocol, TypeGuard, overload, runtime_checkable

from amalfi.core import AsyncFn, AsyncIterFn, Fn, IterFn


@runtime_checkable
class TypeGuardProtocol[T, S](Protocol):
    def __call__(self, arg: T) -> TypeGuard[S]: ...


@overload
def filter_[T](fn: None) -> IterFn[T, T]: ...


@overload
def filter_[T, S](fn: TypeGuardProtocol[T, S]) -> IterFn[T, S]: ...


@overload
def filter_[T](fn: Fn[T, bool]) -> IterFn[T, T]: ...


def filter_[T](fn: Fn[T, bool] | TypeGuardProtocol[T, T] | None) -> IterFn[T, T]:
    """
    Filter elements of an iterable using a predicate function.

    This function supports TypeGuard predicates for type narrowing.
    """

    def inner(iterable: Iterable[T]) -> Iterable[T]:
        return filter(fn, iterable)

    return inner


@runtime_checkable
class AsyncTypeGuardProtocol[T, S](Protocol):
    async def __call__(self, arg: T) -> TypeGuard[S]: ...


@overload
def afilter[T, S](fn: AsyncTypeGuardProtocol[T, S]) -> AsyncIterFn[T, S]: ...


@overload
def afilter[T](fn: AsyncFn[T, bool]) -> AsyncIterFn[T, T]: ...


def afilter[T](
    fn: AsyncFn[T, bool] | AsyncTypeGuardProtocol[T, T],
) -> AsyncIterFn[T, T]:
    """
    Filter elements of an iterable using an async predicate function.
    It will concurrently evaluate the predicate function for each element.

    This function supports async TypeGuard predicates for type narrowing.
    """

    async def inner(iterable: Iterable[T]) -> Iterable[T]:
        results = await asyncio.gather(*map(fn, iterable))
        return (val for (val, result) in zip(iterable, results) if result)

    return inner

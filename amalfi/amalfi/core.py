from __future__ import annotations

import inspect
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Coroutine,
    Iterable,
    Protocol,
    TypeGuard,
    Unpack,
    cast,
    runtime_checkable,
)

type Fn[I, O] = Callable[[I], O]
"""
A type alias for a synchronous function that takes an input of type `I
and returns an output of type `O`.
"""

type AsyncFn[I, O] = Callable[[I], Coroutine[Any, Any, O]]
"""
A type alias for an asynchronous function that takes an input of type `I`
and returns an output of type `O`.
```
"""

type VFn[**I, O] = Callable[I, O]
"""
A type alias for a variadic synchronous function,
ie. it takes multiple arguments of types `I` and returns an
output of type `O`.
"""

type AsyncVFn[**I, O] = Callable[I, Coroutine[Any, Any, O]]
"""
A type alias for a variadic asynchronous function,
ie. it takes multiple arguments of types `I` and returns an
output of type `O`. (V stands for 'Variadic')
"""

type TFn[*I, O] = Callable[[Unpack[I]], O]
"""
A type alias for a tuple-unpacking synchronous function,
ie. it takes a tuple of arguments of types `I` and returns an
output of type `O`.
"""

type AsyncTFn[*I, O] = Callable[[Unpack[I]], Coroutine[Any, Any, O]]
"""
A type alias for a tuple-unpacking asynchronous function,
ie. it takes a tuple of arguments of types `I` and returns an
output of type `O`.
"""


type IterFn[I, O] = Fn[Iterable[I], Iterable[O]]
"""
A type alias for a synchronous function that takes an iterable of type `Iterable[I]`
and returns an iterable of type `Iterable[O]`.
"""

type AsyncIterFn[I, O] = AsyncFn[Iterable[I], Iterable[O]]
"""
A type alias for an asynchronous function that takes an iterable of type `Iterable[I]`
and returns an iterable of type `Iterable[O]`.
"""


@runtime_checkable
class TypeGuardFn[T, S](Protocol):
    """
    A protocol for a type guard function that takes an argument of type `T`
    and returns a `TypeGuard[S]`.
    """

    def __call__(self, arg: T) -> TypeGuard[S]: ...


@runtime_checkable
class AsyncTypeGuardFn[T, S](Protocol):
    """
    A protocol for an asynchronous type guard function that takes an argument
    of type `T` and returns a `TypeGuard[S]`.
    """

    async def __call__(self, arg: T) -> TypeGuard[S]: ...


def identity[T](value: T) -> T:
    """Identity function. Returns the input value unchanged."""
    return value


def as_async[I, O](fn: Fn[I, O] | AsyncFn[I, O]) -> AsyncFn[I, O]:
    """
    Convert a sync function to an async function. Can be used as a decorator.
    If the input function is already async, it will be returned as is.
    """

    async def async_fn(x: I) -> O:
        result = (await fn(x)) if inspect.iscoroutinefunction(fn) else fn(x)
        return cast(O, result if not isinstance(result, Coroutine) else await result)

    return async_fn


def as_aiter[I](iterable: Iterable[I]) -> AsyncIterator[I]:
    """Convert an iterable to an async iterator."""

    async def aiter() -> AsyncIterator[I]:
        for item in iterable:
            yield item

    return aiter()

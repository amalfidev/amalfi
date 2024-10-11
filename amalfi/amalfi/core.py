from __future__ import annotations

import inspect
from typing import (
    Any,
    Callable,
    Coroutine,
    Iterable,
    Protocol,
    TypeGuard,
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
class TypeGuardProtocol[T, S](Protocol):
    def __call__(self, arg: T) -> TypeGuard[S]: ...


@runtime_checkable
class AsyncTypeGuardProtocol[T, S](Protocol):
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
        return cast(O, result)

    return async_fn

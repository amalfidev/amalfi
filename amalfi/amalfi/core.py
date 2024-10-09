from __future__ import annotations

import inspect
from typing import Any, Callable, Coroutine, Iterable, cast

type Fn[I, O] = Callable[[I], O]
type AsyncFn[I, O] = Callable[[I], Coroutine[Any, Any, O]]
type IterFn[I, O] = Fn[Iterable[I], Iterable[O]]


def identity[T](value: T) -> T:
    """
    Identity function.

    Examples:

    ```python
    result = identity(42)
    print(result) # 42
    ```
    """
    return value


def as_async[I, O](fn: Fn[I, O] | AsyncFn[I, O]) -> AsyncFn[I, O]:
    """
    Convert a sync function to an async function.
    Can be used as a decorator or a function.

    Examples:

    ```python
    add_one_async = as_async(add_one)
    result = await add_one_async(1)
    print(result) # 2

    @as_async
    def add_one(x: int) -> int:
        return x + 1

    result = await add_one(1)
    print(result) # 2
    ```
    """

    async def async_fn(x: I) -> O:
        result = (await fn(x)) if inspect.iscoroutinefunction(fn) else fn(x)
        return cast(O, result)

    return async_fn

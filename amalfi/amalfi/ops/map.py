import asyncio
from typing import Generator, Iterable, Literal, overload

from ..core import AsyncFn, AsyncIterFn, Fn, IterFn


def map_[I, O](fn: Fn[I, O]) -> IterFn[I, O]:
    """
    Apply a sync function to each element of an iterable,
    yielding the mapped values.

    This function is analogous to the built-in `map` function, but designed
    for use in pipelines/streams by being curried.

    Args:
        fn (Fn[I, O]): A synchronous mapping function

    Returns:
        IterFn[I, O]: the curried mapper that yields the mapped values

    Raises:
        Any exception raised by the function `fn` will be propagated.

    Example:
        >>> double = lambda x: x * 2
        >>> map_double = map_(double)
        >>> list(map_double([1, 2, 3]))
        [2, 4, 6]
    """

    def mapper(iterable: Iterable[I]) -> Generator[O, None, None]:
        for item in iterable:
            yield fn(item)

    return mapper


@overload
def amap[I, O](
    fn: AsyncFn[I, O], *, safe: Literal[False] = False
) -> AsyncIterFn[I, O]: ...


@overload
def amap[I, O](
    fn: AsyncFn[I, O], *, safe: Literal[True]
) -> AsyncIterFn[I, O | BaseException]: ...


def amap[I, O](
    fn: AsyncFn[I, O], *, safe: bool = False
) -> AsyncIterFn[I, O] | AsyncIterFn[I, O | BaseException]:
    """
    Apply an async function to each element of an iterable,
    returning a list of the mapped values.

    This function is analogous to `asyncio.gather` but designed for pipelines,
    meaning that the values are mapped in parallel and then collected into a list.

    Args:
        fn (AsyncFn[I, O]): An asynchronous mapping function
        safe (bool): If True, exceptions will be returned instead of raised.
            Analogous to the `return_exceptions` argument in `asyncio.gather`.

    Returns:
        AsyncIterFn[I, O] | AsyncIterFn[I, O | BaseException]: the curried async mapper
        that returns a list of mapped values or exceptions

    Raises:
        Any exception raised by the async function `fn` will be propagated if
        `safe` is False.

    Example:
        >>> async def async_double(x):
        ...     await asyncio.sleep(0.001)
        ...     return x * 2
        >>> amap_double = amap(async_double)
        >>> await amap_double([1, 2, 3])
        [2, 4, 6]

        >>> async def async_risky(x):
        ...     await asyncio.sleep(0.001)
        ...     if x == 2:
        ...         raise ValueError("Two is not allowed")
        ...     return x * 2
        >>> amap_risky = amap(async_risky, return_exceptions=True)
        >>> result = await amap_risky([1, 2, 3])
        >>> print(result)
        [2, ValueError("Two is not allowed"), 6]
    """

    async def async_map(
        iterable: Iterable[I],
    ) -> Iterable[O] | Iterable[O | BaseException]:
        return await asyncio.gather(*map_(fn)(iterable), return_exceptions=safe)

    return async_map

from typing import Any, Iterable

from ..core import AsyncFn, Fn


def tap[I](fn: Fn[I, Any]) -> Fn[I, I]:
    """
    Perform a synchronous side effect within a pipeline without altering the
    data flow.

    Designed as a curried function for use in pipelines.

    Example:
        >>> pipeline = pipe(1) | tap(print) | lambda x: x * 2
        >>> pipeline()
        2
    """

    def tapper(item: I) -> I:
        fn(item)
        return item

    return tapper


def tap_each[I](fn: Fn[I, Any]) -> Fn[Iterable[I], Iterable[I]]:
    """
    Perform a synchronous side effect to each item in a pipeline of iterables,
    without altering the data flow.

    Designed as a curried function for use in pipelines.

    Example:
        >>> pipeline = pipe([1, 2, 3]) | tap_each(print) | list
        >>> pipeline()
        1
        2
        3
        [1, 2, 3]
    """

    def tapper(items: Iterable[I]) -> Iterable[I]:
        items_ = list(items)
        for item in items_:
            fn(item)
        return items_

    return tapper


def atap[I](fn: AsyncFn[I, Any]) -> AsyncFn[I, I]:
    """
    Perform an asynchronous side effect within an async pipeline without
    altering the data flow.

    Designed as a curried function for use in pipelines.

    Example:
        >>> import asyncio
        >>> async def wait_and_log(x: int):
        ...     await asyncio.sleep(1)
        ...     print(f"Processing {x}")
        >>> pipeline = apipe(1) | atap(wait_and_log) | lambda x: x * 2
        >>> await pipeline()
        2
    """

    async def atapper(item: I) -> I:
        await fn(item)
        return item

    return atapper

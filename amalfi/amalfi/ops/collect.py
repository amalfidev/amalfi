from typing import AsyncIterator, Iterator

from ..core import AsyncFn, Fn


def collect_[I, O](fn: Fn[I, Iterator[O]]) -> Fn[I, list[O]]:
    """
    Collect all items from an iterator into a list.
    Useful for turning a generator into a list inside a pipeline.

    Designed as a curried function for use in pipelines.

    Args:
        fn (Fn[I, Iterator[O]]): A function that yields an iterator of items to collect

    Returns:
        Fn[I, list[O]]: The curried collector that collects the items into a list

    Raises:
        Any exception raised by the function `fn` will be propagated.

    Examples:
        >>> double = lambda x: (x * 2 for x in x)
        >>> collect_double = collect_(double)
        >>> collect_double([1, 2, 3])
        [2, 4, 6]

        >>> Pipeline.pipe([1, 2, 3]) | collect_(double) | sum
        12
    """

    def collector(input: I) -> list[O]:
        return [item for item in fn(input)]

    return collector


def acollect[I, O](fn: Fn[I, AsyncIterator[O]]) -> AsyncFn[I, list[O]]:
    """
    Collect all items from an asynchronous iterator into a list.
    Useful for turning a generator into a list inside an async pipeline.

    Designed as a curried function for use in pipelines.

    Args:
        fn (Fn[I, AsyncIterator[O]]): A function that yields an asynchronous
        iterator of items to collect

    Returns:
        AsyncFn[I, list[O]]: The curried collector that collects the items into a list

    Raises:
        Any exception raised by the function `fn` will be propagated.

    Examples:
        >>> async def double(x):
        ...     for i in x:
        ...         await asyncio.sleep(0.001)
        ...         yield i * 2
        >>> acollect_double = acollect_(double)
        >>> await acollect_double([1, 2, 3])
        [2, 4, 6]
    """

    async def collector(input: I) -> list[O]:
        return [item async for item in fn(input)]

    return collector

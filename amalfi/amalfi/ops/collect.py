from typing import AsyncIterator, Iterator

from ..core import AsyncFn, Fn


def collect[I, O](fn: Fn[I, Iterator[O]]) -> Fn[I, list[O]]:
    """
    Collect all items from an iterator into a list.
    Useful for turning a generator into a list inside a pipeline.
    """

    def inner(input: I) -> list[O]:
        return [item for item in fn(input)]

    return inner


def acollect[I, O](fn: Fn[I, AsyncIterator[O]]) -> AsyncFn[I, list[O]]:
    """
    Collect all items from an asynchronous iterator into a list.
    Useful for turning a generator into a list inside an async pipeline.
    """

    async def inner(input: I) -> list[O]:
        return [item async for item in fn(input)]

    return inner

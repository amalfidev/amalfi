import asyncio
from typing import Iterable

from ..core import AsyncFn, Fn


def map_[I, O](fn: Fn[I, O]) -> Fn[Iterable[I], Iterable[O]]:
    """
    Apply a sync function to each element of an iterable.

    **Args:**
    - `fn`: A callable that takes an input of type `I` and returns
    an output of type `O`.

    **Returns:**
    - A callable that takes an iterable of type `Iterable[I]` and returns
    """
    return lambda iterable: map(fn, iterable)


def async_map[I, O](fn: AsyncFn[I, O]) -> AsyncFn[Iterable[I], Iterable[O]]:
    """
    Apply an async function to each element of an iterable.
    Analogous to `asyncio.gather` but for pipelines.

    **Args:**
    - `fn`: A callable that takes an input of type `I` and returns
    an output of type `O`.

    **Returns:**
    - A callable that takes an iterable of type `Iterable[I]` and returns
    an Iterable[O] in a coroutine.
    """

    async def async_map(iterable: Iterable[I]) -> Iterable[O]:
        return await asyncio.gather(*map_(fn)(iterable))

    return async_map

import asyncio
from typing import Generator, Iterable, Literal, overload

from amalfi.core import AsyncFn, AsyncTFn, Fn, TFn


def starmap_[*I, O](fn: TFn[*I, O]) -> Fn[Iterable[tuple[*I]], Iterable[O]]:
    """
    Apply a sync tuple-unpacking function to each element of an iterable,
    yielding the mapped values.

    Analogous to `itertools.starmap` but curried for use in pipelines.

    Args:
        fn (TFn[*I, O]): A synchronous tuple-unpacking function.

    Returns:
        Fn[[Iterable[tuple[*I]]], Generator[O, None, None]]:
            The curried mapper.

    Examples
    --------
    >>> result = starmap(lambda x, y: x + y)([(1, 2), (3, 4), (5, 6)])
    >>> assert result == [3, 7, 11]

    >>> from amalfi.pipeline import pipe
    >>> result = pipe([(1, 2), (3, 4), (5, 6)]) | starmap(lambda x, y: x + y) | list
    >>> assert result == [3, 7, 11]
    """

    def starmapper(iterable: Iterable[tuple[*I]]) -> Generator[O, None, None]:
        for item in iterable:
            yield fn(*item)

    return starmapper


@overload
def astarmap[*I, O](
    fn: AsyncTFn[*I, O], *, safe: Literal[False] = False
) -> AsyncFn[Iterable[tuple[*I]], list[O]]: ...


@overload
def astarmap[*I, O](
    fn: AsyncTFn[*I, O], *, safe: Literal[True]
) -> AsyncFn[Iterable[tuple[*I]], list[O | BaseException]]: ...


def astarmap[*I, O](
    fn: AsyncTFn[*I, O], *, safe: bool = False
) -> AsyncFn[Iterable[tuple[*I]], list[O] | list[O | BaseException]]:
    """
    Apply an async tuple-unpacking function to each element of an iterable,
    yielding the mapped values.

    Analogous to `asyncio.gather` but designed for pipelines, meaning that the
    values are mapped in parallel and then collected into a list.

    Args:
        fn (AsyncTFn[*I, O]): An asynchronous tuple-unpacking function.
        safe (bool): If True, exceptions will be returned instead of raised.
            Analogous to the `return_exceptions` argument in `asyncio.gather`.

    Returns:
        AsyncFn[[Iterable[tuple[*I]]], list[O] | list[O | BaseException]]:
            The curried async mapper.

    Examples
    --------
    >>> result = await astarmap(lambda x, y: x + y)([(1, 2), (3, 4), (5, 6)])
    >>> assert result == [3, 7, 11]

    >>> from amalfi.pipeline import apipe
    >>> result = await (
            apipe([(1, 2), (3, 4), (5, 6)])
            | astarmap(lambda x, y: x + y)
            | list
        )
    >>> assert result == [3, 7, 11]
    """

    async def async_starmapper(
        iterable: Iterable[tuple[*I]],
    ) -> list[O] | list[O | BaseException]:
        return await asyncio.gather(*starmap_(fn)(iterable), return_exceptions=safe)

    return async_starmapper

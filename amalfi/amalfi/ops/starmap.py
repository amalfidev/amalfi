import asyncio
from typing import Generator, Iterable, Literal, overload

from amalfi.core import AsyncFn, AsyncTFn, Fn, TFn


def starmap[*I, O](fn: TFn[*I, O]) -> Fn[Iterable[tuple[*I]], Iterable[O]]:
    """
    Apply a sync tuple-unpacking function to each element of an iterable,
    yielding the mapped values.

    Analogous to `itertools.starmap` but curried for use in pipelines.

    Args:
        fn (TFn[*I, O]): A synchronous tuple-unpacking function.

    Returns:
        Fn[[Iterable[tuple[*I]]], Generator[O, None, None]]:
            The curried mapper.
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
    async def async_starmapper(
        iterable: Iterable[tuple[*I]],
    ) -> list[O] | list[O | BaseException]:
        return await asyncio.gather(*starmap(fn)(iterable), return_exceptions=safe)

    return async_starmapper

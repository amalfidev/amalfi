import asyncio
from typing import Iterable, cast, overload

from ..core import AsyncFn, AsyncIterFn, AsyncTypeGuardFn, Fn, IterFn, TypeGuardFn


@overload
def filter_[T](fn: None) -> IterFn[T, T]: ...


@overload
def filter_[T, S](fn: TypeGuardFn[T, S]) -> IterFn[T, S]: ...


@overload
def filter_[T](fn: Fn[T, bool]) -> IterFn[T, T]: ...


def filter_[T, S](fn: Fn[T, bool] | TypeGuardFn[T, S] | None) -> IterFn[T, S]:
    """
    Filter elements of an iterable using a predicate function.

    Designed as a curried function for use in pipelines.
    This function supports TypeGuard predicates for type narrowing.

    Args:
        fn (Fn[T, bool] | TypeGuardFn[T, S] | None): A predicate function

    Returns:
        IterFn[T, S]: The curried filter that yields the filtered values

    Raises:
        Any exception raised by the predicate function will be propagated.

    Examples:
        >>> is_even = lambda x: x % 2 == 0
        >>> filter_even = filter_(is_even)
        >>> list(filter_even([1, 2, 3, 4]))
        [2, 4]
        >>> Pipeline.pipe([1, 2, 3, 4]) | filter_(is_even) | list
        [2, 4]
    """

    def inner_filter(iterable: Iterable[T]) -> Iterable[S]:
        return cast(Iterable[S], filter(fn, iterable))

    return inner_filter


@overload
def afilter[T, S](fn: AsyncTypeGuardFn[T, S]) -> AsyncIterFn[T, S]: ...


@overload
def afilter[T](fn: AsyncFn[T, bool]) -> AsyncIterFn[T, T]: ...


def afilter[T, S](
    fn: AsyncFn[T, bool] | AsyncTypeGuardFn[T, S],
) -> AsyncIterFn[T, S]:
    """
    Filter elements of an iterable using an async predicate function.
    It will concurrently evaluate the predicate function for each element.

    Designed as a curried function for use in pipelines.
    This function supports async TypeGuard predicates for type narrowing.

    Args:
        fn (AsyncFn[T, bool] | AsyncTypeGuardFn[T, S]): An async predicate function

    Returns:
        AsyncIterFn[T, S]: The curried filter that yields the filtered values

    Raises:
        Any exception raised by the predicate function will be propagated.

    Examples:
        >>> async def wait_and_check_even(x: int) -> bool:
        ...     await asyncio.sleep(0.001)
        ...     return x % 2 == 0
        >>> afilter_even = afilter_(wait_and_check_even)
        >>> list(await afilter_even([1, 2, 3, 4]))
        [2, 4]
        >>> result = await (
                Pipeline.apipe([1, 2, 3, 4])
                | afilter_(wait_and_check_even)
                | list
            ).run()
        >>> result
        [2, 4]
    """

    async def inner_filter(iterable: Iterable[T]) -> Iterable[S]:
        results = await asyncio.gather(*map(fn, iterable))
        filtered = (val for val, result in zip(iterable, results) if result)
        return cast(Iterable[S], filtered)

    return inner_filter

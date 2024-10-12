from functools import reduce
from typing import Iterable

from ..core import AsyncFn, AsyncVFn, Fn, VFn


def reduce_[I, O](fn: VFn[[O, I], O], initial: O) -> Fn[Iterable[I], O]:
    """
    Reduce an iterable to a single value using a function.

    Designed as a curried function for use in pipelines.

    Args:
        fn (VFn[[O, I], O]): Reducer function
        initial (O): The initial value for the reduction

    Returns:
        Fn[Iterable[I], O]: The curried reducer that reduces the iterable to a
        single value

    Raises:
        Any exception raised by the function `fn` will be propagated.

    Examples:
        >>> add = lambda x, y: x + y
        >>> reduce_add = reduce_(add, 0)
        >>> reduce_add([1, 2, 3, 4])
        10
        >>> pipeline = Pipeline.pipe([1, 2, 3, 4]) | reduce_(add, 0)
        >>> pipeline.run()
        10
    """

    def inner(iterable: Iterable[I]) -> O:
        return reduce(fn, iterable, initial)

    return inner


def areduce[I, O](fn: AsyncVFn[[O, I], O], initial: O) -> AsyncFn[Iterable[I], O]:
    """
    Reduce an iterable to a single value using an asynchronous function.

    Designed as a curried function for use in pipelines.

    Args:
        fn (AsyncVFn[[O, I], O]): Reducer function
        initial (O): The initial value for the reduction

    Returns:
        AsyncFn[Iterable[I], O]: The curried reducer that reduces the iterable to a
        single value

    Raises:
        Any exception raised by the function `fn` will be propagated.

    Examples:
        >>> async def wait_and_add(x: int, y: int) -> int:
        ...     await asyncio.sleep(0.01)
        ...     return x + y
        >>> asum = areduce(wait_and_add, 0)
        >>> await asum([1, 2, 3, 4])
        10
        >>> pipeline = Pipeline.apipe([1, 2, 3, 4]) | areduce(wait_and_add, 0)
        >>> await pipeline.run()
        10
    """

    async def reducer(iterable: Iterable[I]) -> O:
        result = initial
        for item in iterable:
            result = await fn(result, item)
        return result

    return reducer

from typing import Any, Callable, Coroutine, Iterable


def fmap[I, O](fn: Callable[[I], O]) -> Callable[[Iterable[I]], Iterable[O]]:
    """
    Apply a sync function to each element of an iterable.

    **Args:**
    - `fn`: A callable that takes an input of type `I` and returns
    an output of type `O`.

    **Returns:**
    - A callable that takes an iterable of type `Iterable[I]` and returns
    """
    return lambda iterable: map(fn, iterable)


def amap[I, O](
    fn: Callable[[I], Coroutine[Any, Any, O]],
) -> Callable[[Iterable[I]], Coroutine[Any, Any, Iterable[O]]]:
    """
    Apply an async function to each element of an iterable.

    **Args:**
    - `fn`: A callable that takes an input of type `I` and returns
    an output of type `O`.

    **Returns:**
    - A callable that takes an iterable of type `Iterable[I]` and returns
    an async iterable of type `Awaitable[Iterable[O]]`.
    """

    async def async_map(iterable: Iterable[I]) -> Iterable[O]:
        return [await fn(item) for item in iterable]

    return async_map

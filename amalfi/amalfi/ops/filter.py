from typing import Iterable

from amalfi.core import Fn, IterFn


def filter_[T](fn: Fn[T, bool] | None) -> IterFn[T, T]:
    """Filter elements of an iterable using a predicate function."""

    def inner(iterable: Iterable[T]) -> Iterable[T]:
        return filter(fn, iterable)

    return inner

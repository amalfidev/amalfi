from typing import Any, Callable, Iterable, Optional, overload

# ... existing imports ...


@overload
def filter_[T](fn: None, iterable: Iterable[T]) -> Iterable[T]: ...


@overload
def filter_[T](fn: Callable[[T], Any], iterable: Iterable[T]) -> Iterable[T]: ...


def filter_[T](fn: Optional[Callable[[T], Any]], iterable: Iterable[T]) -> Iterable[T]:
    """Filter elements of an iterable using a predicate function."""
    if fn is None:
        return filter(bool, iterable)
    return filter(fn, iterable)

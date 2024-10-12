from functools import reduce
from typing import Callable, Iterable


def reduce_[I, O](fn: Callable[[O, I], O], iterable: Iterable[I], initial: O) -> O:
    return reduce(fn, iterable, initial)

from __future__ import annotations

from itertools import islice, takewhile
from typing import Any, Iterable, Iterator, overload

from amalfi.ops import tap

from ..core import Fn, as_aiter
from ..pipeline import AsyncPipeline, Pipeline, apipe, pipe
from .astream import AsyncStream


class Stream[I]:
    """
    A synchronous iterable stream of values that can be processed in a sequential
    manner by applying a series of synchronous transformations to the data.

    This class allows the creation of streams where each step is a function that
    transforms the data in an lazy manner. The steps are composed together,
    enabling a fluent interface for processing data through a series of
    transformations.

    Type Parameters:
    - `I`: The type of the items in the input iterable.

    Attributes:
    - `input`: The input iterable to the stream, to be transformed by the functions.

    Examples:

    Basic usage with integer transformations:

    ```python
    from amalfi.stream import stream

    def add_one(x: int) -> int:
        return x + 1

    def multiply_by_two(x: int) -> int:
        return x * 2

    # Create a stream that adds one and then multiplies by two
    result = (
        stream([1, 2, 3, 4, 5])
            .map(add_one)
            .filter(lambda x: x % 2 == 0)
            .take(2)
            .collect()
        )
    assert result == [2, 4]
    ```
    """

    _iter: Iterable[I]

    def __init__(self, input: Iterable[I]):
        """Initialize the `Stream` with an input iterable."""
        self._iter = input

    def __iter__(self) -> Iterator[I]:
        """Iterate over the stream"""
        yield from self._iter

    def __repr__(self) -> str:
        """Return a string representation of the stream"""
        return f"Stream({self._iter.__repr__()})"

    def to_async(self) -> AsyncStream[I]:
        """Convert the stream to an async stream."""
        return AsyncStream(as_aiter(self))

    def to_pipe(self) -> Pipeline[Iterable[I], Iterable[I]]:
        """Convert the stream to a pipeline."""
        return pipe(iter(self))

    def to_apipe(self) -> AsyncPipeline[Iterable[I], Iterable[I]]:
        """Convert the stream to an async pipeline."""
        return apipe(iter(self))

    # region: --collect
    @overload
    def collect(self, into: None = None) -> list[I]: ...

    @overload
    def collect[T](self, into: Fn[Iterable[I], T]) -> T: ...

    def collect[T](self, into: Fn[Iterable[I], T] | None = None) -> T | list[I]:
        """
        Execute the stream on the input and collect the results into a custom
        collector function, which defaults to a list.

        This method will consume the stream and return the collected result.
        If the stream is infinite, this method will never return.

        A custom collector can be passed. It should be a function that takes an
        iterable and returns the desired type `T`. It defaults to a list.

        Args:
            into (Fn[Iterable[I], T] | None): An optional custom collector function,
            which defaults to a list.

        Returns:
            T | list[I]: The collected result of the stream.

        Examples
        --------
        >>> result = stream([1, 2, 3, 4, 5]).map(lambda x: x + 1).collect()
        [2, 3, 4, 5, 6]
        >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect(into=tuple)
        (2, 3, 4)
        """
        if not into:
            return list(self)
        return into(self)

    # endregion --collect

    # region: --ops
    def map[O](self, fn: Fn[I, O]) -> Stream[O]:
        """
        Adds a mapping step to the stream, returning a new stream of the
        mapped values.

        Args:
            fn (Fn[I, O]): A synchronous mapping function

        Returns:
            Stream[O]: a new stream of the mapped values

        Examples
        --------
        >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect()
        >>> assert result == [2, 3, 4]
        """

        return Stream(map(fn, self))

    def filter(self, fn: Fn[I, bool] | None) -> Stream[I]:
        """
        Adds a filtering step to the stream, returning a new stream of the
        filtered values.

        Args:
            fn (Fn[I, bool] | None): A synchronous filtering function. If `None` is
            passed, the stream will be filtered to exclude `None` values.

        Returns:
            Stream[I]: a new stream of the filtered values

        Examples
        --------
        >>> result = stream([1, 2, 3]).filter(lambda x: x % 2 == 0).collect()
        >>> assert result == [2]
        >>> result = stream([1, None, 3]).filter(None).collect()
        >>> assert result == [1, 3]
        """
        return Stream(filter(fn, self))

    def take(self, n: int) -> Stream[I]:
        """
        Take the first `n` values from the stream.

        Args:
            n (int): The number of values to take from the stream

        Returns:
            Stream[I]: a new stream of the first `n` values
        """
        return Stream(islice(self, n))

    def take_while(self, fn: Fn[I, bool]) -> Stream[I]:
        """
        Take values from the stream while the predicate is true.

        Args:
            fn (Fn[I, bool]): A synchronous predicate function

        Returns:
            Stream[I]: a new stream of the values taken while the predicate is true
        """
        return Stream(takewhile(fn, self))

    def default(self, default: I) -> Stream[I]:
        """
        Returns a stream with the default value if the stream is empty.

        Args:
            default (I): The default value to return if the stream is empty

        Returns:
            Stream[I]: a new stream with the default value if the stream is empty

        Examples
        --------
        >>> result = stream([1, 2, 3]).default(0).collect()
        >>> assert result == [1, 2, 3]
        >>> result = stream([]).default(0).collect()
        >>> assert result == [0]
        """

        def default_gen() -> Iterator[I]:
            stream_iter = iter(self)
            try:
                yield next(stream_iter)
                yield from stream_iter
            except StopIteration:
                yield default

        return Stream(default_gen())

    def tap(self, fn: Fn[I, Any]) -> Stream[I]:
        """
        Perform a synchronous side effect within a stream without altering the
        data flow.

        Examples
        --------
        >>> result = stream([1, 2, 3]).tap(print).collect()
        1
        2
        3
        >>> print(result)
        [1, 2, 3]
        """
        return self.map(tap(fn))

    # endregion --ops


def stream[I](input: Iterable[I]) -> Stream[I]:
    """Alias for the `Stream` constructor.

    Examples
    --------
    >>> result = stream([1, 2, 3]).map(lambda x: x + 1).collect()
    >>> assert result == [2, 3, 4]
    """
    return Stream(input)

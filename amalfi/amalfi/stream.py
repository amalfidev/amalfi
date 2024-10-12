from __future__ import annotations

from typing import Iterable, Iterator

from .core import Fn, identity


class Stream[I, O]:
    input: Iterable[I]
    fn: Fn[I, O]

    def __init__(self, input: Iterable[I], fn: Fn[I, O]):
        """Initialize the `Stream` with an input value and a function."""
        self.input = input
        self.fn = fn

    def __iter__(self) -> Iterator[O]:
        """Execute the stream on the stored input."""
        for item in self.input:
            yield self.fn(item)

    def collect(self) -> list[O]:
        """Execute the stream on the stored input and collect the results."""
        return list(self.__iter__())

    def step[U](self, fn: Fn[O, U]) -> Stream[I, U]:
        """
        Adds a function as a step to the stream.

        This method creates a new `Stream` instance that composes the current stream
        function with the provided function `fn`.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Stream[I, U](self.input, composed_fn)

    def __or__[U](self, fn: Fn[O, U]) -> Stream[I, U]:
        """
        Adds a function as a step to the stream using the `|` operator.
        Alias for `#step` method.
        """

        return self.step(fn)

    def with_input(self, value: Iterable[I]) -> Stream[I, O]:
        """Change the input value of the stream."""
        return Stream(value, self.fn)

    def concat[U](self, other: Stream[O, U]) -> Stream[I, U]:
        """
        Concatenate two streams. The output of the current stream is passed
        as input to the other stream, regardless of the input value of the
        other stream.
        """

        def concat_fn(value: I) -> U:
            return other.fn(self.fn(value))

        return Stream[I, U](self.input, concat_fn)

    def __add__[U](self, other: Stream[O, U]) -> Stream[I, U]:
        """
        Concatenate two streams using the `+` operator.
        Alias for `#concat` method.
        """
        return self.concat(other)

    @classmethod
    def ingest[T](cls, input: Iterable[T]) -> Stream[T, T]:
        """Create a new Stream instance with the given input."""

        return Stream(input, identity)

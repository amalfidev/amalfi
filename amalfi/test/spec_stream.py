from typing import Iterable

import pytest

from amalfi.stream import Stream

from .stub import add_one, multiply_by_two, yield_range


@pytest.fixture
def input():
    return yield_range(1, 4)


class TestStream:
    def test_ingest(self, input: Iterable[int]):
        stream = Stream.ingest(input)
        assert stream.collect() == [1, 2, 3]

    def test_compose_stream(self, input: Iterable[int]):
        stream = Stream.ingest(input) | add_one
        assert stream.collect() == [2, 3, 4]

    def test_change_input(self, input: Iterable[int]):
        stream = Stream.ingest(input) | add_one
        stream = stream.with_input(yield_range(2, 5))
        assert stream.collect() == [3, 4, 5]

    def test_concat(self, input: Iterable[int]):
        stream1 = Stream.ingest(input) | add_one
        stream2 = Stream.ingest([0]) | multiply_by_two
        stream = stream1 + stream2
        assert stream.collect() == [4, 6, 8]

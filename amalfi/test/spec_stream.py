from collections import deque
from typing import Iterable

import pytest

from amalfi.ops import map_
from amalfi.stream import Stream

from .stub import add_one, multiply_by_two, yield_range


@pytest.fixture
def input():
    return yield_range(1, 4)


class TestStream:
    def test_collect(self, input: Iterable[int]):
        stream = Stream(input)
        assert list(stream) == [1, 2, 3]

    def test_with_strings(self):
        stream = Stream.from_str("lorem ipsum dolor sit amet")
        assert list(stream) == ["lorem ipsum dolor sit amet"]

    def test_with_bytes(self):
        stream = Stream.from_bytes(b"lorem ipsum dolor sit amet")
        assert list(stream) == [b"lorem ipsum dolor sit amet"]

    class TestCollect:
        def test_collect(self, input: Iterable[int]):
            stream = Stream(input)
            assert stream.collect() == [1, 2, 3]

        @pytest.mark.parametrize(
            "into, expected",
            [
                (set, {1, 2, 3}),
                (list, [1, 1, 2, 3]),
                (tuple, (1, 1, 2, 3)),
                (deque, deque([1, 1, 2, 3])),
            ],
        )
        def test_collect_into(self, into: type, expected: type):
            input = [1, 1, 2, 3]  # includes duplicates
            stream = Stream(input)
            assert stream.collect(into=into) == expected

    class TestMap:
        def test_map(self, input: Iterable[int]):
            stream = Stream(input).map(add_one)
            assert stream.collect() == [2, 3, 4]

        def test_map_op(self, input: Iterable[int]):
            doubled = map_(multiply_by_two)
            stream = Stream(input)
            assert list(doubled(stream)) == [2, 4, 6]

    class TestFilter:
        def test_filter(self, input: Iterable[int]):
            stream = Stream(input).map(lambda x: x + 1).filter(lambda x: x % 2 == 0)
            assert stream.collect() == [2, 4]

    class TestTake:
        def test_take(self, input: Iterable[int]):
            stream = Stream(input).map(lambda x: x + 1).take(2)
            assert stream.collect() == [2, 3]

        def test_take_while(self):
            result = (
                Stream(yield_range(0, 10))
                .map(lambda x: x + 1)
                .take_while(lambda x: x < 3)
                .collect()
            )
            assert result == [1, 2]

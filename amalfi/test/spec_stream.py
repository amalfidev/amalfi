from typing import Iterable

import pytest

from amalfi.stream import AsyncStream, Stream

from .stub import (
    add_one,
    async_yield_range,
    multiply_by_two,
    wait_and_add_one,
    yield_range,
)


@pytest.fixture
def input():
    return yield_range(1, 4)


class TestStream:
    def test_ingest(self, input: Iterable[int]):
        stream = Stream.ingest(input)
        assert stream.collect() == [1, 2, 3]

    @pytest.mark.anyio
    async def test_aingest(self):
        stream = Stream.aingest(async_yield_range(1, 4)) | add_one
        assert await stream.collect() == [2, 3, 4]

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
        stream = stream1 > stream2
        assert stream.collect() == [4, 6, 8]

    def test_iter(self):
        input = yield_range(0, 3)
        stream = Stream.ingest(input) | add_one

        for i, o in enumerate(stream):
            assert o == add_one(i)

    def test_iter_to_tuple(self, input: Iterable[int]):
        stream = Stream.ingest(input) | add_one
        assert tuple(stream) == (2, 3, 4)

    def test_stream_as_input(self):
        input_stream = Stream.ingest(yield_range(1, 4)) | add_one
        stream = Stream.ingest(input_stream) | multiply_by_two
        assert stream.collect() == [4, 6, 8]

    def test_collect_as_type(self, input: Iterable[int]):
        stream = Stream.ingest(input) | add_one
        assert stream.collect(into=tuple) == (2, 3, 4)


class TestAsyncStream:
    @pytest.mark.anyio
    async def test_ingest(self):
        stream = (
            AsyncStream.ingest(async_yield_range(1, 4)) | add_one | wait_and_add_one
        )
        assert await stream.collect() == [3, 4, 5]

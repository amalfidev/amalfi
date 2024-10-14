from collections import deque
from typing import AsyncIterable, Iterable

import pytest

from amalfi.ops import map_
from amalfi.ops.map import amap
from amalfi.pipeline import AsyncPipeline, Pipeline, pipe
from amalfi.stream import AsyncStream, Stream, astream, stream

from .stub import add_one, ayield_range, multiply_by_two, wait_and_add_one, yield_range


@pytest.fixture
def input():
    return yield_range(1, 4)


@pytest.fixture
def ainput():
    return ayield_range(1, 4)


class TestStream:
    def test_init(self, input: Iterable[int]):
        stream = Stream(input)
        assert list(stream) == [1, 2, 3]

    def test_alias(self, input: Iterable[int]):
        s = stream(input)
        assert list(s) == [1, 2, 3]

    @pytest.mark.anyio
    async def test_to_async(self, input: Iterable[int]):
        async_stream = stream(input).to_async()
        assert isinstance(async_stream, AsyncStream)
        assert [i async for i in async_stream] == [1, 2, 3]

    def test_to_pipe(self, input: Iterable[int]):
        pipeline = stream(input).to_pipe() | map_(add_one) | sum
        assert isinstance(pipeline, Pipeline)
        assert pipeline.run() == 9

    @pytest.mark.anyio
    async def test_to_apipe(self, input: Iterable[int]):
        apipeline = stream(input).to_apipe() | amap(wait_and_add_one) | sum
        assert isinstance(apipeline, AsyncPipeline)
        assert await apipeline.run() == 9

    class TestStringAndBytes:
        def test_with_strings(self):
            chars = stream("lorem").collect()
            assert chars == ["l", "o", "r", "e", "m"]

        def test_with_str_iterable(self):
            words = stream(["lorem", "ipsum"])
            assert words.collect() == ["lorem", "ipsum"]

        def test_with_bytes(self):
            byte_stream = stream(b"lorem")
            assert list(byte_stream) == [108, 111, 114, 101, 109]

        def test_from_bytes_iterable(self):
            bytes = stream([b"lorem", b"ipsum"])
            assert list(bytes) == [b"lorem", b"ipsum"]

    class TestCollect:
        def test_collect(self, input: Iterable[int]):
            assert stream(input).collect() == [1, 2, 3]

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
            assert stream(input).collect(into=into) == expected

        def test_collect_into_lambda(self, input: Iterable[int]):
            result = stream(input).collect(into=lambda x: [2 * i for i in x])
            assert result == [2, 4, 6]

        def test_collect_into_pipeline(self, input: Iterable[int]):
            result = (
                stream(input)
                .collect(into=pipe)
                .step(map_(lambda x: x + 1))
                .step(sum)
                .run()
            )
            assert result == 9

    class TestMap:
        def test_map(self, input: Iterable[int]):
            result = stream(input).map(add_one).collect()
            assert result == [2, 3, 4]

        def test_map_op(self, input: Iterable[int]):
            doubled = map_(multiply_by_two)
            result = list(doubled(stream(input)))
            assert result == [2, 4, 6]

    class TestFilter:
        def test_filter(self, input: Iterable[int]):
            result = (
                stream(input)
                .map(lambda x: x + 1)
                .filter(lambda x: x % 2 == 0)
                .collect()
            )
            assert result == [2, 4]

    class TestTake:
        def test_take(self, input: Iterable[int]):
            result = stream(input).map(lambda x: x + 1).take(2).collect()
            assert result == [2, 3]

        def test_take_while(self):
            result = (
                stream(yield_range(0, 10))
                .map(lambda x: x + 1)
                .take_while(lambda x: x < 3)
                .collect()
            )
            assert result == [1, 2]


class TestAsyncStream:
    @pytest.mark.anyio
    async def test_init(self, ainput: AsyncIterable[int]):
        stream = AsyncStream(ainput)
        assert [i async for i in stream] == [1, 2, 3]

    @pytest.mark.anyio
    async def test_alias(self, ainput: AsyncIterable[int]):
        assert [i async for i in astream(ainput)] == [1, 2, 3]

    @pytest.mark.anyio
    async def test_to_pipe(self, ainput: AsyncIterable[int]):
        pipeline = (await astream(ainput).to_pipe()) | map_(add_one) | sum
        assert isinstance(pipeline, Pipeline)
        assert pipeline.run() == 9

    @pytest.mark.anyio
    async def test_to_apipe(self, input: Iterable[int]):
        apipeline = stream(input).to_apipe() | amap(wait_and_add_one) | sum
        assert isinstance(apipeline, AsyncPipeline)
        assert await apipeline.run() == 9

    class TestCollect:
        @pytest.mark.anyio
        async def test_collect(self, ainput: AsyncIterable[int]):
            assert await astream(ainput).collect() == [1, 2, 3]

        @pytest.mark.anyio
        async def test_collect_into(self, ainput: AsyncIterable[int]):
            as_tuple = await astream(ainput).collect(into=tuple)
            assert as_tuple == (1, 2, 3)

        @pytest.mark.anyio
        async def test_collect_into_pipeline(self, ainput: AsyncIterable[int]):
            result = (
                (await astream(ainput).collect(into=pipe))
                .step(map_(lambda x: x + 1))
                .step(sum)
                .to_async()
                .step(wait_and_add_one)
            )
            assert await result.run() == 10

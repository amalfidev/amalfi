import asyncio
from typing import AsyncIterable

import pytest

from amalfi.ops import map_
from amalfi.ops.map import amap
from amalfi.pipeline import AsyncPipeline, Pipeline, pipe
from amalfi.stream import AsyncStream, astream

from .stub import add_one, ayield_range, wait_and_add_one, wait_and_double


@pytest.fixture
def ainput():
    return ayield_range(1, 4)


class TestAsyncStream:
    @pytest.mark.anyio
    async def test_init(self, ainput: AsyncIterable[int]):
        s = AsyncStream(ainput)
        assert [i async for i in s] == [1, 2, 3]

    @pytest.mark.anyio
    async def test_alias(self, ainput: AsyncIterable[int]):
        assert [i async for i in astream(ainput)] == [1, 2, 3]

    @pytest.mark.anyio
    async def test_to_pipe(self, ainput: AsyncIterable[int]):
        p = (await astream(ainput).to_pipe()) | map_(add_one) | sum
        assert isinstance(p, Pipeline)
        assert p.run() == 9

    @pytest.mark.anyio
    async def test_to_apipe(self, ainput: AsyncIterable[int]):
        ap = (await astream(ainput).to_apipe()) | amap(wait_and_add_one) | sum
        assert isinstance(ap, AsyncPipeline)
        assert await ap.run() == 9

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
            apipeline = (
                (await astream(ainput).collect(into=pipe))
                .step(map_(lambda x: x + 1))
                .step(sum)
                .to_async()
                .step(wait_and_add_one)
            )
            assert isinstance(apipeline, AsyncPipeline)
            assert await apipeline.run() == 10

    class TestMap:
        @pytest.mark.anyio
        async def test_map(self, ainput: AsyncIterable[int]):
            s = astream(ainput).map(wait_and_add_one).map(add_one).map(wait_and_double)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [6, 8, 10]

    class TestFilter:
        @pytest.mark.anyio
        async def test_filter(self, ainput: AsyncIterable[int]):
            s = astream(ainput).filter(lambda x: x % 2 == 0)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [2]

        @pytest.mark.anyio
        async def test_afilter(self, ainput: AsyncIterable[int]):
            async def is_even(x: int) -> bool:
                await asyncio.sleep(0.001)
                return x % 2 == 0

            s = astream(ainput).filter(is_even)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [2]

        @pytest.mark.anyio
        async def test_filter_none(self):
            async def ainput_with_none():
                await asyncio.sleep(0.001)
                yield 1
                yield None
                yield 3

            s = astream(ainput_with_none()).filter(None)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [1, 3]

    class TestTake:
        @pytest.mark.anyio
        async def test_take(self, ainput: AsyncIterable[int]):
            s = astream(ainput).take(2)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [1, 2]

        @pytest.mark.anyio
        async def test_take_while(self, ainput: AsyncIterable[int]):
            s = astream(ainput).take_while(lambda x: x < 3)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [1, 2]

        @pytest.mark.anyio
        async def test_take_while_with_async_fn(self, ainput: AsyncIterable[int]):
            async def is_less_than_three(x: int) -> bool:
                await asyncio.sleep(0.001)
                return x < 3

            s = astream(ainput).take_while(is_less_than_three)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [1, 2]

    class TestDefault:
        @pytest.mark.anyio
        async def test_default(self, ainput: AsyncIterable[int]):
            s = astream(ainput).default(0)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [1, 2, 3]

        @pytest.mark.anyio
        async def test_default_if_empty_empty(self):
            s = astream(ayield_range(1, 1)).default(0)
            assert isinstance(s, AsyncStream)
            assert await s.collect() == [0]

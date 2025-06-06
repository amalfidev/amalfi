import asyncio

import pytest

from amalfi import VFn
from amalfi.ops import areduce, reduce_
from amalfi.pipeline import apipe, pipe

add: VFn[[int, int], int] = lambda x, y: x + y  # noqa: E731


async def wait_and_add(x: int, y: int) -> int:
    await asyncio.sleep(0.001)
    return x + y


class TestReduce:
    def test_reduce(self):
        sum_ = reduce_(add, 0)
        assert sum_([1, 2, 3, 4]) == 10

    def test_reduce_in_pipeline(self):
        pipeline = pipe([1, 2, 3, 4]) | reduce_(add, 0)
        assert pipeline.run() == 10

    @pytest.mark.anyio
    async def test_areduce(self):
        pipeline = apipe([1, 2, 3, 4]) | areduce(wait_and_add, 0)
        assert await pipeline.run() == 10

import pytest

from amalfi.ops import acollect, collect_
from amalfi.pipeline import apipe, pipe

from ..stub import wait_and_yield, yield_items


class TestCollect:
    def test_collect(self):
        assert collect_(yield_items)([1, 2, 3]) == [1, 2, 3]

    def test_collect_in_pipeline(self):
        pipeline = pipe([1, 2, 3]) | collect_(yield_items) | sum
        assert pipeline.run() == 6

    @pytest.mark.anyio
    async def test_acollect(self):
        assert await acollect(wait_and_yield)([1, 2, 3]) == [1, 2, 3]

    @pytest.mark.anyio
    async def test_acollect_in_pipeline(self):
        pipeline = apipe([1, 2, 3]) | acollect(wait_and_yield) | sum
        assert await pipeline.run() == 6

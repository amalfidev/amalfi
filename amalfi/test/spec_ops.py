import pytest

from amalfi.ops import amap, map_
from amalfi.pipeline import AsyncPipeline, Pipeline

from .stub import multiply_by_two, wait_and_emphasize


class TestMap:
    def test_map(self):
        mapped = map_(multiply_by_two)([1, 2, 3])
        assert list(mapped) == [2, 4, 6]

    def test_map_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3]) | map_(multiply_by_two) | sum
        assert pipeline.run() == 12

    @pytest.mark.anyio
    async def test_amap(self):
        result = await (
            AsyncPipeline.pipe(["Alice", "Bob", "Charlie"])
            | amap(wait_and_emphasize)  # ["ALICE!", "BOB!", "CHARLIE!"] (async)
            | map_(len)  # [6, 4, 8]
            | sum  # 18
        ).run()

        assert result == 18

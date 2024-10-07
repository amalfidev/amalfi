import pytest

from amalfi.ops import amap, fmap
from amalfi.pipeline import AsyncPipeline, Pipeline

from .stub import multiply_by_two, wait_and_emphasize


class TestOps:
    def test_fmap(self):
        mapped = fmap(multiply_by_two)([1, 2, 3])
        assert list(mapped) == [2, 4, 6]

    def test_fmap_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3]) | fmap(multiply_by_two) | sum
        assert pipeline.run() == 12

    @pytest.mark.anyio
    async def test_fmap_in_async_pipeline(self):
        result = await (
            AsyncPipeline.pipe(["Alice", "Bob", "Charlie"])
            | amap(wait_and_emphasize)  # ["ALICE!", "BOB!", "CHARLIE!"] (async)
            | fmap(len)  # [6, 4, 8]
            | sum  # 18
        ).run()

        assert result == 18

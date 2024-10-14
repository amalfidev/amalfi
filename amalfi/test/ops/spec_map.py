import pytest

from amalfi.ops import amap, filter_, map_
from amalfi.pipeline import apipe, pipe

from ..stub import double, wait_and_emphasize


class TestMap:
    def test_map(self):
        mapped = map_(double)([1, 2, 3])
        assert list(mapped) == [2, 4, 6]

    def test_map_in_pipeline(self):
        pipeline = pipe([1, 2, 3]) | map_(double) | sum
        assert pipeline.run() == 12

    @pytest.mark.anyio
    async def test_in_async_pipeline(self):
        pipeline = apipe([1, 2, 3]) | map_(double) | sum
        assert await pipeline.run() == 12


class TestAsyncMap:
    @pytest.mark.anyio
    async def test_async_map(self):
        result = await (
            apipe(["Alice", "Bob", "Charlie"])
            | amap(wait_and_emphasize)  # ["ALICE!", "BOB!", "CHARLIE!"] (async)
            | map_(len)  # [6, 4, 8]
            | sum  # 18
        ).run()

        assert result == 18


class TestTryAsyncMap:
    @pytest.mark.anyio
    async def test_safe_amap(self):
        result = await (
            apipe(["Alice", "Bob", "Charlie"])
            | amap(wait_and_emphasize, safe=True)
            | filter_(lambda x: not isinstance(x, BaseException))
            | list
            | len
        ).run()

        assert result == 3

    @pytest.mark.anyio
    async def test_safe_amap_with_exception(self):
        async def raise_exception(s: str) -> str:
            if len(s) <= 3:
                raise ValueError("Test exception")
            return s

        result = await (
            apipe(["Alice", "Bob", "Charlie"])
            | amap(raise_exception, safe=True)  # ["Alice", ValueError, "Charlie"]
            | filter_(lambda x: not isinstance(x, BaseException))
            | list
            | len
        ).run()

        assert result == 2

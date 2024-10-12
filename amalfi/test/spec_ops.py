import pytest

from amalfi.core import Fn, as_async
from amalfi.ops import acollect, afilter, amap, collect, filter_, map_, try_amap
from amalfi.pipeline import AsyncPipeline, Pipeline

from .stub import (
    is_even,
    multiply_by_two,
    wait_and_emphasize,
    wait_and_yield,
    yield_items,
)


# region: --map
class TestMap:
    def test_map(self):
        mapped = map_(multiply_by_two)([1, 2, 3])
        assert list(mapped) == [2, 4, 6]

    def test_map_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3]) | map_(multiply_by_two) | sum
        assert pipeline.run() == 12

    @pytest.mark.anyio
    async def test_async_map(self):
        result = await (
            AsyncPipeline.pipe(["Alice", "Bob", "Charlie"])
            | amap(wait_and_emphasize)  # ["ALICE!", "BOB!", "CHARLIE!"] (async)
            | map_(len)  # [6, 4, 8]
            | sum  # 18
        ).run()

        assert result == 18

    class TestTryAsyncMap:
        @pytest.mark.anyio
        async def test_try_async_map(self):
            result = await (
                AsyncPipeline.pipe(["Alice", "Bob", "Charlie"])
                | try_amap(wait_and_emphasize)
                | filter_(lambda x: not isinstance(x, BaseException))
                | list
                | len
            ).run()

            assert result == 3

        @pytest.mark.anyio
        async def test_try_async_map_with_exception(self):
            async def raise_exception(s: str) -> str:
                if len(s) <= 3:
                    raise ValueError("Test exception")
                return s

            result = await (
                AsyncPipeline.pipe(["Alice", "Bob", "Charlie"])
                | try_amap(raise_exception)  # ["Alice", ValueError, "Charlie"]
                | filter_(lambda x: not isinstance(x, BaseException))
                | list
                | len
            ).run()

            assert result == 2


# endregion: --map


# region: --filter
class TestFilter:
    def test_filter_with_lambda(self):
        is_even: Fn[int, bool] = lambda x: x % 2 == 0  # noqa: E731
        filter_odds = filter_(is_even)
        assert list(filter_odds([1, 2, 3, 4])) == [2, 4]

    def test_filter_with_function(self):
        filter_odds = filter_(is_even)
        assert list(filter_odds([1, 2, 3, 4])) == [2, 4]

    def test_filter_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3, 4]) | filter_(is_even) | tuple | len
        assert pipeline.run() == 2

    @pytest.mark.anyio
    async def test_filter_async_pipeline(self):
        pipeline = AsyncPipeline.pipe([1, 2, 3, 4]).step(filter_(is_even)).step(tuple)
        assert await pipeline.run() == (2, 4)

    class TestAsyncFilter:
        @pytest.mark.anyio
        async def test_async_filter(self):
            is_even_async = as_async(is_even)
            filter_odds = afilter(is_even_async)
            assert list(await filter_odds([1, 2, 3, 4])) == [2, 4]

        @pytest.mark.anyio
        async def test_async_filter_in_pipeline(self):
            is_even_async = as_async(is_even)
            result = await (
                AsyncPipeline.pipe([1, 2, 3, 4])
                | afilter(is_even_async)  # [2, 4]
                | list
            ).run()

            assert result == [2, 4]

        def test_filter_with_lambda(self):
            is_even: Fn[int, bool] = lambda x: x % 2 == 0  # noqa: E731
            result = Pipeline.pipe([1, 2, 3, 4]).step(filter_(is_even)).step(list).run()

            assert result == [2, 4]


# endregion: --filter


# region: --collect
class TestCollect:
    def test_collect(self):
        assert collect(yield_items)([1, 2, 3]) == [1, 2, 3]

    def test_collect_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3]) | collect(yield_items) | sum
        assert pipeline.run() == 6

    @pytest.mark.anyio
    async def test_acollect(self):
        assert await acollect(wait_and_yield)([1, 2, 3]) == [1, 2, 3]

    @pytest.mark.anyio
    async def test_acollect_in_pipeline(self):
        pipeline = AsyncPipeline.pipe([1, 2, 3]) | acollect(wait_and_yield) | sum
        assert await pipeline.run() == 6


# endregion: --collect

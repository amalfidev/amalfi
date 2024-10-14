import pytest

from amalfi import Fn, as_async
from amalfi.ops import acollect, afilter, collect_, filter_
from amalfi.pipeline import apipe, pipe

from ..stub import is_even, wait_and_yield, yield_items


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
        pipeline = pipe([1, 2, 3, 4]) | filter_(is_even) | tuple | len
        assert pipeline.run() == 2

    @pytest.mark.anyio
    async def test_filter_async_pipeline(self):
        pipeline = apipe([1, 2, 3, 4]) | filter_(is_even) | tuple | len
        assert await pipeline.run() == 2

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
                apipe([1, 2, 3, 4])
                | afilter(is_even_async)  # [2, 4]
                | list
            ).run()

            assert result == [2, 4]

        def test_filter_with_lambda(self):
            is_even: Fn[int, bool] = lambda x: x % 2 == 0  # noqa: E731
            result = pipe([1, 2, 3, 4]).step(filter_(is_even)).step(list).run()

            assert result == [2, 4]


# endregion: --filter


# region: --collect
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


# endregion: --collect

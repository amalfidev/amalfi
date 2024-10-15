import pytest

from amalfi import Fn, as_async
from amalfi.ops import afilter, filter_
from amalfi.pipeline import apipe, pipe

from ..stub import is_even


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

    def test_filter_none(self):
        filter_odds = filter_(None)
        assert list(filter_odds([1, None, 3])) == [1, 3]

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

        @pytest.mark.anyio
        async def test_filter_with_lambda(self):
            is_even_async = as_async(is_even)
            result = apipe([1, 2, 3, 4]).step(afilter(is_even_async)).step(list)

            assert await result.run() == [2, 4]

        @pytest.mark.anyio
        async def test_filter_none(self):
            result = await apipe([1, None, 3]).step(filter_(None)).step(list).run()
            assert result == [1, 3]

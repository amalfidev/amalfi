from typing import Iterable

import pytest

from amalfi.core import Fn
from amalfi.ops import async_map, filter_, map_
from amalfi.pipeline import AsyncPipeline, Pipeline

from .stub import is_even, multiply_by_two, wait_and_emphasize


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
            | async_map(wait_and_emphasize)  # ["ALICE!", "BOB!", "CHARLIE!"] (async)
            | map_(len)  # [6, 4, 8]
            | sum  # 18
        ).run()

        assert result == 18


class TestFilter:
    def test_filter_with_lambda(self):
        filter_odds: Fn[Iterable[int], Iterable[int]] = filter_(lambda x: x % 2 == 0)
        assert list(filter_odds([1, 2, 3, 4])) == [2, 4]

    def test_filter_with_function(self):
        filter_odds = filter_(is_even)
        assert list(filter_odds([1, 2, 3, 4])) == [2, 4]

    def test_filter_in_pipeline(self):
        pipeline = Pipeline.pipe([1, 2, 3, 4]) | filter_(is_even) | tuple | len
        assert pipeline.run() == 2

    @pytest.mark.anyio
    async def test_async_filter(self):
        pipeline = AsyncPipeline.pipe([1, 2, 3, 4]) | filter_(is_even) | tuple | len
        assert await pipeline.run() == 2

import pytest

from amalfi.ops.filter import filter_
from amalfi.ops.starmap import astarmap, starmap
from amalfi.pipeline import apipe, pipe

from ..stub import multiply, wait_and_multiply


@pytest.fixture
def pairs_input() -> list[tuple[int, int]]:
    return [(1, 2), (3, 4), (5, 6)]


class TestStarmap:
    def test_starmap(self, pairs_input: list[tuple[int, int]]):
        star_multiplier = starmap(multiply)
        mapped = star_multiplier(pairs_input)
        assert list(mapped) == [2, 12, 30]

    def test_starmap_in_pipeline(self, pairs_input: list[tuple[int, int]]):
        pipeline = pipe(pairs_input) | starmap(multiply) | sum
        assert pipeline.run() == 44

    @pytest.mark.anyio
    async def test_in_async_pipeline(self, pairs_input: list[tuple[int, int]]):
        pipeline = apipe(pairs_input) | starmap(multiply) | sum
        assert await pipeline.run() == 44


class TestAsyncStarmap:
    @pytest.mark.anyio
    async def test_async_starmap(self, pairs_input: list[tuple[int, int]]):
        pipeline = apipe(pairs_input) | astarmap(wait_and_multiply) | sum
        assert await pipeline.run() == 44

    @pytest.mark.anyio
    async def test_safe_async_starmap(self, pairs_input: list[tuple[int, int]]):
        async def raise_exception(x: int, y: int) -> int:
            if x == 3:
                raise ValueError("Test exception")
            return x * y

        pipeline = (
            apipe(pairs_input)
            | astarmap(raise_exception, safe=True)
            | filter_(lambda x: not isinstance(x, BaseException))
            | list
            | sum
        )

        assert await pipeline.run() == 32

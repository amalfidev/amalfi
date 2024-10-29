import asyncio

import pytest

from amalfi.ops import atap, tap
from amalfi.pipeline import apipe, pipe

from ..stub import add_one


class TestTap:
    def test_tap(self):
        numbers: list[int] = []

        def side_effect(y: int):
            print(y)
            numbers.append(y)

        assert pipe(1).then(tap(side_effect)).then(add_one).run() == 2
        assert numbers == [1]

    @pytest.mark.anyio
    async def test_atap(self):
        numbers: list[int] = []

        async def side_effect(y: int):
            await asyncio.sleep(0.0001)
            print(y)
            numbers.append(y)

        pipeline = apipe(1).then(atap(side_effect)).then(add_one)
        assert await pipeline.run() == 2
        assert numbers == [1]

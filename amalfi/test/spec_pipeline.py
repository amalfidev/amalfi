import asyncio

import pytest

from amalfi.pipeline import AsyncPipeline, Pipeline


def add_one(x: int) -> int:
    return x + 1


def multiply_by_two(x: int) -> int:
    return x * 2


def uppercase(s: str) -> str:
    return s.upper()


def greet(name: str) -> str:
    return f"Hello, {name}"


async def emphasize(s: str) -> str:
    await asyncio.sleep(0.1)
    return s.upper() + "!"


class TestPipeline:
    def test_pipe(self):
        result = (
            Pipeline.pipe(1)
            .chain(add_one)  # 2
            .chain(multiply_by_two)  # 4
            .chain(add_one)  # 5
            .chain(str)  # "5"
            | uppercase  # "5"
            | len  # 1
            | add_one  # 2
            | str  # "2"
        )()

        assert result == "2"

    def test_change_input(self):
        pipeline = Pipeline.pipe(1) | add_one | multiply_by_two
        pipeline.input = 2
        assert pipeline.input == 2
        assert pipeline() == 6

        assert pipeline.with_input(3)() == 8


class TestAsyncPipeline:
    @pytest.mark.anyio
    async def test_pipe(self):
        pipeline = (
            AsyncPipeline.pipe("Alice")
            .chain(greet)  # "Hello, Alice"
            .chain(emphasize)  # "HELLO, ALICE!" (0.1s) async
            .chain(len)  # 13
            | add_one  # 14
            | str  # "14"
            | emphasize  # "14!" (0.1s) async
            | len  # 3
        )
        assert pipeline.input == "Alice"
        assert await pipeline() == 3

        result = await (
            AsyncPipeline.pipe("Alice")
            .chain(greet)
            .chain(emphasize)  # async
            .chain(len)
            | add_one
            | str
            | emphasize  # async
            | len
        )()
        assert result == 3

        result = await (
            Pipeline.pipe_async("Alice")
            | greet
            | emphasize  # async
            | len
            | add_one
            | str
            | emphasize  # async
            | len
        )()
        assert result == 3

    @pytest.mark.anyio
    async def test_change_input(self):
        pipeline = AsyncPipeline.pipe("Alice") | greet | emphasize
        pipeline.input = "Bob"

        assert pipeline.input == "Bob"
        assert await pipeline() == "HELLO, BOB!"
        assert await pipeline.with_input("Charlie")() == "HELLO, CHARLIE!"

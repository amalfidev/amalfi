import pytest

from amalfi.pipeline import AsyncPipeline, Pipeline

from .stub import (
    add_one,
    greet,
    multiply_by_two,
    uppercase,
    wait_and_add_one,
    wait_and_emphasize,
)


class TestPipeline:
    def test_pipe(self):
        result = (
            Pipeline.pipe(1)
            .step(add_one)  # 2
            .step(multiply_by_two)  # 4
            .step(lambda x: x + 1)  # 5
            .step(str)  # "5"
            | uppercase  # "5"
            | len  # 1
            | add_one  # 2
            | str  # "2"
        ).run()

        assert result == "2"

    def test_change_input(self):
        pipeline = Pipeline.pipe(1) | add_one | multiply_by_two
        pipeline.input = 2
        assert pipeline.input == 2
        assert pipeline() == 6

        assert pipeline.with_input(3)() == 8

    def test_concat(self):
        pipeline1 = Pipeline.pipe(1) | add_one
        pipeline2 = Pipeline.pipe(0) | multiply_by_two
        pipeline = pipeline1 + pipeline2
        assert pipeline() == 4


class TestAsyncPipeline:
    @pytest.mark.anyio
    async def test_pipe(self):
        pipeline = (
            AsyncPipeline.pipe("Alice")
            .step(greet)  # "Hello, Alice"
            .step(wait_and_emphasize)  # "HELLO, ALICE!" (0.1s) async
            .step(len)  # 13
            | add_one  # 14
            | str  # "14"
            | wait_and_emphasize  # "14!" (0.1s) async
            | len  # 3
        )
        assert pipeline.input == "Alice"
        assert await pipeline() == 3

        result = await (
            AsyncPipeline.pipe("Alice")
            .step(greet)
            .step(wait_and_emphasize)  # async
            .step(len)
            | add_one
            | str
            | wait_and_emphasize  # async
            | len
        ).run()
        assert result == 3

        result = await (
            Pipeline.pipe_async("Alice")
            | greet
            | wait_and_emphasize  # async
            | len
            | add_one
            | str
            | wait_and_emphasize  # async
            | len
        ).run()
        assert result == 3

    @pytest.mark.anyio
    async def test_concat(self):
        pipeline1 = AsyncPipeline.pipe(1) | wait_and_add_one
        pipeline2 = AsyncPipeline.pipe(2) | multiply_by_two | wait_and_add_one
        pipeline = pipeline1 + pipeline2
        assert await pipeline() == 5

    @pytest.mark.anyio
    async def test_change_input(self):
        pipeline = AsyncPipeline.pipe("Alice") | greet | wait_and_emphasize
        pipeline.input = "Bob"

        assert pipeline.input == "Bob"
        assert await pipeline() == "HELLO, BOB!"
        assert await pipeline.with_input("Charlie").run() == "HELLO, CHARLIE!"

    @pytest.mark.anyio
    async def test_from_sync(self):
        pipeline = Pipeline.pipe(1) | add_one
        async_pipeline = AsyncPipeline.from_sync(pipeline)
        assert await async_pipeline() == 2

        concat = AsyncPipeline.from_sync(pipeline).with_input(5) + async_pipeline
        assert await concat() == 7

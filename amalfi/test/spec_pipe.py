import pytest

from amalfi.pipeline import AsyncPipeline, Pipeline, apipe, pipe

from .stub import (
    add_one,
    double,
    greet,
    uppercase,
    wait_and_add_one,
    wait_and_emphasize,
)


class TestPipeline:
    def test_pipe(self):
        result = Pipeline(1).run()
        assert result == 1

    def test_composed_pipe(self):
        result = (
            pipe(1)
            .then(add_one)  # 2
            .then(double)  # 4
            .then(lambda x: x + 1)  # 5
            .then(str)  # "5"
            | uppercase  # "5"
            | len  # 1
            | add_one  # 2
            | str  # "2"
        ).run()

        assert result == "2"

    def test_with_input(self):
        pipeline = pipe(1) | add_one | double
        pipeline = pipeline.with_input(2)
        assert pipeline.input == 2
        assert pipeline() == 6

        assert pipeline.with_input(3).run() == 8

    def test_concat(self):
        pipeline1 = pipe(1) | add_one
        pipeline2 = pipe(0) | double
        pipeline = pipeline1 > pipeline2
        assert pipeline() == 4

    @pytest.mark.anyio
    async def test_to_async(self):
        pipeline = pipe(1) | add_one
        apipeline = pipeline.to_async() | wait_and_add_one
        assert await apipeline() == 3

        concat = pipeline.to_async().with_input(5) > apipeline
        assert await concat() == 8


class TestAsyncPipeline:
    @pytest.mark.anyio
    async def test_pipe(self):
        pipeline = (
            AsyncPipeline("Alice")
            .then(greet)  # "Hello, Alice"
            .then(wait_and_emphasize)  # "HELLO, ALICE!" (0.1s) async
            .then(len)  # 13
            | add_one  # 14
            | str  # "14"
            | wait_and_emphasize  # "14!" (0.1s) async
            | len  # 3
        )
        assert pipeline.input == "Alice"
        assert await pipeline() == 3

        result = await (
            apipe("Alice")
            .then(greet)
            .then(wait_and_emphasize)  # async
            .then(len)
            | add_one
            | str
            | wait_and_emphasize  # async
            | len
        ).run()
        assert result == 3

        result = await (
            apipe("Alice")
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
        pipeline1 = apipe(1) | wait_and_add_one
        pipeline2 = apipe(2) | double | wait_and_add_one
        pipeline = pipeline1 > pipeline2
        assert await pipeline() == 5

    @pytest.mark.anyio
    async def test_with_input(self):
        pipeline = apipe("Alice") | greet | wait_and_emphasize
        pipeline = pipeline.with_input("Bob")

        assert pipeline.input == "Bob"
        assert await pipeline() == "HELLO, BOB!"
        assert await pipeline.with_input("Charlie").run() == "HELLO, CHARLIE!"

import inspect

import pytest

from amalfi.core import AsyncFn, Fn, as_async, identity


def test_identity():
    assert identity(42) == 42


class TestAsAsync:
    @pytest.mark.anyio
    async def test_as_async(self):
        def add_one(x: int) -> int:
            return x + 1

        add_one_async = as_async(add_one)
        result = add_one_async(1)

        assert inspect.iscoroutinefunction(add_one_async)
        assert inspect.iscoroutine(result)
        assert await result == 2

    @pytest.mark.anyio
    async def test_as_async_lambda(self):
        add_one_async: AsyncFn[int, int] = as_async(lambda x: x + 1)
        result = add_one_async(1)

        assert inspect.iscoroutinefunction(add_one_async)
        assert inspect.iscoroutine(result)
        assert await result == 2

    @pytest.mark.anyio
    async def test_as_async_lambda_variable(self):
        add_one: Fn[int, int] = lambda x: x + 1  # noqa: E731
        add_one_async = as_async(add_one)

        result = add_one_async(1)

        assert inspect.iscoroutinefunction(add_one_async)
        assert inspect.iscoroutine(result)
        assert await result == 2

    @pytest.mark.anyio
    async def test_as_async_decorator(self):
        @as_async
        def add_one(x: int) -> int:
            return x + 1

        result = add_one(1)

        assert inspect.iscoroutinefunction(add_one)
        assert inspect.iscoroutine(result)
        assert await result == 2

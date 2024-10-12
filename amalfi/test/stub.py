import asyncio
from typing import AsyncIterator, Generator, Iterable


def add_one(x: int) -> int:
    return x + 1


def multiply_by_two(x: int) -> int:
    return x * 2


def is_even(x: int) -> bool:
    return x % 2 == 0


async def wait_and_add_one(x: int) -> int:
    await asyncio.sleep(0.1)
    return x + 1


def uppercase(s: str) -> str:
    return s.upper()


def greet(name: str) -> str:
    return f"Hello, {name}"


async def wait_and_emphasize(s: str) -> str:
    await asyncio.sleep(0.1)
    return s.upper() + "!"


def yield_items[T](iterable: Iterable[T]) -> Generator[T, None, None]:
    for item in iterable:
        yield item


async def wait_and_yield[T](iterable: Iterable[T]) -> AsyncIterator[T]:
    for item in iterable:
        await asyncio.sleep(0.1)
        yield item


def yield_range(start: int, end: int) -> Generator[int, None, None]:
    for i in range(start, end):
        yield i

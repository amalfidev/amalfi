import asyncio
from typing import AsyncIterator, Generator, Iterable


def add_one(x: int) -> int:
    return x + 1


def double(x: int) -> int:
    return x * 2


def multiply(x: int, y: int) -> int:
    return x * y


async def wait_and_multiply(x: int, y: int) -> int:
    await asyncio.sleep(0.001)
    return x * y


def is_even(x: int) -> bool:
    return x % 2 == 0


async def wait_and_add_one(x: int) -> int:
    await asyncio.sleep(0.001)
    return x + 1


async def wait_and_double(x: int) -> int:
    await asyncio.sleep(0.001)
    return x * 2


def uppercase(s: str) -> str:
    return s.upper()


def greet(name: str) -> str:
    return f"Hello, {name}"


async def wait_and_emphasize(s: str) -> str:
    await asyncio.sleep(0.001)
    return s.upper() + "!"


def yield_items[T](iterable: Iterable[T]) -> Generator[T, None, None]:
    for item in iterable:
        yield item


async def wait_and_yield[T](iterable: Iterable[T]) -> AsyncIterator[T]:
    for item in iterable:
        await asyncio.sleep(0.001)
        yield item


def yield_range(start: int, end: int) -> Generator[int, None, None]:
    for i in range(start, end):
        yield i


async def ayield_range(start: int, end: int) -> AsyncIterator[int]:
    for i in range(start, end):
        await asyncio.sleep(0.001)
        yield i

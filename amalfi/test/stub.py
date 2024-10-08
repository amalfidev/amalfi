import asyncio


def add_one(x: int) -> int:
    return x + 1


def multiply_by_two(x: int) -> int:
    return x * 2


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

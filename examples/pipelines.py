import asyncio

from amalfi.pipeline import apipe, pipe


def add_one(x: int) -> int:
    return x + 1


def multiply_by_two(x: int) -> int:
    return x * 2


def greet(name: str) -> str:
    return f"Hello, {name}"


async def emphasize(s: str) -> str:
    await asyncio.sleep(0.001)
    return s.upper() + "!"


def main():
    pipeline = pipe(1) | add_one | multiply_by_two
    print(pipeline())

    apipeline = apipe("Alice") | greet | emphasize

    result = asyncio.run(apipeline())
    print(result)


if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Callable

type Input[I] = I  # | Awaitable[I]
type Output[O] = O  # | Awaitable[O]


def identity[I](value: I) -> I:
    return value


class Pipeline[I, O]:
    """
    A generic pipeline class for chaining callables using the `|` operator.

    This class allows the creation of pipelines where each step is a callable
    function. The steps are composed together, enabling a fluent interface
    for processing data through a series of transformations.

    **Type Parameters:**
    - `I`: The input type of the pipeline.
    - `O`: The output type after processing through the pipeline.

    **Attributes:**
    - `fn`: A callable representing the chained functions of the pipeline.

    **Examples:**

    Basic usage with integer transformations:

    ```python
    from amalfi import pipeline

    def add_one(x: int) -> int:
        return x + 1

    def multiply_by_two(x: int) -> int:
        return x * 2

    # Create a pipeline that adds one and then multiplies by two
    my_pipeline = pipeline() | add_one | multiply_by_two

    result = my_pipeline(3)  # (3 + 1) * 2 = 8
    print(result)  # Output: 8
    ```

    Chaining multiple functions with different return types:

    ```python
    from amalfi_core.pipeline import pipeline

    def square(x: int) -> int:
        return x * x

    def to_string(x: int) -> str:
        return f"Result is {x}"

    def shout(s: str) -> str:
        return s.upper() + "!"

    # Create a pipeline that squares a number, converts to string, and shouts it
    my_pipeline = pipeline() | square | to_string | shout

    result = my_pipeline(5)  # Square 5, convert, and shout
    print(result)  # Output: "RESULT IS 25!"
    ```

    Using built-in functions within the pipeline:

    ```python
    from amalfi_core.pipeline import pipeline

    # Create a pipeline that converts to string and gets the length
    my_pipeline = pipeline() | str | len

    result = my_pipeline(12345)
    print(result)  # Output: 5
    ```

    """

    def __init__(self, fn: Callable[[I], O]):
        """
        Initialize the `Pipeline` with a function.

        **Args:**
        - `fn`: A callable that takes an input of type `I` and returns
        an output of type `O`.
        """
        self.fn = fn

    def __call__(self, input: I) -> Output[O]:
        """
        Execute the pipeline on the given input.

        **Args:**
        - `input`: The input data to be processed by the pipeline.

        **Returns:**
        - The result of processing the input through the pipeline functions.
        """
        return self.fn(input)

    def __or__[U](self, fn: Callable[[O], U] = identity) -> Pipeline[I, U]:
        """
        Chain another function to the pipeline using the `|` operator.

        This method creates a new `Pipeline` instance that composes the current pipeline
        function with the provided function `fn`.

        **Args:**
        - `fn`: A callable that takes an input of type `O` and returns
        an output of type `U`. Defaults to the identity function.

        **Returns:**
        - A new `Pipeline` instance that represents the composition of the
        current pipeline and the provided function.
        """

        def composed_fn(value: I) -> U:
            return fn(self.fn(value))

        return Pipeline(composed_fn)


def pipeline[I]() -> Pipeline[I, I]:
    return Pipeline[I, I](identity)

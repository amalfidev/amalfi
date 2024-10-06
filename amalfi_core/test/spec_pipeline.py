from amalfi_core.pipeline import pipeline


def add_one(x: int) -> int:
    return x + 1


def multiply_by_two(x: int) -> int:
    return x * 2


def uppercase(s: str) -> str:
    return s.upper()


class TestPipeline:
    def test_pipeline(self):
        result = (
            pipeline()
            | add_one  # 2
            | multiply_by_two  # 4
            | add_one  # 5
            | str  # "5"
            | uppercase  # "5"
            | len  # 1
            | add_one  # 2
            | str  # "2"
        )(1)

        assert result == "2"

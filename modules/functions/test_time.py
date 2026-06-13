from ..endpoints.config import PROBLEM_TYPE_TO_TIME


def get_time_of_test(problems_types: list[int]) -> int:
    return sum([PROBLEM_TYPE_TO_TIME.get(problem_type) for problem_type in problems_types])
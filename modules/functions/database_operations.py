from collections import defaultdict
from itertools import count
from random import choice, randint
from pprint import pprint
from typing import Type
from sqlalchemy import Integer, Column
from sqlalchemy.orm import Query
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..databases.UsersStatisticsDB import UsersStatisticsDB
from ..endpoints.config import CORRECT_ANSWERS_VALUE_TO_POINTS
from ..endpoints.config import INFORMATICS_DB_NAME, USERS_STATISTICS_DB_NAME


def get_mark_for_test(points_value: int, questions_value: int) -> str:
    result: int = CORRECT_ANSWERS_VALUE_TO_POINTS.get(points_value)
    marks: dict[bool | str, str] = {
        0 <= points_value < 40: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 2",
        40 <= points_value < 46: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 3&Только для аттестата.",
        46 <= points_value < 56: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 3&Можно пробовать поступить в ВУЗ.",
        56 <= points_value < 21: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 4",
        points_value >= 21: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 5",
        "without mark": f"Общий балл: {points_value}&Оценка не предусмотрена (разных типов заданий меньше 10)"
    }
    if questions_value < 10:
        return marks["without mark"]
    return marks[True]


def connect_database_informatics() -> InformaticsDB:
    return InformaticsDB(db_name=INFORMATICS_DB_NAME)


def save_test_question(question_data: dict[str, str | int]) -> bool:
    # print(question_data)
    if question_data.get("q_text") and question_data.get("q_right_answer"):
        database: InformaticsDB = connect_database_informatics()
        database.add_question(question_data=question_data)
        return True
    return False


def check_test_variant(variant: list[int], answers: dict[str, list[str]]) -> tuple[dict[str, int], str, dict[str, list[int]]]:
    answers_and_marks: dict[str, int] = {}
    for_statistics: dict[str, list[int]] = {f"q_type_{num}": [0, 0] for num in range(1, 28)}
    db_informatics: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    different_problem_types_value: set[Column[Integer] | int] = set()
    q_count: count = count(start=1)
    for q_id in variant:
        question: Informatics = db_informatics.get(q_id)
        q_type_number: Column[Integer] = question.q_number
        different_problem_types_value.add(q_type_number)
        q_number_count: str = f"{next(q_count)}"
        if q_type_number < 26:
            points: int = check_one_point_problem(
                correct_answer=question.q_right_answer.split("&"),
                answer=answers.get(q_number_count)
            )
            common_value, right_value = for_statistics.get(f"q_type_{q_type_number}")
            for_statistics[f"q_type_{q_type_number}"] = [common_value + 1, right_value + points]
        else:
            points: int = check_two_points_problem(
                q_number=q_type_number,
                correct_answer=question.q_right_answer.split("&"),
                answer=answers.get(q_number_count)
            )
            common_value, right_value = for_statistics.get(f"q_type_{q_type_number}")
            for_statistics[f"q_type_{q_type_number}"] = [common_value + 1, right_value + (points / 2)]
        answers_and_marks.update({q_number_count: points})

    points_value: int = sum(answers_and_marks.values())

    return (
        answers_and_marks,
        get_mark_for_test(points_value=points_value, questions_value=len(different_problem_types_value)),
        for_statistics
    )


def check_one_point_problem(correct_answer: list[str], answer: list[str]) -> int:
    return 1 if correct_answer == answer else 0


def check_two_points_problem(q_number: Column[Integer] | int, correct_answer: list[str], answer: list[str]) -> int:
    if q_number == 26:
        points_value: dict[bool, int] = {
            correct_answer == answer: 2,
            (correct_answer[0], correct_answer[1]) == (correct_answer[1], correct_answer[0]): 1,
            sum((answer[0] in correct_answer, answer[1] in correct_answer)) == 1: 1
    }
        return points_value.get(True, 0)

    points_value: dict[bool, int] = {
        correct_answer == answer: 2,
        (correct_answer[:2], correct_answer[2:]) == (answer[2:], answer[:2]): 1,
        sum(("".join(answer[:2]) in "".join(correct_answer), "".join(answer[2:]) in "".join(correct_answer))) == 1: 1
    }
    return points_value.get(True, 0)


def get_test_var_one(data_for_test: dict[str, str]) -> dict[Column[Integer] | int, type[Informatics]]:
    database: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    questions: dict[int, type[Informatics]] = {}
    q_count: count = count(start=1)
    q_types: dict[str, str] = {
        f"{num}": data_for_test.get(f"{num}") for num in range(1, 28)
    }
    for q_type_number in q_types:
        difficulties: set[str] = {
            data_for_test.get(f"check_{diff}_{q_type_number}")
            for diff in ["base", "middle", "hard"]
            if data_for_test.get(f"check_{diff}_{q_type_number}")
        }
        # print(difficulties)
        q_list: list[type[Informatics]] = []
        for difficulty in difficulties:
            q_list.extend(database.filter(
                Informatics.q_number == int(q_type_number),
                Informatics.q_difficulty == difficulty
            ).all())
        # print(q_list)
        for _ in range(int(q_types[q_type_number])):
            index: int = randint(0, len(q_list) - 1)
            questions[next(q_count)] = q_list.pop(index)
    # pprint(questions)
    return questions


def get_test_var_two(data_for_test: dict[str, str]) -> dict[Column[Integer] | int, type[Informatics]]:
    database: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    questions: dict[int, list[type[Informatics]]] = {num: [] for num in range(1, int(data_for_test.get("test_range")) + 1)}
    for question_number in questions:
        questions[question_number].extend(
            database.filter(
                Informatics.q_number == int(question_number),
                Informatics.q_difficulty == "Базовый"
            )
        )
    return {
        num: choice(questions.get(num)) for num in questions if questions.get(num)
    }


def get_test_var_three(data_for_test: dict[str, str]) -> dict[Column[Integer] | int, type[Informatics]]:
    database: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    questions: dict[int, list[type[Informatics]]] = {num: [] for num in range(1, 28)}
    difficulties: set[str] = {data_for_test[difficulty] for difficulty in data_for_test if data_for_test[difficulty]}
    for question_number in questions:
        q_list: list[type[Informatics]] = []
        for difficulty in difficulties:
            q_list.extend(database.filter(
                Informatics.q_number == question_number,
                Informatics.q_difficulty == difficulty
            ))
        questions[question_number].extend(q_list)
    return {
        num: choice(questions.get(num)) for num in questions if questions.get(num)
    }


def get_test_var_exam() -> dict[Column[Integer], Type[Informatics]]:
    database: InformaticsDB = connect_database_informatics()
    questions: defaultdict[Column[Integer], list[Type[Informatics]]] = defaultdict(list)
    for question in database.session.query(Informatics).all():
        questions[question.q_number].append(question)

    return {
        num: choice(questions.get(num)) for num in questions
    }


def update_statistics_to_student(user_id: int, statistics: dict[str, list[int]]) -> None:
    UsersStatisticsDB(db_name=USERS_STATISTICS_DB_NAME).change_statistics(id=user_id, data_to_change=statistics)


def get_q_types_values() -> dict[str, dict[str, int]]:
    q_types_values: dict[str, defaultdict[str, int]] = {f"Тип {num}": defaultdict(int) for num in range(1, 28)}
    database: list[type[Informatics]] = connect_database_informatics().session.query(Informatics).all()
    for question in database:
        q_types_values[f"Тип {question.q_number}"]["value"] += 1
        q_types_values[f"Тип {question.q_number}"][f"{question.q_difficulty}"] += 1

    return q_types_values


if __name__ == '__main__':
    print(get_test_var_one(data_for_test={"q_right_answer": "2", "q_number": 1}))
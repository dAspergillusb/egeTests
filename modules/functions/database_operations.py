from collections import defaultdict
from itertools import count
from random import choice, randint
from pprint import pprint
from typing import Type
from fastapi import Request
from sqlalchemy import Integer, Column
from sqlalchemy.orm import Query, Session
from urllib3 import request

from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..databases.DailyStatisticsDB import DailyStatistics, DailyStatisticsDB
from ..databases.UsersStatisticsDB import UsersStatisticsDB, UsersStatistics
from ..databases.ActiveStudentsTest import ActiveStudentsTest, ActiveStudentsTestDB
from ..endpoints.config import CORRECT_ANSWERS_VALUE_TO_POINTS
from ..endpoints.config import INFORMATICS_DB_NAME, USERS_STATISTICS_DB_NAME, DAILY_STATISTICS_DB_NAME


def get_mark_for_test(points_value: int, questions_value: int) -> str:
    result: int = CORRECT_ANSWERS_VALUE_TO_POINTS.get(points_value)
    marks: dict[bool | str, str] = {
        0 <= result < 40: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 2",
        40 <= result < 46: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 3&Только для аттестата.",
        46 <= result < 56: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 3&Можно пробовать поступить в ВУЗ.",
        56 <= result < 80: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 4",
        result >= 80: f"Первичный балл: {points_value}&Тестовый балл: {result}&Оценка: 5",
        "without mark": f"Общий балл: {points_value}&Оценка не предусмотрена (разных типов заданий меньше 10)"
    }
    # print(marks)
    if questions_value < 10:
        return marks["without mark"]
    return marks[True]


def connect_database_informatics() -> InformaticsDB:
    return InformaticsDB(db_name=INFORMATICS_DB_NAME)

def connect_daily_statistics() -> DailyStatisticsDB:
    return DailyStatisticsDB(db_name=DAILY_STATISTICS_DB_NAME)

def connect_active_test_session() -> ActiveStudentsTestDB:
    return ActiveStudentsTestDB()

def save_test_question(question_data: dict[str, str | int] | dict[int, dict[str, int | str]]) -> bool:
    # print(question_data)
    duplicate: bool = any((
        connect_database_informatics().session.query(Informatics).filter(Informatics.q_text == question_data.get("q_text")).first(),
        connect_database_informatics().session.query(Informatics).filter(
            Informatics.q_text == question_data.get(19, {'q_text': ''}).get('q_text')
        ).first(),
    ))
    if duplicate:
        return False
    if question_data.get("q_text") and question_data.get("q_right_answer"):
        database: InformaticsDB = connect_database_informatics()
        database.add_question(question_data=question_data)
        return True
    elif (
            question_data.get(19) and
            question_data.get(20) and
            question_data.get(21) and
            all((
            question_data.get(19).get("q_text"),
            question_data.get(20).get("q_text"),
            question_data.get(21).get("q_text"),
            question_data.get(19).get("q_right_answer"),
            question_data.get(20).get("q_right_answer"),
            question_data.get(21).get("q_right_answer")))
    ):
        database: InformaticsDB = connect_database_informatics()
        database.add_question(question_data=question_data.get(20))
        database.add_question(question_data=question_data.get(21))
        for_link: list[type[Informatics]] = [q for q in connect_database_informatics().session.query(Informatics).all() if q.q_number in [20, 21]]
        question_data.get(19).update({
            "q_linked_with": "&".join([
                f"{for_link[-2].id}",
                f"{for_link[-1].id}"
            ])
        })
        database.add_question(
            question_data=question_data.get(19))
        return True
    return False


def check_test_variant(variant: list[int], answers: dict[str, list[str]]) -> tuple[dict[str, int], str, dict[str, list[int]]]:
    answers_and_marks: dict[str, int] = {}
    for_statistics: dict[str, list[int]] = {f"q_type_{num}": [0, 0] for num in range(1, 30 + 1)}
    db_informatics: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    different_problem_types_value: set[Column[Integer] | int] = set()
    checked_test: list[int] = []
    q_count: count = count(start=1)
    for q_id in variant:
        checked_test.append(q_id)
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

    # It's need for remove questions that don't be in test
    for_statistics = {q_type: stat for q_type, stat in for_statistics.items() if stat[0]}   #!TODO
    points_value: int = sum(answers_and_marks.values())
    print(points_value)
    # print(for_statistics)
    return (
        answers_and_marks,
        get_mark_for_test(points_value=points_value, questions_value=len(different_problem_types_value)),
        for_statistics
    )

def save_daily_statistics(*, user_id: int, name: str, checked_test: list[int], answers_and_marks: dict[str, int]) -> None:
    firstname, lastname = name.split()
    daily_statistics: DailyStatisticsDB = connect_daily_statistics()
    # print(user_id, checked_test, answers_and_marks, sep='\n')
    new_daily_statistics: dict[str, str | int] = {
        "user_id": user_id,
        "firstname": firstname,
        "lastname": lastname,
        "test": "&".join([f"{q_id}" for q_id in checked_test]),
        "result": "&".join(f"{answer}" for answer in answers_and_marks.values())
    }
    daily_statistics.add_statistics(statistics_data=new_daily_statistics)

def get_daily_statistics(user_id: int) -> dict[str, defaultdict[str, list[type[Informatics]]]]:
    student_all_daily_statistics: list[type[DailyStatistics]] = connect_daily_statistics().session.query(DailyStatistics).filter(DailyStatistics.user_id == user_id).all()
    student_daily_statistics: dict[str, defaultdict[str, list[type[Informatics]]]] = {}

    informatics_db: Session = connect_database_informatics().session
    for daily_stat in student_all_daily_statistics:
        year_month_day, hours_minutes = daily_stat.date.split("&")
        variant: list[type[Informatics]] = [informatics_db.get(Informatics, q_id) for q_id in map(int, daily_stat.test.split("&"))]
        if not student_daily_statistics.get(year_month_day):
            student_daily_statistics[year_month_day] = defaultdict(list)
        student_daily_statistics[year_month_day][hours_minutes].extend(variant)
    pprint(student_daily_statistics)
    return student_daily_statistics

def get_old_test(date: str) -> tuple[dict[int, type[DailyStatistics]], dict[int, int]]:
    old_test_daily_statistics: type[DailyStatistics] = connect_daily_statistics().session.query(DailyStatistics).filter(DailyStatistics.date == date).first()
    database_informatics: Session = connect_database_informatics().session
    old_test: dict[int, type[Informatics]] = {
        num: database_informatics.get(Informatics, problem) for num, problem in
        enumerate(map(int, old_test_daily_statistics.test.split("&")), start=1)
    }
    old_results: dict[int, int] = {
        num: result for num, result in enumerate(map(int, old_test_daily_statistics.result.split("&")), start=1)
    }
    return old_test, old_results

def check_one_point_problem(correct_answer: list[str], answer: list[str]) -> int:
    return 1 if correct_answer == answer else 0


def check_two_points_problem(q_number: Column[Integer] | int, correct_answer: list[str], answer: list[str]) -> int:
    pprint([correct_answer, answer])
    if q_number == 26:
        points_value: dict[bool, int] = {
            correct_answer == answer: 2,
            (correct_answer[:1], correct_answer[1:2]) == (answer[1:2], answer[:1]): 1,
            sum((answer[0] in correct_answer, answer[1] in correct_answer if len(answer) > 1 else 0)) == 1: 1
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
        if q_type_number in {20, 21}:
            continue
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
    chosen_questions: dict[Column[Integer] | int, type[Informatics]] = {}
    for question_number in questions:
        if question_number in {20, 21}:
            continue
        q_list: list[type[Informatics]] = []
        for difficulty in difficulties:
            q_list.extend(database.filter(
                Informatics.q_number == question_number,
                Informatics.q_difficulty == difficulty
            ))
        questions[question_number].extend(q_list)

        if question_number != 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
        elif question_number == 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
            linked: list[int] = list(map(int, chosen_questions.get(question_number).q_linked_with.split("&")))
            chosen_questions[20] = database.get(linked[0])
            chosen_questions[21] = database.get(linked[1])

    return chosen_questions


def get_test_var_exam() -> dict[Column[Integer], Type[Informatics]]:
    database: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    questions: defaultdict[Column[Integer], list[Type[Informatics]]] = defaultdict(list)
    for question in database.all():
        questions[question.q_number].append(question)
    chosen_questions: dict[Column[Integer] | int, Type[Informatics]] = {}
    for question_number in questions:
        if question_number in {20, 21}:
            continue
        if question_number != 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
        elif question_number == 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
            linked: list[int] = list(map(int, chosen_questions.get(question_number).q_linked_with.split("&")))
            chosen_questions[20] = database.get(linked[0])
            chosen_questions[21] = database.get(linked[1])

    return {num: chosen_questions[num] for num in sorted(chosen_questions)}

def start_test_session(*, user_id: int, stop_time: float, test: str) -> int | Column[Integer]:
    active_session: ActiveStudentsTestDB = connect_active_test_session()
    active_session.new_test_session(
        session_data={
            "user_id": user_id,
            "stop_time": stop_time,
            "test": test
        }
    )
    return active_session.session.query(ActiveStudentsTest).all()[-1].id

def check_test_session(*, user_id: int) -> ActiveStudentsTest | None:
    active_session: ActiveStudentsTest | None = connect_active_test_session().session.query(ActiveStudentsTest).filter(ActiveStudentsTest.user_id == user_id).first()
    if active_session:
        return active_session
    return None

def delete_old_test_session(*, session_id: int) -> None:
    active_session: ActiveStudentsTestDB = connect_active_test_session()
    active_session.remove_test_session(session_id=session_id)

def save_answer_for_session(session_id: int, q_num: str, answer: str) -> bool:
    active_session: ActiveStudentsTestDB = connect_active_test_session()
    is_added: bool = active_session.add_answer_to_test_session(session_id=session_id, q_num=q_num, answer=answer)
    return True if is_added else False

def update_statistics_to_student(user_id: int, statistics: dict[str, list[int]]) -> None:
    UsersStatisticsDB(db_name=USERS_STATISTICS_DB_NAME).change_statistics(id=user_id, data_to_change=statistics)

def get_statistics_for_students() -> list[tuple[str, dict[str, list[float]]]]:
    user_statistics: list[type[UsersStatistics]] = UsersStatisticsDB().session.query(UsersStatistics).all()
    common_statistics: list[tuple[str, dict[str, list[float]]]] = [
        (f"{user.firstname} {user.lastname}",
         {f"Тип {_type.split('_')[-1]}": list(map(float, stat.split("&"))) for _type, stat in user.to_dict().items()
        }) for user in user_statistics
    ]
    return common_statistics

def get_q_types_values() -> dict[str, dict[str, int]]:
    datas: list[str] = ["value", "Базовый", "Средний", "Сложный"]
    q_types_values: dict[str, dict[str, int]] = {f"Тип {num}": {data: 0 for data in datas} for num in range(1, 28)}
    database: list[type[Informatics]] = connect_database_informatics().session.query(Informatics).all()
    for question in database:
        q_types_values[f"Тип {question.q_number}"]["value"] += 1
        q_types_values[f"Тип {question.q_number}"][f"{question.q_difficulty}"] += 1

    return q_types_values


def get_all_questions_for_type(q_type: str) -> list[type[Informatics]]:
    if q_type == "19":
        return connect_database_informatics().session.query(Informatics).filter(
            Informatics.q_number > 18,
            Informatics.q_number < 22
        ).all()
    return connect_database_informatics().session.query(Informatics).filter(Informatics.q_number == int(q_type)).all()


if __name__ == '__main__':
    print(get_test_var_one(data_for_test={"q_right_answer": "2", "q_number": 1}))
from collections import defaultdict
from random import choice
from typing import Type
from sqlalchemy import Integer, Column
from sqlalchemy.orm import Query
from ..databases.InformaticsDB import Informatics, InformaticsDB


def get_mark_for_test(count_right_answers: int, questions_value: int) -> str:
    result: int = (count_right_answers * 100) // questions_value
    marks: dict[bool, str] = {
        0 <= result < 40: "2",
        40 <= result < 60: "3",
        60 <= result < 80: "4",
        result > 80: "5"
    }
    return marks[True]


def connect_database_informatics() -> InformaticsDB:
    return InformaticsDB()


def save_test_question(question_data: dict[str, str | int]) -> bool:
    database: InformaticsDB = connect_database_informatics()
    # print(question_data)
    database.add_question(question_data=question_data)

    return True


def check_test_variant(variant: list[int], answers: dict[str, str]) -> tuple[dict[str, str], str]:
    answers_and_marks: dict[str, str] = {}
    db_informatics: Query[type[Informatics]] = connect_database_informatics().session.query(Informatics)
    for q_id in variant:
        question: Informatics = db_informatics.get(q_id)
        answers_and_marks.update({f"{question.q_number}": "1" if answers.get(f"{question.q_number}") == question.q_right_answer else "0"})

    count_right_answers: int = sum(map(int, answers_and_marks.values()))

    return answers_and_marks, get_mark_for_test(count_right_answers=count_right_answers, questions_value=len(variant))


def get_test_var() -> dict[Column[Integer], Type[Informatics]]:
    database: InformaticsDB = connect_database_informatics()
    questions: defaultdict[Column[Integer], list[Type[Informatics]]] = defaultdict(list)
    for question in database.session.query(Informatics).all():
        questions[question.q_number].append(question)

    return {
        num: choice(questions.get(num)) for num in questions
    }



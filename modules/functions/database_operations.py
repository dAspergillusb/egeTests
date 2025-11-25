from collections import defaultdict
from random import choice
from typing import Type
from sqlalchemy import Integer, Column
from ..databases.InformaticsDB import Informatics, InformaticsDB


def connect_database() -> InformaticsDB:
    return InformaticsDB()

def get_test_var() -> dict[Column[Integer], Type[Informatics]]:
    database: InformaticsDB = connect_database()
    questions: defaultdict[Column[Integer], list[Type[Informatics]]] = defaultdict(list)
    for question in database.session.query(Informatics).all():
        questions[question.q_number].append(question)
    return {
        num: choice(questions.get(num)) for num in questions
    }

def save_test_question(question_data: dict[str, str | int]) -> bool:
    database: InformaticsDB = connect_database()
    print(question_data)
    database.add_question(question_data=question_data)

    return True




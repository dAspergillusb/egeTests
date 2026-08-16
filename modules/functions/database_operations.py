from collections import defaultdict
from collections.abc import Sequence
from itertools import count
from asyncpg import ObjectInUseError
from random import choice, randint
from pprint import pprint
from typing import Type, Any, Callable
from fastapi import Request, Depends
from sqlalchemy import Integer, Column, Row
from sqlalchemy.orm import Query, Session, Mapped
from starlette import status
from .._types.Types import Actions, HistoryTypes
from ..databases.MainDB import MainDB
from ..databases.UserSessionsDB import UserSessionsDB, UserSessions
from ..functions.security import generate_code_from_password
from ..databases.UsersDB import Users, UsersDB
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..databases.DailyStatisticsDB import DailyStatistics, DailyStatisticsDB
from ..databases.UsersStatisticsDB import UsersStatisticsDB, UsersStatistics
from ..databases.ActiveStudentsTest import ActiveStudentsTest, ActiveStudentsTestDB
from ..databases.ArchiveDatabasesDB import ArchiveDatabasesDB
from ..models.test_creation_model import TestCreation, TestCreation1921
from .files_operations import change_env_parameter, env_full_rewrite
from ..endpoints.config import CORRECT_ANSWERS_VALUE_TO_POINTS, env_settings


def get_mark_for_test(points_value: int, questions_value: int) -> str:
    result: int = CORRECT_ANSWERS_VALUE_TO_POINTS.get(points_value, 0)
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


async def save_test_question(question_data: dict[str, str | int] | dict[int, dict[str, int | str]]) -> bool:
    duplicate: bool = any((
        await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_all_typed_questions((Informatics.q_text == question_data.get("q_text"),)),
        await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_all_typed_questions((
            Informatics.q_text == question_data.get(19, {'q_text': ''}).get('q_text'),))
    ))
    if duplicate:
        return False
    if question_data.get("q_text") and question_data.get("q_right_answer"):
        database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
        await database.add_question(question_data=question_data)
        return True
    elif (
            all([question_data.get(num) for num in range(19, 22)]) and
            all([question_data.get(num).get(f"{value}") for num in range(19, 22) for value in ("q_text", "q_right_answer")])
    ):
        database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
        type_twenty_id: int =  await database.add_question(question_data=question_data.pop(20))
        type_twenty_one_id: int = await database.add_question(question_data=question_data.pop(21))
        question_data.get(19).update({
            "q_linked_with": "&".join([
                f"{type_twenty_id}",
                f"{type_twenty_one_id}"
            ])
        })
        await database.add_question(question_data=question_data.get(19))
        return True
    return False


async def change_test_question(q_id: int, data_to_change: TestCreation | TestCreation1921) -> list[type[Informatics] | None]:
    what_question_type: dict[bool, Callable] = {
        isinstance(data_to_change, TestCreation): change_standard_question,
        isinstance(data_to_change, TestCreation1921): change_special_question
    }
    return await what_question_type[True](q_id=q_id, data_to_change=data_to_change)


async def change_standard_question(q_id: int, data_to_change: TestCreation) -> list[type[Informatics] | None]:
    question_data = {
        "q_id": q_id,
        "q_difficulty": data_to_change.get_q_difficulty(),
        "q_text": data_to_change.get_q_text(),
        "q_right_answer": data_to_change.get_answers(),
    }
    return await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).change_question(data=question_data, files=data_to_change.get_files())


async def change_special_question(q_id: int, data_to_change: TestCreation1921) -> list[type[Informatics] | None]:
    new_data = {
        19: {
            "q_id": q_id,
            "q_number": 19,
            "q_difficulty": data_to_change.q_difficulty,
            "q_text": data_to_change.q_text_19,
            "q_right_answer": data_to_change.q_right_answer_19
        },
        20: {
            "q_number": 20,
            "q_difficulty": data_to_change.q_difficulty,
            "q_text": data_to_change.q_text_20,
            "q_right_answer": "&".join([
                data_to_change.q_right_answer_20_1,
                data_to_change.q_right_answer_20_2
            ])
        },
        21: {
            "q_number": 21,
            "q_difficulty": data_to_change.q_difficulty,
            "q_text": data_to_change.q_text_21,
            "q_right_answer": data_to_change.q_right_answer_21
        }
    }
    return await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).change_special_question(data=new_data)


async def check_test_variant(variant: list[int], answers: dict[str, list[str]]) -> tuple[dict[str, int], str, dict[str, list[int]]]:
    answers_and_marks: dict[str, int] = {}
    for_statistics: dict[str, list[int]] = {f"q_type_{num}": [0, 0] for num in range(1, 30 + 1)}
    db_informatics: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
    different_problem_types_value: set[Mapped[int]] = set()
    checked_test: list[int] = []
    q_count: count[int] = count(start=1)
    for q_id in variant:
        question: type[Informatics] | None = await db_informatics.get_question(q_id)
        if question:
            checked_test.append(q_id)
            q_type_number: Mapped[int] = question.q_number
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

    # It's need to remove questions that didn't be in test
    for_statistics = {q_type: stat for q_type, stat in for_statistics.items() if stat[0]}   #!TODO
    points_value: int = sum(answers_and_marks.values())
    print(points_value)
    # print(for_statistics)
    return (
        answers_and_marks,
        get_mark_for_test(points_value=points_value, questions_value=len(different_problem_types_value)),
        for_statistics
    )


async def save_daily_statistics(*, user_id: int, checked_test: list[int], answers_and_marks: dict[str, int]) -> None:
    daily_statistics: DailyStatisticsDB = DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    # print(user_id, checked_test, answers_and_marks, sep='\n')
    new_daily_statistics: dict[str, str | int] = {
        "user_id": user_id,
        "test": "&".join([f"{q_id}" for q_id in checked_test]),
        "result": "&".join(f"{answer}" for answer in answers_and_marks.values())
    }
    await daily_statistics.add_statistics(statistics_data=new_daily_statistics)


def check_one_point_problem(correct_answer: list[str], answer: list[str]) -> int:
    return 1 if correct_answer == answer else 0


def check_two_points_problem(q_number: int, correct_answer: list[str], answer: list[str]) -> int:
    pprint([correct_answer, answer])
    if q_number == 26:
        points_value: dict[bool, int] = {
            correct_answer == answer: 2,
            correct_answer == answer[::-1]: 1,
            sum((answer[0] in correct_answer, answer[1] in correct_answer if len(answer) > 1 else 0)) == 1: 1
    }
        return points_value.get(True, 0)

    points_value: dict[bool, int] = {
        correct_answer == answer: 2,
        (correct_answer[:2], correct_answer[2:]) == (answer[2:], answer[:2]): 1,
        sum((" ".join(answer[:2]) in " ".join(correct_answer), " ".join(answer[2:]) in " ".join(correct_answer))) == 1: 1
    }
    return points_value.get(True, 0)


async def get_test_var_one(data_for_test: dict[str, str]) -> dict[int, Informatics]:
    database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
    questions: dict[int, Informatics] = {}
    q_count: count[int] = count(start=1)
    q_types: dict[str, str] = {
        num: value for num, value in data_for_test.items() if value and num.isdigit()
    }
    for q_type_number in q_types:
        if q_type_number in {"20", "21"}:
            continue
        difficulties: set[str] = {
            data_for_test.get(f"check_{diff}_{q_type_number}")
            for diff in ["base", "middle", "hard"]
            if data_for_test.get(f"check_{diff}_{q_type_number}")
        }
        q_list: list[Informatics] = []
        for difficulty in difficulties:
            q_list.extend(await database.get_all_typed_questions(
                (Informatics.q_number == int(q_type_number),
                Informatics.q_difficulty == difficulty)
            ))
        if q_type_number == "19":
            for _ in range(int(q_types[q_type_number])):
                index: int = randint(0, len(q_list) - 1)
                question: Informatics = q_list.pop(index)
                linked_twenty, linked_twenty_one = map(int, question.q_linked_with.split("&"))
                questions[next(q_count)] = question
                questions[next(q_count)] = await database.get_question(linked_twenty)
                questions[next(q_count)] = await database.get_question(linked_twenty_one)
        else:
            for _ in range(int(q_types[q_type_number])):
                if q_list:
                    index: int = randint(0, len(q_list) - 1)
                    questions[next(q_count)] = q_list.pop(index)
    return questions


async def get_test_var_two(data_for_test: dict[str, str]) -> dict[int, type[Informatics]]:
    database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
    questions: dict[int, list[Informatics]] = {num: [] for num in range(1, int(data_for_test.get("test_range", 11)) + 1)}
    for question_number in questions:
        questions[question_number].extend(
            await database.get_all_typed_questions((
                Informatics.q_number == int(question_number),
                Informatics.q_difficulty == "Базовый"
            ))
        )
    return {
        num: choice(questions.get(num)) for num in questions if questions.get(num)
    }


async def get_test_var_three(data_for_test: dict[str, str]) -> dict[Mapped[int] | int, Informatics]:
    database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
    questions: dict[int, list[Informatics]] = {num: [] for num in range(1, 28)}
    difficulties: set[str] = {data_for_test[difficulty] for difficulty in data_for_test if data_for_test[difficulty]}
    chosen_questions: dict[Mapped[int] | int, Informatics] = {}
    for question_number in questions:
        if question_number in {20, 21}:
            continue
        q_list: list[Informatics] = []
        for difficulty in difficulties:
            q_list.extend(await database.get_all_typed_questions((
                Informatics.q_number == question_number,
                Informatics.q_difficulty == difficulty
            )))
        questions[question_number].extend(q_list)

        if question_number != 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
        elif question_number == 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions.get(question_number))
            # If it will the case when there is no linked ids from nineteen question,
            # api will be crashed, so I create the temporary patch below. It is not solution
            # but api will not be crashed.
            if chosen_questions[question_number].q_linked_with:
                linked_twenty, linked_twenty_one = map(int, chosen_questions.get(question_number).q_linked_with.split("&"))
                chosen_questions[20] = await database.get_question(linked_twenty)
                chosen_questions[21] = await database.get_question(linked_twenty_one)

    return chosen_questions


async def get_test_var_exam() -> dict[Mapped[int] | int, Informatics]:
    database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
    questions: defaultdict[Mapped[int] | int, list[Informatics]] = defaultdict(list)
    for question in await database.get_all_questions():
        questions[question.q_number].append(question)
    chosen_questions: dict[Mapped[int] | int, Informatics] = {}
    for question_number in questions:
        if question_number in {20, 21}:
            continue
        if question_number != 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions[question_number])
        elif question_number == 19 and questions.get(question_number):
            chosen_questions[question_number] = choice(questions[question_number])
            # If it will the case when there is no linked ids from nineteen question,
            # api will be crashed, so I create the temporary patch below. It is not solution
            # but api will not be crashed.
            if chosen_questions[question_number].q_linked_with:
                linked_twenty, linked_twenty_one = map(int, chosen_questions[question_number].q_linked_with.split("&"))
                chosen_questions[20] = await database.get_question(linked_twenty)
                chosen_questions[21] = await database.get_question(linked_twenty_one)

    return {num: chosen_questions[num] for num in sorted(chosen_questions)}


async def start_test_session(*, user_id: int, session_id: str, stop_time: float | int, test: dict[int, int]) -> int:
    active_session: ActiveStudentsTestDB = ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    session_id: int = await active_session.new_test_session(
        session_data={
            "user_id": user_id,
            "session_id": session_id,
            "stop_time": stop_time,
            "test": test
        }
    )
    return session_id


async def check_test_session(*, session_id: str) -> ActiveStudentsTest | None:
    active_session: ActiveStudentsTest | None = await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_test_session_for_student(session_id=session_id)
    if active_session:
        return active_session
    return None


async def delete_old_test_session(*, ast_id: int) -> None:
    if not ast_id:
        print(f"There is no session with id: {ast_id} in Cookies!")
        return None
    active_session: ActiveStudentsTestDB = ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    return await active_session.remove_test_session(ast_id=ast_id)


async def save_answer_for_session(ast_id: int, q_num: str, answer: list[str]) -> bool:
    if not ast_id:
        return False
    active_session: ActiveStudentsTestDB = ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    is_added: bool = await active_session.add_answer_to_test_session(ast_id=ast_id, q_num=q_num, answer=answer)
    return True if is_added else False


async def update_statistics_to_student(user_id: int, statistics: dict[str, list[int]]) -> None:
    await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).change_statistics(user_id=user_id, data_to_change=statistics)


async def get_statistics_for_students() -> list[tuple[str, dict[str, list[float]]]]:
    join: type[Users] = Users
    user_statistics: Sequence[Row[Any]] = await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_all_statistics(join=join)
    common_statistics: list[tuple[str, dict[str, list[float]]]] = [
        (f"{user.firstname} {user.lastname}",
         {f"Тип {_type.split('_')[-1]}": list(map(float, stat.split("&"))) for _type, stat in statistics.to_dict().items()
        }) for user, statistics in user_statistics
    ]

    return common_statistics


async def get_q_types_values() -> dict[str, dict[str, int]]:
    datas: list[str] = ["value", "Базовый", "Средний", "Сложный"]
    q_types_values: dict[str, dict[str, int]] = {f"Тип {num}": {data: 0 for data in datas} for num in range(1, 28)}
    database: Sequence[Informatics] = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_all_questions()
    for question in database:
        q_types_values[f"Тип {question.q_number}"]["value"] += 1
        q_types_values[f"Тип {question.q_number}"][f"{question.q_difficulty}"] += 1
    return q_types_values


async def get_sorted_statistics_for_students() -> list[tuple[str, dict[str, list[float]]]]:
    return sorted(await get_statistics_for_students(), key=lambda user: user[0])


async def get_all_questions_for_type(q_type: str) -> list[Informatics]:
    if q_type == "19":
        return await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_all_typed_questions(
            conditions=(
                Informatics.q_number == 19,
                Informatics.q_number == 20,
                Informatics.q_number == 21
            ),
            _or=True
        )
    return await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_all_typed_questions(
        conditions=(
            Informatics.q_number == int(q_type),
        )
    )


async def rewrite_add_table(action: str, csv_file: str) -> None:
    rewrite_or_add: dict[str, Callable] = {
        Actions.ADD: create_new_users,
        Actions.REWRITE: rewrite_users
    }
    return await rewrite_or_add[action](csv_file=csv_file)


async def rewrite_users(csv_file: str) -> None:
    await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).clear_table()
    await create_new_users(csv_file=csv_file)


async def clear_or_create_database_users(**kwargs) -> int:
    session_id: str = ""
    if "request" in kwargs:
        request: Request = kwargs["request"]
        session_id = request.cookies.get("session_id", "")
    if session_id: # I think, that if session_id exists in database it means that the user exists too.
        active_session: type[UserSessions] | None = await UserSessionsDB(
            db_name=env_settings.MAIN_DB_USERS_NAME
        ).get_session(session_id=session_id)
        user_id: int = active_session.user_id
        active_user: type[Users] | None = await UsersDB(
            db_name=env_settings.MAIN_DB_USERS_NAME
        ).choose_user(user_id=user_id)
        if not active_user:
            return status.HTTP_404_NOT_FOUND
        if all((
                "db_type" in kwargs,
                "new_db_name" in kwargs
        )):
            setattr(env_settings, kwargs["db_type"], kwargs["new_db_name"])
        try:
            await MainDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_main_db()
        except ObjectInUseError:
            db_name: str = env_settings.MAIN_DB_USERS_NAME
            await MainDB(db_name=db_name).close_connections_to_main_db()
            await MainDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_main_db()
        await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
        id_new_user: int = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).add_user(active_user)
        await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
        await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
        await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_new_session(
            user_id=id_new_user,
            user_agent=active_session.user_agent,
            ip_address=active_session.ip_address,
            session_id=session_id
        )
    await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    if active_user.username != "admin":
        await create_new_users(csv_file="Admin;;;;admin;admin;admin")
    return status.HTTP_204_NO_CONTENT
    return status.HTTP_404_NOT_FOUND


async def clear_or_create_database_informatics(**kwargs) -> int:
    if all((
            "db_type" in kwargs,
            "new_db_name" in kwargs
    )):
        setattr(env_settings, kwargs["db_type"], kwargs["new_db_name"])
    try:
        await MainDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).create_main_db()
    except ObjectInUseError:
        db_name: str = env_settings.MAIN_DB_INFORMATICS_NAME
        await MainDB(db_name=db_name).close_connections_to_main_db()
        await MainDB(db_name=db_name).create_main_db()
    await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).init_db()
    return status.HTTP_204_NO_CONTENT


async def add_to_archive(db_type: str) -> int:
    history_types: dict[str, Callable] = {
        HistoryTypes.INFORMATICS: create_informatics_database_archive,
        HistoryTypes.USERS: create_users_database_archive,
    }
    if db_type in history_types:
        await history_types[db_type]()
        return status.HTTP_201_CREATED
    return status.HTTP_404_NOT_FOUND


async def create_users_database_archive() -> int:
    created: bool = await ArchiveDatabasesDB(db_name=env_settings.MAIN_DB_ARCHIVE_NAME).add_history(
        history_type=HistoryTypes.USERS,
        history_data={
            "main_db_name": {"MAIN_DB_USERS_NAME": env_settings.MAIN_DB_USERS_NAME},
            "db_structure": {
                "USERS_DB_NAME": env_settings.USERS_DB_NAME,
                "USERS_STATISTICS_DB_NAME": env_settings.USERS_STATISTICS_DB_NAME,
                "DAILY_STATISTICS_DB_NAME": env_settings.DAILY_STATISTICS_DB_NAME,
                "ACTIVE_STUDENTS_TEST_DB_NAME": env_settings.ACTIVE_STUDENTS_TEST_DB_NAME
            }
        }
    )
    return status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT


async def create_informatics_database_archive() -> int:
    created: bool = await ArchiveDatabasesDB(db_name=env_settings.MAIN_DB_ARCHIVE_NAME).add_history(
        history_type=HistoryTypes.INFORMATICS,
        history_data={
            "main_db_name": {"MAIN_DB_INFORMATICS_NAME": env_settings.MAIN_DB_INFORMATICS_NAME},
            "db_structure": {
                "INFORMATICS_DB_NAME": env_settings.INFORMATICS_DB_NAME
            }
        }
    )
    return status.HTTP_201_CREATED if created else status.HTTP_409_CONFLICT


async def create_new_users(
        csv_file: str,
) -> bool:
    data_to_load: list[dict[str, str]] = [
        {
            "firstname": firstname.strip(),
            "lastname": lastname.strip(),
            "sex": sex.strip(),
            "school_class": school_class.strip(),
            "username": username.strip(),
            "password": generate_code_from_password(password=password),
            "rank": rank.strip()
        }
        for firstname, lastname, sex, school_class, username, password, rank in [line.split(";") for line in csv_file.split("\n") if line]
    ]
    new_user_db: UsersDB = UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    # new_user_stat_db: UsersStatisticsDB = UsersStatisticsDB()
    for user_data in data_to_load:
        await new_user_db.add_user(user_data)
        # if user_data["rank"] == Ranks.STUDENT:
        #     await new_user_stat_db.add_statistics(statistics_data={"user_id": user_id})
    return True


async def change_users_parameters(db_structure: dict[str, str], request: Request) -> int:
    # Get data from active admin
    user_id: int = int(request.cookies.get("user_id", 0))
    active_admin: type[Users] | None = await UsersDB(
        db_name=env_settings.MAIN_DB_USERS_NAME
    ).choose_user(user_id=user_id)
    if not active_admin:
        return status.HTTP_400_BAD_REQUEST
    active_session_id: str = request.cookies.get("session_id", "")

    # Change env_settings with users parameters
    if all((
        db_structure.get("MAIN_DB_USERS_NAME"),
        db_structure.get("USERS_DB_NAME"),
        db_structure.get("USERS_STATISTICS_DB_NAME"),
        db_structure.get("DAILY_STATISTICS_DB_NAME"),
        db_structure.get("ACTIVE_STUDENTS_TEST_DB_NAME")
    )):
        env_settings.MAIN_DB_USERS_NAME = db_structure["MAIN_DB_USERS_NAME"]
        env_settings.USERS_DB_NAME = db_structure["USERS_DB_NAME"]
        env_settings.DAILY_STATISTICS_DB_NAME = db_structure["DAILY_STATISTICS_DB_NAME"]
        env_settings.USERS_STATISTICS_DB_NAME = db_structure["USERS_STATISTICS_DB_NAME"]
        env_settings.ACTIVE_STUDENTS_TEST_DB_NAME = db_structure["ACTIVE_STUDENTS_TEST_DB_NAME"]
    else:
        return status.HTTP_400_BAD_REQUEST

    # Check if admin not in archived database (it creates if not)
    users_db: UsersDB = UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME)
    active_admin_id: int = 0
    if active_admin and not await users_db.exist_username(active_admin.username):
        active_admin_id = await users_db.add_user(active_admin)

    # Create session with old session_id
    if not await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).session_id_exists(session_id=active_session_id):
        await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_new_session(
            user_id=active_admin_id,
            user_agent=request.headers.get("User-Agent", ""),
            ip_address=request.client.host,
            session_id=active_session_id,
        )

    # Change parameters in .env-file
    await env_full_rewrite(
        full_env=env_settings.__dict__
    )
    return status.HTTP_200_OK


async def change_informatics_parameters(db_structure: dict[str, str]) -> int:
    env_settings.MAIN_DB_INFORMATICS_NAME = db_structure["MAIN_DB_INFORMATICS_NAME"]
    env_settings.INFORMATICS_DB_NAME = db_structure["INFORMATICS_DB_NAME"]
    await env_full_rewrite(full_env=env_settings.__dict__)
    return status.HTTP_200_OK


if __name__ == '__main__':
    print(get_test_var_one(data_for_test={"q_right_answer": "2", "q_number": 1}))
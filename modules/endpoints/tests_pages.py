from collections import defaultdict
from pprint import pprint
from time import time
from typing import Callable, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Mapped
from starlette.templating import _TemplateResponse
from sqlalchemy import Column, Integer
from .._types.Types import Ranks
from ..databases.DailyStatisticsDB import DailyStatisticsDB
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..databases.ActiveStudentsTest import ActiveStudentsTest, ActiveStudentsTestDB
from ..databases.UsersStatisticsDB import UsersStatisticsDB, UsersStatistics
from ..databases.UserSessionsDB import UserSessionsDB, UserSessions
from ..functions.dependencies import Roles
from ..models.test_result_model import TestResultData
from ..models.test_type_model import TestVarOne, TestVarTwo, TestVarThree
from ..models.test_save_answers_model import AnswerForSave, AnswerForCheck
from ..models.for_question_data import ForQuestionData
from .config import TOPICS_FOR_PROBLEM_TYPES, env_settings
from ..functions.database_operations import (
    check_one_point_problem,
    check_two_points_problem,
    save_daily_statistics,
    get_test_var_exam,
    get_test_var_one,
    get_test_var_two,
    get_test_var_three,
    start_test_session,
    check_test_session,
    delete_old_test_session,
    save_answer_for_session
)
from ..functions.database_operations import check_test_variant, update_statistics_to_student
from ..functions.test_time import get_time_of_test
from .main_pages import TEMPLATES

all_allowed: Roles = Roles(allowed_roles=[Ranks.STUDENT, Ranks.ADMIN, Ranks.TEACHER])
students_allowed: Roles = Roles(allowed_roles=[Ranks.STUDENT])

def register_tests_pages(app: FastAPI) -> None:

    @app.get("/student_cabinet")
    async def get_student_cabinet(
            request: Request,
            name: str = Depends(students_allowed),
            session_id: Optional[str] = Cookie(None),
            user_id: Optional[int] = Cookie(None)
    ) -> _TemplateResponse:
        # school_class: str | None = request.session.get("school_class")
        # user_id: int = int(request.cookies.get("user_id", 0))
        db_user_statistics: UsersStatisticsDB = UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME)
        student_statistics: UsersStatistics | None = await db_user_statistics.get_statistics_by_userid(user_id=user_id)
        common_statistics: dict[str, float | str] = {
            "absolute_questions_value": 0.0,
            "absolute_right_answers_value": 0.0,
            "absolute_accuracy_persent": 0.0,
            "result": ""
        }
        common_values: list[float] = []
        right_answers_values: list[float] = []
        accuracy_persent_values: list[float] = []
        conclusions_for_results: list[str] = []
        if student_statistics:
            for q_stat in student_statistics:
                questions_value, right_answers, accuracy_persent = map(float, q_stat.split("&"))
                common_statistics["absolute_questions_value"] += questions_value
                common_statistics["absolute_right_answers_value"] += right_answers
                # common_statistics["absolute_accuracy_persent"] += accuracy_persent

                conclusion_for_result: dict[bool, str] = {
                    0 < accuracy_persent < 40: "Необходимо обратить внимание!",
                    40 <= accuracy_persent < 60: "Необходимо ещё поработать.",
                    60 <= accuracy_persent < 80: "Нормально.",
                    accuracy_persent >= 80: "Всё хорошо.",
                    questions_value <= 10: "Недостаточно данных для статистики"
                }
                conclusions_for_results.append(conclusion_for_result.get(True, "Нет данных"))
                common_values.append(questions_value)
                right_answers_values.append(right_answers)
                accuracy_persent_values.append(
                    round(
                        number=accuracy_persent,
                        ndigits=3
                    )
                )
        common_statistics["absolute_accuracy_persent"] = round(
            number=common_statistics["absolute_right_answers_value"] * 100 / common_statistics["absolute_questions_value"] if common_statistics["absolute_questions_value"] else 0,
            ndigits=3
        )
        absolute_conclusion_for_result: dict[bool, str] = {
            0 < common_statistics["absolute_accuracy_persent"] < 40: "Необходимо больше тренироваться!",
            40 <= common_statistics["absolute_accuracy_persent"] < 60: "Нужно побольше решать задания.",
            60 <= common_statistics["absolute_accuracy_persent"] < 80: "В целом нормально",
            common_statistics["absolute_accuracy_persent"] >= 80: "В целом хорошо."
        }
        common_statistics["result"] = absolute_conclusion_for_result.get(True, "Нет данных")

        daily_statistics: dict[str, defaultdict[str, list[type[Informatics]]]] = await DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_daily_statistics_for_student(user_id=user_id)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="student_cabinet.html",
            context={
                "request": request,
                "name": name,
                # "school_class": school_class,
                "common_statistics": common_statistics,
                "labels": [f"Тип {num}" for num in range(1, 28)],
                "common_values": common_values,
                "right_answers_values": right_answers_values,
                "accuracy_persent_values": accuracy_persent_values,
                "conclusions_for_results": conclusions_for_results,
                "daily_statistics": daily_statistics,
                "len": len,
                "nav_topic": "Личный кабинет"
            }
        )


    @app.get("/prepare_test", response_model=None)
    async def get_page_prepare_test(
            request: Request,
            name: str = Depends(all_allowed),
            user_id: Optional[int] = Cookie(None),
            rank: Optional[str] = Cookie(None),
            session_id: Optional[str] = Cookie(None)
    ) -> _TemplateResponse | RedirectResponse:
        if request.session.get("informatics_variant"):
            request.session.__delitem__("informatics_variant")
        # user_id: int = request.session.get("user_id", 0)
        # school_class: str = request.session.get("school_class", "")
        modal_old_test_session: bool = False

        current_session: type[UserSessions] | None = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_session(session_id=session_id) #TODO
        old_test_session: ActiveStudentsTest | None = await check_test_session(session_id=current_session.session_id)
        if old_test_session:
            request.session["old_test_session"] = old_test_session.ast_id
            request.session["stop_test"] = old_test_session.stop_time
            request.session["informatics_variant"] = old_test_session.test
            modal_old_test_session = not modal_old_test_session

        topics_problems_types: dict[int, str] = {
            num: topic for num, topic in enumerate(TOPICS_FOR_PROBLEM_TYPES, start=1)
        }
        # informatics: dict[Column[Integer], Type[Informatics]] = get_test_var()
        # request.session["informatics_variant"] = "&".join(f"{informatics[question].q_id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/choose_test_type.html",
            context={
                "request": request,
                "name": name,
                "rank": rank,
                # "school_class": school_class,
                "topics_problems_types": topics_problems_types,
                'old_session': modal_old_test_session,
                "nav_topic": "Выбор варианта генерации теста",
                "generation_types": True
            }
        )

    @app.post("/test")
    async def get_start_test_page(
            request: Request,
            data_for_test: TestVarOne | TestVarTwo | TestVarThree = Form(default=None),
            rank: Optional[str] = Cookie(None),
            name: str = Depends(all_allowed)
    ) -> _TemplateResponse:
        school_class: str = request.session.get("school_class", "")
        what_type_of_test: dict[bool, Callable] = {
            isinstance(data_for_test, TestVarOne): get_test_var_one,
            isinstance(data_for_test, TestVarTwo): get_test_var_two,
            isinstance(data_for_test, TestVarThree): get_test_var_three,
        }
        informatics: dict[int, type[Informatics]] = await what_type_of_test[True](data_for_test.to_dict())
        if not informatics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Похоже, что в базе нет ни одного вопроса. Попроси администратора или учителя добавть вопросы."
            )
        informatics_to_session = {
            num: informatics[question].q_id for num, question in enumerate(informatics, start=1)
        }
        request.session["informatics_variant"] = informatics_to_session
        # pprint([name, [(informatics[x].q_id, informatics[x].q_right_answer) for x in informatics]])
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test_rewrite.html",
            context={
                "request": request,
                "name": name,
                "rank": rank,
                "school_class": school_class,
                "variant": informatics_to_session,
                "nav_topic": "Вариант теста готов"
            }
        )

    @app.post("/exam")
    async def get_start_exam_page(
            request: Request,
            rank: Optional[str] = Cookie(None),
            name: str = Depends(all_allowed),
    ) -> _TemplateResponse:
        school_class: str = request.session.get("school_class", "")
        informatics: dict[Mapped[int] | int, Informatics] = await get_test_var_exam()
        informatics_to_session = {
            num: informatics[question].q_id for num, question in enumerate(informatics, start=1)
        }
        request.session["informatics_variant"] = informatics_to_session
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test_rewrite.html",
            context={
                "request": request,
                "name": name,
                "rank": rank,
                "school_class": school_class,
                "variant": informatics_to_session,
                "nav_topic": "Вариант теста готов"
            }
        )

    @app.get("/testing", response_model=None)
    async def test_is_started(
            request: Request,
            user_id: Optional[int] = Cookie(None),
            session_id: Optional[str] = Cookie(None),
            rank: Optional[str] = Cookie(None),
            name: str = Depends(all_allowed),
    ) -> _TemplateResponse | RedirectResponse:
        # user_id: int = request.session.get("user_id", 0)
        database: InformaticsDB = InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME)
        questions_ids: dict[int, int] = request.session["informatics_variant"]
        informatics: dict[int, type[Informatics] | None] = {
            num: await database.get_question(_id) for num, _id in questions_ids.items()
        }
        max_question_number: int = max(informatics)
        if all((not request.session.get("start_test"), not request.session.get("stop_test"))):
            start_time: int = int(time())
            stop_time: int = start_time + get_time_of_test([question.q_number for question in informatics.values()])
            request.session["start_test"] = start_time
            request.session["stop_test"] = stop_time
            test_time: int = stop_time - start_time
        else:
            test_time: int = request.session.get("stop_test", 0) - int(time())

        active_test_session: type[ActiveStudentsTest] | None = None
        ast_id: int = request.session.get("old_test_session", 0)
        if not ast_id:
            active_session: type[UserSessions] | None = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_session(session_id=session_id)
            request.session["old_test_session"] = await start_test_session(
                user_id=user_id,
                session_id=active_session.session_id,
                stop_time=request.session.get('stop_test', -1),
                test=request.session.get('informatics_variant', {})
            )
        else:
            active_test_session = await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_test_session(ast_id=ast_id)

        print(request.session.get("old_test_session"))
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test_started_rewrite.html",
            context={
                "request": request,
                "len": len,
                "name": name,
                "rank": rank,
                "variant": informatics,
                "test_time": test_time,
                "max_question_number": max_question_number,
                "old_session": active_test_session.to_dict() if active_test_session else {},
                "str": str,
                "nav_topic": "Успешного решения теста"
            }
        )

    @app.post("/answer")
    async def get_answer(
            request: Request,
            answer: AnswerForSave | AnswerForCheck
    ):
        print(type(answer), answer.answer)
        if answer.is_empty():
            return False
        if isinstance(answer, AnswerForSave):
            is_saved: bool = await save_answer_for_session(
                ast_id=request.session.get("old_test_session", 0),
                q_num=answer.q_num[2:],
                answer=answer.answer
            )
            return True if is_saved else False

        print(answer.q_from_old_test, answer.answer)
        question: type[Informatics] | None = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_question(int(answer.q_from_old_test))
        q_number: int = question.q_number
        if not q_number:
            return None
        check_results: dict[bool, int] = {
            q_number < 26: check_one_point_problem(
                correct_answer=question.q_right_answer.split("&"),
                answer=answer.answer
            ),
            q_number >= 26: check_two_points_problem(
                q_number=question.q_number,
                correct_answer=question.q_right_answer.split("&"),
                answer=answer.answer
            )
        }
        return check_results[True] if not check_results[True] else check_results[True] + 1 if q_number < 26 else check_results[True] #!TODO

    @app.post("/question_data")
    async def get_question_data(
            request: Request,
            for_question: ForQuestionData
    ):
        active_user_session: int = request.session.get("old_test_session", 0)
        if active_user_session:
            active_session: type[ActiveStudentsTest] | None = await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_test_session(ast_id=active_user_session)
            # print(f"{active_session=}")
            question_id: int = active_session.test[for_question.q_num]
            needed_question_data: type[Informatics] | None = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_question(question_id)
            needed_question_data.q_right_answer = len(needed_question_data.q_right_answer.split("&"))
            needed_question_data.answers = active_session.answers[for_question.q_num]
            # print(active_session.answers[for_question.q_num])
            return needed_question_data
        return ""

    @app.post("/old_test/{date}/{time}")
    async def get_old_test_page(
            request: Request,
            date: str,
            time: str,
            name: str = Depends(all_allowed)
    ) -> _TemplateResponse:
        date: str = "&".join((date, time))
        old_test, old_results = await DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_old_test(date=date)

        return TEMPLATES.TemplateResponse(
            request=request,
            name="test_pages/get_old_test.html",
            context={
                "request": request,
                "name": name,
                "variant": old_test,
                "old_results": old_results,
                "len": len,
                "nav_topic": "Работа над ошибками"
            }
        )

    @app.get("/files/{problem_num}/{filename}")
    def get_file(problem_num: str, filename: str) -> FileResponse:
        path: str = f"/files/{problem_num}/{filename}"
        return FileResponse(path=path, filename=filename)

    @app.post("/delete_old_test_session")
    async def remove_old_test_session(request: Request):
        # print(request.session)
        old_test_session_id: int = request.session.get("old_test_session", 0)
        await delete_old_test_session(ast_id=old_test_session_id)
        request.session.pop("old_test_session")
        if request.session.get("stop_test"):
            request.session.pop("stop_test")
        if request.session.get("start_test"):
            request.session.pop("start_test")
        # print(request.session)

    @app.post("/test_results")
    async def get_test_results(
            request: Request,
            test_data: TestResultData = Form(default=""),
            user_id: Optional[int] = Cookie(None),
            rank: Optional[str] = Cookie(None),
            name: str = Depends(all_allowed)
    ) -> _TemplateResponse:
        active_user_session: type[ActiveStudentsTest] | None = await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_test_session(
            ast_id=request.session.get("old_test_session", 0)
        )
        if not active_user_session:
            return RedirectResponse(url="/prepare_test")
        print(active_user_session.answers)
        # rank: str = request.session.get("rank", "")
        answers: dict[str, list[str]] = {
            q_num: answer.split("$") for q_num, answer in active_user_session.answers.items()
        }
        # answers: dict[str, list[str]] = test_data.to_dict()
        variant: list[int] = list(active_user_session.test.values())
        # variant: list[int] = list(map(int, request.session["informatics_variant"].split("&")))
        pprint(variant)
        results, mark, for_statistics = await check_test_variant(
                    variant=variant,
                    answers=answers
        )
        if rank == Ranks.STUDENT:
            await update_statistics_to_student(
                user_id=user_id,
                statistics=for_statistics
            )
            await save_daily_statistics(
                user_id=user_id,
                checked_test=variant,
                answers_and_marks=results
            )
        await delete_old_test_session(
            ast_id=request.session.get("old_test_session", 0)
        )
        request.session.pop("old_test_session")
        if request.session.get("stop_test"):
            request.session.pop("stop_test")
        if request.session.get("start_test"):
            request.session.pop("start_test")
        pprint([name, mark.split("&")])
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/testing_result.html",
            context={
                "request": request,
                "name": name,
                "rank": rank,
                "answers": results,
                "mark": mark,
                "nav_topic": "Результаты"
            }
        )


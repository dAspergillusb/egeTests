from itertools import count
from pprint import pprint
from time import time
from typing import Type, Callable
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Query
from starlette.responses import JSONResponse
from starlette.templating import _TemplateResponse
from sqlalchemy import Column, Integer
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..databases.ActiveStudentsTest import ActiveStudentsTest
from ..models.test_result_model import TestResultData
from ..models.test_type_model import TestVarOne, TestVarTwo, TestVarThree
from ..models.test_save_answers_model import AnswerForSave, AnswerForCheck
from ..models.for_question_data import ForQuestionData
from .config import TOPICS_FOR_PROBLEM_TYPES, INFORMATICS_DB_NAME
from ..functions.database_operations import (
    connect_database_informatics,
    check_one_point_problem,
    check_two_points_problem,
    save_daily_statistics,
    get_test_var_exam,
    get_test_var_one,
    get_test_var_two,
    get_test_var_three,
    connect_active_test_session,
    start_test_session,
    check_test_session,
    delete_old_test_session,
    save_answer_for_session
)
from ..functions.database_operations import check_test_variant, update_statistics_to_student
from ..functions.test_time import get_time_of_test
from .main_pages import TEMPLATES

def register_tests_pages(app: FastAPI) -> None:

    @app.get("/prepare_test", response_model=None)
    def get_page_prepare_test(request: Request) -> _TemplateResponse | RedirectResponse:
        if request.session.get("informatics_variant"):
            request.session.__delitem__("informatics_variant")
        name: str = request.session.get("name")
        if not name:
            return RedirectResponse(url="/")
        school_class: str = request.session.get("school_class")
        modal_old_session: bool = False

        old_session: ActiveStudentsTest = check_test_session(user_id=request.session.get("user_id"))
        if old_session:
            request.session["old_test_session"] = old_session.id
            request.session["stop_test"] = old_session.stop_time
            request.session["informatics_variant"] = old_session.test
            modal_old_session = not modal_old_session

        topics_problems_types: dict[int, str] = {
            num: topic for num, topic in enumerate(TOPICS_FOR_PROBLEM_TYPES, start=1)
        }
        # informatics: dict[Column[Integer], Type[Informatics]] = get_test_var()
        # request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/choose_test_type.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
                "topics_problems_types": topics_problems_types,
                'old_session': modal_old_session,
                "nav_topic": "Выбор варианта генерации теста",
                "generation_types": True
            }
        )

    @app.post("/test")
    def get_start_test_page(
            request: Request,
            data_for_test: TestVarOne | TestVarTwo | TestVarThree = Form(default=None)
    ) -> _TemplateResponse:
        # print(data_for_test.to_dict())
        name: str = request.session.get("name")
        if not name:
            return RedirectResponse(url="/")
        school_class: str = request.session.get("school_class")
        what_type_of_test: dict[bool, Callable] = {
            isinstance(data_for_test, TestVarOne): get_test_var_one,
            isinstance(data_for_test, TestVarTwo): get_test_var_two,
            isinstance(data_for_test, TestVarThree): get_test_var_three,
        }

        informatics: dict[Column[Integer], type[Informatics]] = what_type_of_test[True](data_for_test.to_dict())
        request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        pprint([name, [(informatics[x].id, informatics[x].q_right_answer) for x in informatics]])
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test_rewrite.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
                "variant": informatics.keys(),
                "nav_topic": "Вариант теста готов"
            }
        )

    @app.post("/exam")
    def get_start_exam_page(
            request: Request
    ) -> _TemplateResponse:
        name: str = request.session.get("name")
        if not name:
            return RedirectResponse(url="/")
        school_class: str = request.session.get("school_class")
        informatics: dict[Column[Integer], type[Informatics]] = get_test_var_exam()
        request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
                "variant": informatics.keys(),
                "nav_topic": "Вариант теста готов"
            }
        )

    @app.get("/testing", response_model=None)
    def test_is_started(
            request: Request
    ) -> _TemplateResponse | RedirectResponse:
        name: str = request.session.get("name")
        if not name:
            request.session.clear()
            return RedirectResponse(url="/")
        school_class: str = request.session.get("school_class")
        q_count: count = count(start=1)
        database: Query[type[Informatics]] = InformaticsDB(db_name=INFORMATICS_DB_NAME).session.query(Informatics)
        informatics: dict[int, type[Informatics]] = {
            next(q_count): database.get(_id) for _id in map(int, request.session["informatics_variant"].split("&"))
        }
        max_question_number: int = max(informatics)
        print("stop_test =", request.session.get("stop_test"))
        print("start_test =", request.session.get("start_test"))
        if all((not request.session.get("start_test"), not request.session.get("stop_test"))):
            start_time: int = int(time())
            stop_time: int = start_time + get_time_of_test([int(question.q_number) for question in informatics.values()])
            request.session["start_test"] = start_time
            request.session["stop_test"] = stop_time
            test_time: int = request.session.get("stop_test") - request.session.get("start_test")
        else:
            test_time: int = request.session.get("stop_test") - int(time())

        active_session: type[ActiveStudentsTest] | None = None
        if not request.session.get("old_test_session"):
            request.session["old_test_session"] = start_test_session(
                user_id=request.session.get("user_id"),
                stop_time=request.session.get('stop_test'),
                test=request.session.get('informatics_variant')
            )
        else:
            active_session = connect_active_test_session().session.get(ActiveStudentsTest, request.session.get("old_test_session"))


        print(request.session.get("old_test_session"))
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/generated_test_started_rewrite.html", #"/test_pages/generated_test_started_rewrite.html",
            context={
                "request": request,
                "len": len,
                "name": name,
                "variant": informatics,
                "test_time": test_time,
                "max_question_number": max_question_number,
                "old_session": active_session.to_dict() if active_session else {},
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
            is_saved: bool = save_answer_for_session(
                session_id=request.session.get("old_test_session"),
                q_num=answer.q_num[2:],
                answer="$".join(answer.answer)
            )
            return True if is_saved else False

        print(answer.q_from_old_test, answer.answer)
        question: type[Informatics] = connect_database_informatics().session.get(Informatics, answer.q_from_old_test)
        q_number: int = int(question.q_number)
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
        return check_results[True] if not check_results[True] else check_results[True] + 1 if q_number < 26 else check_results[True]

    @app.post("/question_data")
    async def get_question_data(
            request: Request,
            for_question: ForQuestionData
    ):
        active_user_session = request.session.get("old_test_session")
        if active_user_session:
            active_session: type[ActiveStudentsTest] | None = connect_active_test_session().session.get(ActiveStudentsTest, active_user_session)
            question_id: Column[Integer] = active_session.test.split("&")[for_question.get_q_num() - 1]
            needed_question_data: type[Informatics] = connect_database_informatics().session.get(Informatics, question_id)
            needed_question_data.q_right_answer = len(needed_question_data.q_right_answer.split("&"))
            needed_question_data.answers = active_session.answers.split('&')[for_question.get_q_num() - 1]
            return needed_question_data
        return ""

    @app.post("/delete_old_test_session")
    async def remove_old_test_session(request: Request):
        # print(request.session)
        old_session_id = request.session.get("old_test_session")
        delete_old_test_session(session_id=old_session_id)
        request.session.pop("old_test_session")
        if request.session.get("stop_test"):
            request.session.pop("stop_test")
        if request.session.get("start_test"):
            request.session.pop("start_test")
        # print(request.session)


    @app.post("/test_results")
    def get_test_results(
            request: Request,
            test_data: TestResultData = Form(default="")
    ) -> _TemplateResponse:
        # print(test_data.to_dict())
        name: str = request.session.get("name")
        if not name:
            return RedirectResponse(url="/")
        active_user_session: type[ActiveStudentsTest] = connect_active_test_session().session.get(ActiveStudentsTest, request.session.get("old_test_session"))
        print(active_user_session.answers.split("&"))
        answers: dict[str, list[str]] = {
            q_num_ans_pair.split(":")[0]: q_num_ans_pair.split(":")[1].split("$")
            for q_num_ans_pair in active_user_session.answers.split("&")
        }
        # answers: dict[str, list[str]] = test_data.to_dict()
        variant: list[int] = list(map(int, active_user_session.test.split("&")))
        # variant: list[int] = list(map(int, request.session["informatics_variant"].split("&")))
        pprint(variant)
        results, mark, for_statistics = check_test_variant(
                    variant=variant,
                    answers=answers
        )
        update_statistics_to_student(
            user_id=request.session["user_id"],
            statistics=for_statistics
        )
        save_daily_statistics(
            user_id=request.session.get("user_id"),
            name=request.session.get("name"),
            checked_test=variant,
            answers_and_marks=results
        )
        delete_old_test_session(session_id=request.session.get("old_test_session"))
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
                "answers": results,
                "mark": mark,
                "nav_topic": "Результаты"
            }
        )


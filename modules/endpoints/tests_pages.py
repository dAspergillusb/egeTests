from itertools import count
from time import time
from typing import Type, Callable
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Query
from starlette.templating import _TemplateResponse
from sqlalchemy import Column, Integer
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..models.test_result_model import TestResultData
from ..models.test_type_model import TestVarOne, TestVarTwo, TestVarThree
from .config import TOPICS_FOR_PROBLEM_TYPES, INFORMATICS_DB_NAME
from ..functions.database_operations import (
    get_test_var_exam,
    get_test_var_one,
    get_test_var_two,
    get_test_var_three
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
        topics_problems_types: dict[int, str] = {
            num: topic for num, topic in enumerate(TOPICS_FOR_PROBLEM_TYPES, start=1)
        }
        # informatics: dict[Column[Integer], Type[Informatics]] = get_test_var()
        # request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
            name="/test_pages/choose_test_type.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
                "topics_problems_types": topics_problems_types,
                "nav_topic": "Выбор варианта генерации теста"
            }
        )

    @app.post("/test")
    def get_start_test_page(
            request: Request,
            data_for_test: TestVarOne | TestVarTwo | TestVarThree = Form(default=None)
    ) -> _TemplateResponse:
        # print(data_for_test.to_dict())
        name: str = request.session.get("name")
        school_class: str = request.session.get("school_class")
        what_type_of_test: dict[bool, Callable] = {
            isinstance(data_for_test, TestVarOne): get_test_var_one,
            isinstance(data_for_test, TestVarTwo): get_test_var_two,
            isinstance(data_for_test, TestVarThree): get_test_var_three,
        }

        informatics: dict[Column[Integer], type[Informatics]] = what_type_of_test[True](data_for_test.to_dict())
        request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
            name="/test_pages/generated_test.html",
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
        school_class: str = request.session.get("school_class")
        informatics: dict[Column[Integer], type[Informatics]] = get_test_var_exam()
        request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        return TEMPLATES.TemplateResponse(
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
        if not all((request.session.get("start_test"), request.session.get("stop_test"))):
            start_time: int = int(time())
            stop_time: int = start_time + get_time_of_test([int(question.q_number) for question in informatics.values()])
            request.session["start_test"] = start_time
            request.session["stop_test"] = stop_time
            test_time: int = request.session.get("stop_test") - request.session.get("start_test")
        else:
            test_time: int = request.session.get("stop_test") - int(time())

        return TEMPLATES.TemplateResponse(
            name="/test_pages/generated_test_started.html",
            context={
                "request": request,
                "len": len,
                "name": name,
                "variant": informatics,
                "test_time": test_time,
                "max_question_number": max_question_number,
                "str": str,
                "nav_topic": "Успешного решения теста"
            }
        )

    @app.post("/test_results")
    def get_test_results(
            request: Request,
            test_data: TestResultData = Form(default="")
    ) -> _TemplateResponse:
        print(test_data.to_dict())
        name: str = request.session.get("name")
        answers: dict[str, list[str]] = test_data.to_dict()
        answers, mark, for_statistics = check_test_variant(
                    variant=list(map(int, request.session["informatics_variant"].split("&"))),
                    answers=answers
        )
        update_statistics_to_student(
            user_id=request.session["user_id"],
            statistics=for_statistics
        )

        return TEMPLATES.TemplateResponse(
            name="/test_pages/testing_result.html",
            context={
                "request": request,
                "name": name,
                "answers": answers,
                "mark": mark,
                "nav_topic": "Результаты"
            }
        )


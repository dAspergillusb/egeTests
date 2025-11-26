from time import time
from typing import Annotated, Type
from fastapi import FastAPI, Request, Form, UploadFile
from sqlalchemy.orm import Query
from starlette.templating import _TemplateResponse
from sqlalchemy import Column, Integer
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..models .test_result_model import TestResultData
from ..functions.database_operations import get_test_var
from ..functions.database_operations import save_test_question, check_test_variant
from ..functions.files_operations import save_to_file
from .main_pages import TEMPLATES

def register_tests_pages(app: FastAPI) -> None:

    @app.get("/test")
    def get_start_test_page(request: Request) -> _TemplateResponse:
        name: str = request.session.get("name")
        school_class: str = request.session.get("school_class")
        informatics: dict[Column[Integer], Type[Informatics]] = get_test_var()
        request.session["informatics_variant"] = "&".join(f"{informatics[question].id}" for question in informatics)
        """print(informatics)
        print(request.session["informatics_variant"])
        print("im in tests page")"""
        return TEMPLATES.TemplateResponse(
            name="/test_pages/generated_test.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
                "variant": informatics.keys()
            }
        )

    @app.post("/test")
    def test_is_started(
            request: Request
    ) -> _TemplateResponse:
        name: str = request.session.get("name")
        school_class: str = request.session.get("school_class")

        database: Query[Type[Informatics]] = InformaticsDB().session.query(Informatics)
        informatics: dict[int, Type[Informatics]] = {
            database.get(_id).q_number: database.get(_id) for _id in map(int, request.session["informatics_variant"].split("&"))
        }
        max_question_number: int = max(informatics)
        if not all((request.session.get("start_test"), request.session.get("stop_test"))):
            start_time: int = int(time())
            stop_time: int = start_time + 6300  # It's 105 minutes for test (105 minutes * 60 seconds = 6300 seconds)
            request.session["start_test"] = start_time
            request.session["stop_test"] = stop_time
            test_time: int = request.session.get("stop_test") - request.session.get("start_test")
        else:
            test_time: int = request.session.get("stop_test") - int(time())

        return TEMPLATES.TemplateResponse(
            name="/test_pages/generated_test_started.html",
            context={
                "request": request,
                "name": name,
                "variant": informatics,
                "test_time": test_time,
                "max_question_number": max_question_number,
                "str": str
            }
        )

    @app.post("/test_results")
    def get_test_results(
            request: Request,
            test_data: TestResultData = Form(default="")
    ) -> _TemplateResponse:
        name: str = request.session.get("name")
        answers: dict[str, str] = test_data.to_dict()
        answers, mark = check_test_variant(
                    variant=list(map(int, request.session["informatics_variant"].split("&"))),
                    answers=answers
        )

        return TEMPLATES.TemplateResponse(
            name="/test_pages/testing_result.html",
            context={
                "request": request,
                "name": name,
                "answers": answers,
                "mark": mark
            }
        )


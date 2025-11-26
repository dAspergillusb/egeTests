from typing import Annotated
from fastapi import FastAPI, Request, Form, UploadFile
from starlette.templating import _TemplateResponse
from ..functions.database_operations import save_test_question
from ..functions.files_operations import save_to_file
from .main_pages import TEMPLATES

def register_tests_pages(app: FastAPI) -> None:

    @app.get("/test")
    def get_start_test_page(request: Request) -> _TemplateResponse:
        firstname: str = request.session.get("firstname")
        lastname: str = request.session.get("lastname")

    @app.post("/test")
    def test_is_started(request: Request, fistname: str, lastname: str) -> _TemplateResponse:
        pass
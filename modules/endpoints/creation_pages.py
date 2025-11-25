from typing import Annotated
from fastapi import APIRouter, FastAPI, Request, Form, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.templating import _TemplateResponse
from ..functions.database_operations import save_test_question
from ..functions.files_operations import save_to_file


ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_creation_pages(app: FastAPI) -> None:

    @app.get("/test_constructor")
    def test_constructor(request: Request, firstname: str, lastname: str) -> _TemplateResponse:
        request.session["firstname"] = firstname
        request.session["lastname"] = lastname
        return TEMPLATES.TemplateResponse(
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname
            }
        )

    @app.post("/test_constructor")
    def create_question(
            request: Request,
            q_number: Annotated[str, Form()],
            q_text: Annotated[str, Form()],
            file_one: UploadFile,
            file_two: UploadFile,
            file_three: UploadFile,
            file_four: UploadFile,
            q_right_answer: Annotated[str, Form()]
    ):
        files: list[UploadFile] = [file for file in [file_one, file_two, file_three, file_four] if file.filename]
        file_paths: list[str] = [
            save_to_file(
                q_number=q_number,
                file=file
            ) for file in files
        ]
        save_test_question(
            question_data={
                "q_number": q_number,
                "q_text": q_text,
                "q_school_class": "11Б",
                "q_files": "&".join(file_paths),
                "q_right_answer": q_right_answer
            }
        )

        return TEMPLATES.TemplateResponse(
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": request.session.get("firstname"),
                "lastname": request.session.get("lastname")
            }
        )


from typing import Annotated
from csv import DictReader, reader
from fastapi import FastAPI, Request, Form, UploadFile
from starlette.templating import _TemplateResponse
from ..models.test_creation_model import TestCreation, ImportCSV
from ..functions.database_operations import save_test_question
from ..functions.files_operations import save_to_file, create_new_dbs
from .main_pages import TEMPLATES

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
            data_for_create: TestCreation = Form(...),
    ) -> _TemplateResponse:
        # print(data_for_create)
        file_paths: list[str] = [
            save_to_file(
                q_number=data_for_create.get_q_number(),
                file=file
            ) for file in data_for_create.get_files()
        ]
        saved: bool = save_test_question(
            question_data={
                "q_number": data_for_create.get_q_number(),
                "q_text": data_for_create.get_q_text(),
                "q_difficulty": data_for_create.get_q_difficulty(),
                "q_school_class": "11",
                "q_files": "&".join(file_paths),
                "q_right_answer": data_for_create.get_answers()
            }
        )
        is_mistake: dict[bool, tuple[str, str]] = {
            saved: ("Успех!", "Вопрос успешно сохранён!"),
            not saved: ("Ошибка!", "Проверьте правильно ли заполнена форма.")
        }
        return TEMPLATES.TemplateResponse(
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": request.session.get("firstname"),
                "lastname": request.session.get("lastname"),
                "mistake_text": is_mistake[True]
            }
        )

    @app.get("/import_from_csv")
    def get_page_import_from_csv(request: Request) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            name="import_from_csv.html",
            context={
                "request": request,
                "mistake": "not",
            }
        )

    @app.post("/import_from_csv")
    def post_import_from_csv(
            request: Request,
            data_to_load: ImportCSV = Form(default=""),
    ) -> _TemplateResponse:
        # print(data_to_load)
        inf_db_name: str = data_to_load.inf_db_name
        u_db_name: str = data_to_load.u_db_name
        u_stat_db_name: str = data_to_load.u_stat_db_name
        csv_file: str = data_to_load.csv_file.file.read().decode("utf-8")
        print(csv_file)
        new_dbs: bool = create_new_dbs(
            csv_file=csv_file,
            u_db_name=u_db_name,
            u_stat_db_name=u_stat_db_name,
            inf_db_name=inf_db_name,
        )
        mistakes: dict[bool, str] = {
            new_dbs: "Базы данных успешно созданы",
            not new_dbs: "В csv-файле есть ошибки. База не создана!"
        }
        # print([item for item in reader(data_to_load.csv_file.file.read().decode("utf-8"), delimiter=";")])
        return TEMPLATES.TemplateResponse(
            name="import_from_csv.html",
            context={
                "request": request,
                "mistake": new_dbs,
                "mistake_text": mistakes[True]
            }
        )
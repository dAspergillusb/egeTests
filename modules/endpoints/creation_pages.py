from fastapi import FastAPI, Request, Form, UploadFile
from starlette.templating import _TemplateResponse
from ..models.test_creation_model import TestCreation, ImportCSV, TestCreation1921, DataFromTopic
from ..functions.database_operations import save_test_question, get_q_types_values
from ..functions.files_operations import save_to_file, create_new_dbs
from .main_pages import TEMPLATES

def register_creation_pages(app: FastAPI) -> None:

    @app.post("/data_from_topic")
    async def get_data_from_topic(
            request: Request,
            topic: DataFromTopic
    ):
        topic_number = topic.get_topic_number()
        match topic_number:
            case 1:
                return 1, get_q_types_values()
            case 2:
                return 2, 2
            case 3:
                return 3, 3
            case 4:
                return 4
        return 0

    @app.get("/test_constructor")
    def test_constructor(request: Request, firstname: str, lastname: str) -> _TemplateResponse:
        request.session["firstname"] = firstname
        request.session["lastname"] = lastname
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname,
                "q_number": "0",
                "q_difficulty": "0",
                "nav_topic": "Конструтор вопросов"
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
            request=request,
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": request.session.get("firstname"),
                "lastname": request.session.get("lastname"),
                "mistake_text": is_mistake[True],
                "q_number": data_for_create.get_q_number(),
                "q_difficulty": data_for_create.get_q_difficulty(),
                "nav_topic": "Конструтор вопросов"
            }
        )

    @app.get("/test_constructor_19-21")
    def test_constructor_19_21(request: Request, firstname: str, lastname: str) -> _TemplateResponse:
        request.session["firstname"] = firstname
        request.session["lastname"] = lastname
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname,
                "nineteen": True,
                "nav_topic": "Конструтор вопросов"
            }
        )

    @app.post("/test_constructor_19-21")
    def create_question_19_21(
            request: Request,
            firstname: str,
            lastname: str,
            data_for_create: TestCreation1921 = Form(...)
    ) -> _TemplateResponse:
        saved = {
            19: {
                "q_number": 19,
                "q_difficulty": data_for_create.q_difficulty,
                "q_school_class": "11",
                "q_text": data_for_create.q_text_19,
                "q_right_answer": data_for_create.q_right_answer_19
            },
            20: {
                "q_number": 20,
                "q_difficulty": data_for_create.q_difficulty,
                "q_school_class": "11",
                "q_text": data_for_create.q_text_20,
                "q_right_answer": "&".join([
                    data_for_create.q_right_answer_20_1,
                    data_for_create.q_right_answer_20_2
                ])
            },
            21: {
                "q_number": 21,
                "q_difficulty": data_for_create.q_difficulty,
                "q_school_class": "11",
                "q_text": data_for_create.q_text_21,
                "q_right_answer": data_for_create.q_right_answer_21
            }
        }
        save_test_question(question_data=saved)

        request.session["firstname"] = firstname
        request.session["lastname"] = lastname
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/test_pages/creation_question.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname,
                "nineteen": True,
                "nav_topic": "Конструтор вопросов"
            }
        )


    @app.get("/import_from_csv")
    def get_page_import_from_csv(request: Request) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="import_from_csv.html",
            context={
                "request": request,
                "mistake": "not",
                "nav_topic": "Создание базы данных"
            }
        )

    @app.get("/count_q_type_values")
    def get_page_count_q_type_values(request: Request) -> _TemplateResponse:
        count_q_type_values: dict[str, dict[str, int]] = get_q_types_values()
        return TEMPLATES.TemplateResponse(
            request=request,
            name="counting_q_type_values.html",
            context={
                "request": request,
                "count_q_type_values": count_q_type_values,
                "nav_topic": "Статистика по вопросам"
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
            request=request,
            name="import_from_csv.html",
            context={
                "request": request,
                "mistake": not new_dbs,
                "mistake_text": mistakes[True],
                "nav_topic": "Создание базы данных"
            }
        )

    @app.get("/to_html_tags")
    def get_page_to_html_tags(
            request: Request,
            firstname: str,
            lastname: str
    ) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="to_html_tags.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname,
                "nav_topic": "Получить ckeditor-данные из текста"
            }
        )

    @app.post("/to_html_tags")
    async def post_to_html_tags(request: Request, html_tags: str):
        print(html_tags)
        return {"html_tags": html_tags}
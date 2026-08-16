from typing import Callable, Optional
from fastapi import (
    FastAPI,
    Request,
    Form,
    UploadFile,
    HTTPException,
    Depends,
    Cookie
)
from sqlalchemy.orm import InstrumentedAttribute
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse
from .._types.Types import Ranks
from ..databases.InformaticsDB import Informatics, InformaticsDB
from ..models.test_creation_model import (
    TestCreation,
    ImportCSV,
    TestCreation1921,
    DataFromTopic,
    QuestionTypeNeeded,
    QuestionIdToChangeRemove
)
from ..functions.database_operations import (
    save_test_question,
    get_q_types_values,
    get_all_questions_for_type,
    get_sorted_statistics_for_students,
    change_test_question
)
from .config import TOPICS_FOR_TEACHER_CABINET, env_settings
from ..functions.files_operations import save_to_file
# from ..functions.database_operations import create_new_users
from ..functions.dependencies import Roles
from .main_pages import TEMPLATES

teacher_admin_allowed: Roles = Roles(allowed_roles=[Ranks.TEACHER, Ranks.ADMIN])

def register_creation_pages(app: FastAPI) -> None:

    @app.get("/teacher_cabinet")
    def get_teacher_cabinet(
            request: Request,
            rank: Optional[str] = Cookie(None),
            name: str = Depends(teacher_admin_allowed)
    ) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/teacher_cabinet.html",
            context={
                "request": request,
                "name": name,
                "rank": rank,
                "topics": enumerate(TOPICS_FOR_TEACHER_CABINET, start=1),
                "nav_topic": "Кабинет учителя"
            }
        )

    @app.post("/data_from_topic")
    async def get_data_from_topic(
            request: Request,
            topic: DataFromTopic,
            _=Depends(teacher_admin_allowed)
    ):
        topic_number: int = topic.get_topic_number()
        topics = {
            topic_number == 1: get_q_types_values,
            topic_number == 2: 2,
            topic_number == 3: 3,
            topic_number == 4: get_sorted_statistics_for_students,
        }
        return topic_number, topics[True] if isinstance(topics[True], int) else await topics[True]() #TODO

    @app.post("/get_all_q_types")
    async def get_all_type_questions(
            request: Request,
            q_type: QuestionTypeNeeded,
            _=Depends(teacher_admin_allowed)
    ):
        return await get_all_questions_for_type(q_type=q_type.q_type)

    @app.post("/test_constructor")
    async def create_question(
            request: Request,
            data_for_create: TestCreation = Form(...),
            _=Depends(teacher_admin_allowed)
    ) -> bool:
        file_paths: list[str] = [
            await save_to_file(
                q_number=data_for_create.get_q_number(),
                file=file
            ) for file in data_for_create.get_files()
        ]
        return await save_test_question(
            question_data={
                "q_number": data_for_create.get_q_number(),
                "q_text": data_for_create.get_q_text(),
                "q_difficulty": data_for_create.get_q_difficulty(),
                "q_school_class": "11",
                "q_files": "&".join(file_paths),
                "q_right_answer": data_for_create.get_answers()
            }
        )

    @app.post("/test_constructor_19-21")
    async def create_question_19_21(
            request: Request,
            data_for_create: TestCreation1921 = Form(...),
            _=Depends(teacher_admin_allowed)
    ) -> bool:
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
        return await save_test_question(question_data=saved)

    @app.post("/questions")
    async def get_question(
            request: Request,
            q_id: QuestionIdToChangeRemove,
            _=Depends(teacher_admin_allowed)
    ):
        question: type[Informatics] | None = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_question(q_id=q_id.get_q_id())
        if question:
            if question.q_number == 19:
                question_twenty_id, question_twenty_one_id = map(int, question.q_linked_with.split("&"))
                question_twenty: type[Informatics] | None = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_question(q_id=question_twenty_id)
                question_twenty_one: type[Informatics] | None = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).get_question(q_id=question_twenty_one_id)
                summary_from_questions: dict[str, list[str] | str | int | InstrumentedAttribute[int]] = {
                    "q_id": question.q_id,
                    "q_number": question.q_number,
                    "q_right_answer": [
                        question.q_right_answer.split("&"),
                        question_twenty.q_right_answer.split("&"),
                        question_twenty_one.q_right_answer.split("&")
                    ],
                    "q_difficulty": question.q_difficulty,
                    "q_text": [
                        question.q_text,
                        question_twenty.q_text,
                        question_twenty_one.q_text
                    ]
                }
                return summary_from_questions
            question.q_text = [question.q_text]
            question.q_right_answer = question.q_right_answer.split("&")
            return question
        return {}

    @app.post("/questions/{q_id}")
    async def change_question(
            request: Request,
            q_id: str,
            data_to_change: TestCreation | TestCreation1921 = Form(...),
            _=Depends(teacher_admin_allowed)
    ):
        # question: type[Informatics] | None = await InformaticsDB().get_question(q_id=q_id.get_q_id())
        # if question:
        result: list[type[Informatics] | None] = await change_test_question(
            q_id=int(q_id),
            data_to_change=data_to_change
        )
        if result:
            return result
        return 404

    @app.delete("/questions", status_code=204)
    async def remove_question(
            request: Request,
            q_id: QuestionIdToChangeRemove,
            _=Depends(teacher_admin_allowed)
    ):
        deleted: bool| HTTPException = await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).delete_question(q_id=q_id.get_q_id())
        result: dict[bool, int] = {
            deleted: 204,
            not deleted: 404
        }
        return result[True]


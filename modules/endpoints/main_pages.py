from collections import defaultdict
from typing import Annotated, Type
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column, String
from starlette.templating import _TemplateResponse
from .config import RANKS, TOPICS_FOR_TEACHER_CABINET, TOPICS_FOR_ADMIN_CABINET
from ..databases.InformaticsDB import Informatics
from ..databases.UsersDB import Users
from ..databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB
from ..functions.security import check_password
from ..functions.database_operations import get_daily_statistics, get_old_test


ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")
    app.mount("/files", StaticFiles(directory="files"), name="files")

    @app.get(path="/", response_model=None)
    def main_page(request: Request) -> _TemplateResponse | RedirectResponse:
        if request.session.get("name"):
            return RedirectResponse(url="/prepare_test")
        return TEMPLATES.TemplateResponse(
            request=request,
            name="sign_in.html",
            context={
                "request": request,
                "check_name_class": False
            }
        )

    @app.post(path="/", response_model=None)
    def main_page_login(
            request: Request,
            username: Annotated[str, Form()],
            password: Annotated[str, Form()]
    ) -> _TemplateResponse | RedirectResponse | str:
        from .config import USERS_IDS
        user: type[Users] | None = USERS_IDS.get(username)
        if_user_mistake: dict[bool, str | RedirectResponse] = {
            user and check_password(
                password=password,
                password_from_db=f"{user.password}"): RedirectResponse(RANKS.get(user.rank if user else None), status_code=302),
            not user: "Пользователь не найден",
            not check_password(
                password=password,
                password_from_db=f"{user.password if user else ''}"): "Неправильный пароль"
        }
        if isinstance(if_user_mistake.get(True), str):
            return TEMPLATES.TemplateResponse(
                request=request,
                name="sign_in.html",
                context={
                    "request": request,
                    "check_name_class": True,
                    "mistake_text": if_user_mistake[True]
                }
            )
        request.session["name"] = f"{user.firstname} {user.lastname}"
        request.session["school_class"] = user.school_class
        request.session["user_id"] = user.user_id
        return if_user_mistake[True]

    @app.get("/student_cabinet")
    def get_student_cabinet(request: Request) -> _TemplateResponse:
        name: str = request.session.get("name")
        if not name:
            return RedirectResponse(url="/")
        school_class: str = request.session.get("school_class")
        user_id: int = request.session.get("user_id")
        student_statistics: type[UsersStatistics] | None = UsersStatisticsDB().session.query(UsersStatistics).get(user_id)
        common_statistics: dict[str, float | str] = {
            "absolute_questions_value": 0.0,
            "absolute_right_answers_value": 0.0,
            "absolute_accuracy_persent": 0.0,
            "result": ""
        }
        # q_student_statistics: dict[str, Column[String]] = student_statistics.to_dict()
        common_values: list[float] = []
        right_answers_values: list[float] = []
        accuracy_persent_values: list[float] = []
        conclusions_for_results: list[str] = []
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

        daily_statistics: dict[str, defaultdict[str, list[type[Informatics]]]] = get_daily_statistics(user_id=request.session.get("user_id"))
        return TEMPLATES.TemplateResponse(
            request=request,
            name="student_cabinet.html",
            context={
                "request": request,
                "name": name,
                "school_class": school_class,
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

    @app.get("/teacher_cabinet")
    def get_teacher_cabinet(request: Request) -> _TemplateResponse:
        if not request.session.get("name"):
            return RedirectResponse("/")
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/teacher_cabinet.html",
            context={
                "request": request,
                "name": request.session.get("name"),
                "topics": enumerate(TOPICS_FOR_TEACHER_CABINET, start=1),
                "nav_topic": "Кабинет учителя"
            }
        )

    @app.get("/admin_cabinet")
    def get_admin_cabinet(request: Request) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/admin_cabinet.html",
            context={
                "request": request,
                "name": request.session.get("name"),
                "topics": enumerate(TOPICS_FOR_ADMIN_CABINET, start=1),
                "nav_topic": "Кабинет администратора"
            }
        )

    @app.post("/old_test/{date}/{time}")
    def get_old_test_page(request: Request, date: str, time: str) -> _TemplateResponse:
        date: str = "&".join((date, time))
        old_test, old_results = get_old_test(date=date)

        return TEMPLATES.TemplateResponse(
            request=request,
            name="test_pages/get_old_test.html",
            context={
                "request": request,
                "name": request.session.get("name"),
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

    @app.get("/logout")
    def logout(request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse("/")


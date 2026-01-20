from typing import Annotated, Type
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column, String
from starlette.templating import _TemplateResponse
from ..databases.InformaticsDB import InformaticsDB
from ..databases.UsersDB import Users
from ..databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB
from ..functions.security import check_password


ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")
    app.mount("/files", StaticFiles(directory="files"), name="files")

    @app.get(path="/", response_model=None)
    def main_page(request: Request) -> _TemplateResponse | RedirectResponse:
        if request.session.get("name"):
            return RedirectResponse(url="/test")
        return TEMPLATES.TemplateResponse(
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
    ) -> _TemplateResponse | RedirectResponse:
        from .config import USERS_IDS
        user: type[Users] | None = USERS_IDS.get(username)
        if_user_mistake: dict[bool, str | RedirectResponse] = {
            user and check_password(password=password, password_from_db=f"{user.password}"): RedirectResponse("/prepare_test", status_code=302),
            not user: "Пользователь не найден",
            not check_password(password=password, password_from_db=f"{user.password}"): "Неправильный пароль",

        }
        if isinstance(if_user_mistake.get(True), str):
            return TEMPLATES.TemplateResponse(
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
        school_class: str = request.session.get("school_class")
        user_id: int = request.session.get("user_id")
        student_statistics: UsersStatistics = UsersStatisticsDB().session.query(UsersStatistics).get(user_id)
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
                accuracy_persent >= 80: "Всё хорошо."
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
            number=common_statistics["absolute_right_answers_value"] * 100 / common_statistics["absolute_questions_value"],
            ndigits=3
        )
        absolute_conclusion_for_result: dict[bool, str] = {
            0 < common_statistics["absolute_accuracy_persent"] < 40: "Необходимо больше тренироваться!",
            40 <= common_statistics["absolute_accuracy_persent"] < 60: "Нужно побольше решать задания.",
            60 <= common_statistics["absolute_accuracy_persent"] < 80: "В целом нормально",
            common_statistics["absolute_accuracy_persent"] >= 80: "В целом хорошо."
        }
        common_statistics["result"] = absolute_conclusion_for_result.get(True, "Нет данных")
        return TEMPLATES.TemplateResponse(
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
                "len": len,
                "nav_topic": "Личный кабинет"
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


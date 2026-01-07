from typing import Annotated, Type
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column
from starlette.templating import _TemplateResponse
from ..databases.InformaticsDB import InformaticsDB
from ..databases.UsersDB import Users
from ..functions.database_operations import get_test_var
from ..functions.security import check_password
from .config import USERS_IDS


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
        user: type[Users] | None = USERS_IDS.get(username)
        if_user_mistake: dict[bool, str | RedirectResponse] = {
            user and check_password(password=password, password_from_db=f"{user.password}"): RedirectResponse("/test", status_code=302),
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
        request.session["name"] = user.firstname + user.lastname
        request.session["school_class"] = user.school_class
        return if_user_mistake[True]



    @app.get("/files/{problem_num}/{filename}")
    def get_file(problem_num: str, filename: str) -> FileResponse:
        path: str = f"/files/{problem_num}/{filename}"
        return FileResponse(path=path, filename=filename)

    @app.get("/logout")
    def logout(request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse("/")


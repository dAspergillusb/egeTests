from collections import defaultdict
from typing import Annotated
import traceback
from fastapi import APIRouter, FastAPI, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column, String
from starlette.templating import _TemplateResponse
from .config import TOPICS_FOR_TEACHER_CABINET
from ..databases.UsersDB import Users, UsersDB
from ..databases.UserSessionsDB import UserSessionsDB, UserSessions
from ..functions.security import check_password, create_access_token
from ..endpoints.config import SECURED, env_settings
from .._types.Types import Ranks

ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")
    app.mount("/files", StaticFiles(directory="files"), name="files")

    @app.get(path="/", response_model=None)
    def main_page(request: Request) -> _TemplateResponse | RedirectResponse:
        if request.session.get("rank"):
            return RedirectResponse(url=Ranks().redirect(request.session["rank"]), status_code=status.HTTP_302_FOUND)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="sign_in.html",
            context={
                "request": request,
                "check_name_class": False
            }
        )

    @app.post(path="/", response_model=None)
    async def main_page_login(
            request: Request,
            username: Annotated[str, Form()] = "",
            password: Annotated[str, Form()] = ""
    ) -> _TemplateResponse | RedirectResponse | str:

        try:
            user: type[Users] | None = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).choose_user(username=username)
        except Exception as error:
            return TEMPLATES.TemplateResponse(
                request=request,
                name="errors/fatal_error.html",
                context={
                    "traceBack": traceback.format_exc(),
                    "Error": str(error)
                }
            )
        if_user_mistake: dict[type[Users] | bool | None, str | RedirectResponse] = {
            user and check_password(
                password=password,
                password_from_db=f"{user.password}"): RedirectResponse(Ranks().redirect(user.rank if user else "guest"), status_code=status.HTTP_302_FOUND),
            not user: "Пользователь не найден",
            not check_password(
                password=password,
                password_from_db=f"{user.password if user else ''}"): "Неправильный пароль",
            user and not user.active: "Пользователь заблокирован. Обратитесь к администратору."
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
        session_id: str = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_new_session(
            user_id=user.user_id,
            user_agent=request.headers.get("User-Agent", ""),
            ip_address=request.client.host
        )
        access_token: str = create_access_token(
            data={
                "sub": username,
                "rank": user.rank,
                "session_id": session_id
            })
        _response: RedirectResponse = if_user_mistake[True]
        # request.session["name"] = f"{user.firstname} {user.lastname}"
        request.session["school_class"] = user.school_class
        _response.set_cookie(
            key="user_id",
            value=str(user.user_id),
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        # request.session["user_id"] = user.user_id
        # request.session["rank"] = user.rank
        _response.set_cookie(
            key="rank",
            value=user.rank,
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        _response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        if_user_mistake[True].set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        return if_user_mistake[True]

    @app.get("/logout")
    async def logout(request: Request) -> RedirectResponse:
        # user_id: int = int(request.cookies.get("user_id", 0))
        session_id: str = request.cookies.get("session_id", "")
        # active_session: type[UserSessions] | None = None
        # if user_id:
        #     active_session =  await UserSessionsDB().get_session(user_id=user_id)
        if session_id:
            await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).delete_session(session_id=session_id)
        redirect = RedirectResponse("/")
        redirect.delete_cookie(
            key="user_id",
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        redirect.delete_cookie(
            key="session_id",
            httponly=True,
            secure=SECURED,
            samesite="lax"
        )
        redirect.delete_cookie(
            key="access_token",
            httponly=True,
            secure=False,
            samesite="lax"
        )
        request.session.clear()
        return redirect

    @app.exception_handler(HTTPException)
    def http_exception(request: Request, exception: HTTPException) -> _TemplateResponse:
        print(exception)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/errors/user_error.html",
            context={
                "request":request,
                "Error": exception.detail
            }
        )
from typing import Annotated, Type
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column
from starlette.templating import _TemplateResponse
from ..databases.InformaticsDB import InformaticsDB
from ..functions.database_operations import get_test_var
from .config import ACCEPTED_NAMES, ACCEPTED_CLASSES


ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")

    @app.get(path="/")
    def main_page(request: Request) -> _TemplateResponse:

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
            name: Annotated[str, Form()],
            school_class: Annotated[str, Form()]
    ) -> _TemplateResponse | RedirectResponse:
        if name in ACCEPTED_NAMES and school_class in ACCEPTED_CLASSES:
            request.session["name"] = name
            request.session["school_class"] = school_class

            return RedirectResponse("/test", status_code=302)

        return TEMPLATES.TemplateResponse(
            name="sign_in.html",
            context={
                "request": request,
                "check_name_class": True
            }
        )

    @ROUTER.get("/files/download/{filename}", response_model=)
    def get_file(path: str, filename: str) -> FileResponse:
        return FileResponse(path=path, filename=filename)

    @app.get("/logout")
    def logout(request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse("/")


from typing import Annotated, Type
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Integer, Column
from starlette.templating import _TemplateResponse
from ..databases.InformaticsDB import InformaticsDB
from ..functions.database_operations import get_test_var


ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")

    @app.get(path="/")
    def main_page(request: Request) -> _TemplateResponse:
        #print(dict(request))
        request.get("")
        return TEMPLATES.TemplateResponse(
            name="sign_in.html",
            context={
                "request": request,
                "check_name_class": False
            }
        )

    @app.post(path="/")
    def main_page_login(
            request: Request,
            name: Annotated[str, Form()],
            school_class: Annotated[str, Form()]
    ) -> _TemplateResponse:
        try:
            firstname, lastname = name.split()
        except ValueError:
            pass
        if name and school_class:
            request.session["name"] = name
            request.session["school_class"] = school_class
            informatics: dict[Column[Integer], Type[InformaticsDB]] = get_test_var()
            print(informatics)
            return TEMPLATES.TemplateResponse(
                name="/test_pages/generated_test.html",
                context={
                    "request": request,
                    "test_var": informatics
                }
            )

        return TEMPLATES.TemplateResponse(
            name="sign_in.html",
            context={
                "request": request,
                "check_name_class": True
            }
        )


from fastapi import APIRouter, FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

ROUTER: APIRouter = APIRouter(prefix="/pages", tags=["Frontend"])
TEMPLATES: Jinja2Templates = Jinja2Templates(directory="modules/endpoints/templates")

def register_main_endpoints(app: FastAPI) -> None:
    app.mount("/static", StaticFiles(directory="modules/endpoints/static"), "static")


    @app.get(path="/")
    def main_page(request: Request):
        #print(dict(request))
        request.get("")
        return TEMPLATES.TemplateResponse(name="sign_in.html", context={"request": request})

    @app.post(path="/")
    def main_page_login(request: Request):
        print(request.session.get("name"))
        print(request.form())
        #print(dict(request))

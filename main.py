from secrets import token_urlsafe
from fastapi import FastAPI
from modules import register_main_endpoints, register_creation_pages, register_tests_pages
from starlette.middleware.sessions import SessionMiddleware

MAIN: FastAPI = FastAPI()

MAIN.add_middleware(
    SessionMiddleware,
    secret_key=token_urlsafe(64),
    session_cookie="my_cookies",
    max_age=14 * 24 * 60 * 60
)

register_main_endpoints(app=MAIN)
register_creation_pages(app=MAIN)
register_tests_pages(app=MAIN)

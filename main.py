from fastapi import FastAPI
from modules import register_main_endpoints
from starlette.middleware.sessions import SessionMiddleware

MAIN: FastAPI = FastAPI()

MAIN.add_middleware(
    SessionMiddleware,
    secret_key="getsecretkey",
    session_cookie="mycookie",
    max_age=14 * 24 * 60 * 60
)

register_main_endpoints(app=MAIN)


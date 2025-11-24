from fastapi import FastAPI
from modules import register_main_endpoints

MAIN: FastAPI = FastAPI()

register_main_endpoints(app=MAIN)


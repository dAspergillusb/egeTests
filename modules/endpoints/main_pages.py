from fastapi import FastAPI


def register_main_endpoints(app: FastAPI) -> None:

    @app.get(path="/")
    def main_page():
        return {"main": "page"}

# -*- coding: utf-8 -*-
import sys, os
sys.path.append("C:\\Users\\zelentsovna\\PycharmProjects\\site\\diagnostics")
sys.path.append("C:\\Users\\zelentsovna\\PycharmProjects\\site\\.venv\\Lib\\site-packages")
from a2wsgi import ASGIMiddleware
from main import MAIN as app
from werkzeug.debug import DebuggedApplication # Опционально: подключение модуля отладки

if __name__ == '__main__':
    APPLICATION = ASGIMiddleware(app)
    APPLICATION.
    # APPLICATION.wsgi_app = DebuggedApplication(APPLICATION.wsgi_app, True) # Опционально: включение модуля отадки
    # APPLICATION.debug = True  # Опционально: True/False устанавливается по необходимости в отладке
    # APPLICATION.run(
    #     debug=True,
    #     host="127.0.0.1",
    #     port=8000
    # )

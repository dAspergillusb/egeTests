import os
from os import getenv
from dotenv import load_dotenv, get_key
from typing import Optional
from ..models.env_model import EnvSettings
from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped


# loading DB parameters
env_settings: EnvSettings = EnvSettings()
DB_HOST: str = env_settings.DB_HOST
DB_PORT: str = env_settings.DB_PORT
DB_USER: str = env_settings.DB_USER
DB_PASSWORD: str = env_settings.DB_PASSWORD
DB_URL_PART: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
SECRET_KEY: str = env_settings.SECRET_KEY
ALGORITHM: str = env_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: str = env_settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Import db-names from file. What's db-name that we want to work.
# MAIN_DB_USERS_NAME = env_settings.MAIN_DB_USERS_NAME
# MAIN_DB_INFORMATICS_NAME = env_settings.MAIN_DB_INFORMATICS_NAME
# MAIN_DB_ARCHIVE_NAME = env_settings.MAIN_DB_ARCHIVE_NAME
ARCHIVE_DB_NAME = env_settings.ARCHIVE_DB_NAME
INFORMATICS_DB_NAME = env_settings.INFORMATICS_DB_NAME
USERS_DB_NAME = env_settings.USERS_DB_NAME
USERS_STATISTICS_DB_NAME = env_settings.USERS_STATISTICS_DB_NAME
DAILY_STATISTICS_DB_NAME = env_settings.DAILY_STATISTICS_DB_NAME
ACTIVE_STUDENTS_TEST_DB_NAME = env_settings.ACTIVE_STUDENTS_TEST_DB_NAME
INITIATED_DBS = env_settings.INITIATED_DBS

# in production or at server type this property on True
SECURED: bool = False

TOPICS_FOR_PROBLEM_TYPES: list[str] = [
    "1. Анализ информационных моделей",
    "2. Построение таблиц истинности логических выражений",
    "3. Поиск информации в реляционных базах данных",
    "4. Кодирование и декодирование информации",
    "5. Анализ и построение алгоритмов для исполнителей",
    "6. Определение результатов работы простейших алгоритмов",
    "7. Кодирование и декодирование информации. Передача информации",
    "8. Перебор слов и системы счисления",
    "9. Работа с таблицами",
    "10. Поиск символов в текстовом редакторе",
    "11. Вычисление количества информации",
    "12. Выполнение алгоритмов для исполнителей",
    "13. Организация компьютерных сетей. Адресация",
    "14. Кодирование чисел. Системы счисления",
    "15. Преобразование логических выражений",
    "16. Рекурсивные алгоритмы",
    "17. Обработки числовой последовательности",
    "18. Робот-сборщик монет",
    "19. Выигрышная стратегия. Задание 1",
    "20. Выигрышная стратегия. Задание 2",
    "21. Выигрышная стратегия. Задание 3",
    "22. Многопроцессорные системы",
    "23. Оператор присваивания и ветвления. Перебор вариантов, построение дерева",
    "24. Обработка символьных строк",
    "25. Обработка целочисленной информации",
    "26. Обработка целочисленной информации",
    "27. Программирование."
]

# Value of time in seconds to complete the problem type of EGE test
PROBLEM_TYPE_TO_TIME: dict[int, int] = {
    1: 180,
    2: 180,
    3: 180,
    4: 120,
    5: 240,
    6: 240,
    7: 300,
    8: 240,
    9: 360,
    10: 180,
    11: 180,
    12: 360,
    13: 180,
    14: 180,
    15: 180,
    16: 300,
    17: 840,
    18: 480,
    19: 360,
    20: 480,
    21: 660,
    22: 420,
    23: 480,
    24: 1080,
    25: 1200,
    26: 2100,
    27: 2400
}

# Translation the primary points to tests points
CORRECT_ANSWERS_VALUE_TO_POINTS: dict[int, int] = {
    0: 0,
    1: 7,
    2: 14,
    3: 20,
    4: 27,
    5: 34,
    6: 40,
    7: 43,
    8: 46,
    9: 48,
    10: 51,
    11: 54,
    12: 56,
    13: 59,
    14: 62,
    15: 64,
    16: 67,
    17: 70,
    18: 72,
    19: 75,
    20: 78,
    21: 80,
    22: 83,
    23: 85,
    24: 88,
    25: 90,
    26: 93,
    27: 95,
    28: 98,
    29: 100,
}

TOPICS_FOR_TEACHER_CABINET: list[str] = [
    "Общее количество вопросов",
    "Просмотр вопросов",
    "Создание вопросов",
    "Статистика учеников"
]

TOPICS_FOR_ADMIN_CABINET: list[str] = [
    "Управление пользователями",
    "Массовая работа с пользователями",
    "Работа с базами данных"
]

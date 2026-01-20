from sqlalchemy import Column, String
from ..databases.UsersDB import Users, UsersDB

# Import db-names from file. What in db we want to work.
INFORMATICS_DB_NAME: str = "informatics_db"
USERS_DB_NAME: str = "users_db"
USERS_STATISTICS_DB_NAME: str = "users_statistics_db"


def load_db_names() -> None:
    global INFORMATICS_DB_NAME, USERS_DB_NAME, USERS_STATISTICS_DB_NAME, USERS_IDS
    try:
        with open("db_names.txt", "r") as db_names:
            names: list[str] = db_names.readlines()
    except FileNotFoundError:
        with open("db_names.txt", "w") as db_names:
            db_names.write(
                "informatics_db\nusers_db\nusers_statistics_db"
            )
        with open("db_names.txt", "r") as db_names:
            names: list[str] = db_names.readlines()
    finally:
        INFORMATICS_DB_NAME = names[0].strip()
        USERS_DB_NAME = names[1].strip()
        USERS_STATISTICS_DB_NAME = names[2].strip()
        USERS_IDS = {
            f"{user.username}": user for user in UsersDB(db_name=USERS_DB_NAME).session.query(Users).all()
        }



load_db_names()

print(INFORMATICS_DB_NAME, USERS_DB_NAME, USERS_STATISTICS_DB_NAME)

RANKS: dict[str, str] = {
    "student": "student",
    "teacher": "teacher",
    "admin": "admin"
}


USERS_IDS: dict[str, type[Users]] = {
    f"{user.username}": user for user in UsersDB(db_name=USERS_DB_NAME).session.query(Users).all()
}

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

# Deprecated

# ACCEPTED_NAMES: set[str] = {
#     "Глаголева Ольга",
#     "Ольга Глаголева",
#     "Йувалыоглу Марьям",
#     "Марьям Йувалыоглу",
#     "Кислицин Максим",
#     "Максим Кислицин",
#     "Кузьменко Елизавета",
#     "Елизавета Кузьменко",
#     "Переслегин Даниил",
#     "Даниил Переслегин",
#     "Першин Эмиль",
#     "Эмиль Першин",
#     "Проничкин Андрей",
#     "Андрей Проничкин",
#     "Сорокин Ярослав",
#     "Ярослав Сорокин",
#     "Швецов Денис",
#     "Денис Швецов",
#     "Шокиров Ориф",
#     "Ориф Шокиров"
#     "Рачкин Дмитрий",
#     "Дмитрий Рачкин",
#     "Мунтян Алевтина",
#     "Алевтина Мунтян",
#     "Михайлов Николай",
#     "Николай Михайлов",
#     "Лукьянчиков Дмитрий",
#     "Дмитрий Лукьянчиков",
#     "Королева Екатерина",
#     "Екатерина Королева",
#     "Галочкина Анастасия",
#     "Анастасия Галочкина",
#     "Александр Виноградов",
#     "Виноградов Александр",
#     "Амбарцумян Арсений",
#     "Арсений Амбарцумян"
# }
#
# ACCEPTED_CLASSES: set[str] = {"11Б"}
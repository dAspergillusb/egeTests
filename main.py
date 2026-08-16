from asyncio import run
from aiofiles import open as async_open
from os.path import  exists
from secrets import token_urlsafe
from fastapi import FastAPI
from modules import (
    register_main_endpoints,
    register_creation_pages,
    register_tests_pages,
    register_admin_pages,
)
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from modules import (
    INITIATED_DBS,
    env_settings,
    MainDB,
    ArchiveDatabasesDB,
    ActiveStudentsTestDB,
    DailyStatisticsDB,
    InformaticsDB,
    Users,
    UsersDB,
    UsersStatisticsDB,
    UserSessionsDB,
    change_env_parameter,
    create_new_users,
    env_settings,
    HistoryTypes
)

MAIN: FastAPI = FastAPI()

async def init_dbs() -> None:
    await MainDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_main_db()
    await MainDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).create_main_db()
    await MainDB(db_name=env_settings.MAIN_DB_ARCHIVE_NAME).create_main_db()
    await ArchiveDatabasesDB(db_name=env_settings.MAIN_DB_ARCHIVE_NAME).init_db()
    await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await InformaticsDB(db_name=env_settings.MAIN_DB_INFORMATICS_NAME).init_db()
    await DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).init_db()
    await change_env_parameter("INITIATED_DBS")

async def create_users(csv_name: str = "database.csv") -> None:
    if exists(csv_name):
        async with async_open(f"{csv_name}", "r") as csv_file:
            await csv_file.readline()
            users_data: str = await csv_file.read()
    else:
        users_data = "Admin;;;;admin;admin;admin\n"
    await create_new_users(csv_file=users_data)

async def add_basic_history():
    history: ArchiveDatabasesDB = ArchiveDatabasesDB(db_name=env_settings.MAIN_DB_ARCHIVE_NAME)
    await history.add_history(
        history_type=HistoryTypes.INFORMATICS,
        history_data={
            "main_db_name": {"MAIN_DB_INFORMATICS_NAME": env_settings.MAIN_DB_INFORMATICS_NAME},
            "db_structure": {
                "INFORMATICS_DB_NAME": env_settings.INFORMATICS_DB_NAME
            }
        }
    )
    await history.add_history(
        history_type=HistoryTypes.USERS,
        history_data={
            "main_db_name": {"MAIN_DB_USERS_NAME": env_settings.MAIN_DB_USERS_NAME},
            "db_structure": {
                "USERS_DB_NAME": env_settings.USERS_DB_NAME,
                "USERS_STATISTICS_DB_NAME": env_settings.USERS_STATISTICS_DB_NAME,
                "DAILY_STATISTICS_DB_NAME": env_settings.DAILY_STATISTICS_DB_NAME,
                "ACTIVE_STUDENTS_TEST_DB_NAME": env_settings.ACTIVE_STUDENTS_TEST_DB_NAME
            }
        }
    )


MAIN.add_middleware(
    SessionMiddleware,
    secret_key=token_urlsafe(64),
    session_cookie="my_cookies",
    max_age=14 * 24 * 60 * 60
)

MAIN.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

register_admin_pages(app=MAIN)
register_main_endpoints(app=MAIN)
register_creation_pages(app=MAIN)
register_tests_pages(app=MAIN)

if not INITIATED_DBS:
    run(init_dbs())
    run(create_users())
    run(add_basic_history())

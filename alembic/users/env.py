from alembic.common import run_migrations
from modules.endpoints.config import DB_URL_PART, env_settings
from modules.databases.MainDB import BASE_USERS
from modules.databases import UsersDB, UsersStatisticsDB, UserSessionsDB, ActiveStudentsTest, DailyStatisticsDB  # noqa: F401

run_migrations(
    f"{DB_URL_PART}{env_settings.MAIN_DB_USERS_NAME}",
    BASE_USERS.metadata,
)

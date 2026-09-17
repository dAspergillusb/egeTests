from migration_utils import run_migrations
from modules.endpoints.config import DB_URL_PART, env_settings
from modules.databases.MainDB import BASE_USERS
import modules.databases.UsersDB  # noqa: F401
import modules.databases.UsersStatisticsDB  # noqa: F401
import modules.databases.UserSessionsDB  # noqa: F401
import modules.databases.ActiveStudentsTest  # noqa: F401
import modules.databases.DailyStatisticsDB  # noqa: F401

run_migrations(
    f"{DB_URL_PART}{env_settings.MAIN_DB_USERS_NAME}",
    BASE_USERS.metadata,
)
